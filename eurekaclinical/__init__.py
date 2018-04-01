import json, requests
from contextlib import contextmanager

class Struct(object):
    def __init__(self, data=None):
        super(Struct, self).__init__()
        if data is not None:
            for name, value in data.iteritems():
                setattr(self, name, self.__wrap(value))

    def to_json(self):
        def json_dumps_default(o):
            return {key: \
                    json_dumps_default(value) if hasattr(value, '__dict__') else value \
                    for key, value in o.__dict__.iteritems()}
        return json.dumps(self, default=json_dumps_default)

    def __wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)): 
            return type(value)([self.__wrap(v) for v in value])
        else:
            return Struct(value) if isinstance(value, dict) else value

class CASServer(object):
    def __init__(self, session, cas_url, verify_cert=True):
        self.__cas_url = cas_url
        self.__ticket_url = cas_url + '/v1/tickets/'
        self.__verify_cert = verify_cert
        self.__session = session
    
    def login(self, username, password):
        params = {'username': username, 'password': password}
        result = self.__session.post(self.__ticket_url,
                                     data=params,
                                     verify=self.__verify_cert)
        result.raise_for_status()
        location = result.headers['Location']
        self.__tgt = location[location.rfind('/') + 1:]

    def get_service_ticket(self, service):
        params = {'service': service}
        result = self.__session.post(self.__ticket_url + self.__tgt,
                                     data=params,
                                     verify=self.__verify_cert)
        result.raise_for_status()
        return result.text

    def logout(self):
        self.__session.delete(self.__ticket_url + self.__tgt, verify=self.__verify_cert)

class CASSession(object):
    def __init__(self, username, password,
                 cas_url='https://localhost:8000/cas-server', verify_cas_cert=True,
                 timeout=60, max_retries=3):
        self.__verify_cas_cert = verify_cas_cert
        self.__session = _RetrySessionProxy(requests.Session(), timeout=timeout)
        self.__session.mount('https://', requests.adapters.HTTPAdapter(max_retries=max_retries))
        self.__cas = CASServer(self.__session, cas_url, verify_cas_cert)
        self.__cas.login(username, password)

    @contextmanager
    def analytics(self, *args, **kwargs):
        session = None
        try:
            session = analyticsclient.AnalyticsSession(self, *args, **kwargs)
            yield session
        finally:
            try:
                close_it = session.close
            except AttributeError:
                pass
            else:
                close_it()
        
    def _get(self, *args, **kwargs):
        return self.__session.get(*args, **kwargs)

    def _post(self, *args, **kwargs):
        return self.__session.post(*args, **kwargs)

    def _get_service_ticket(self, service_url):
        return self.__cas.get_service_ticket(service_url)
    
    def close(self):
        self.__cas.logout()

    

class APISession(object):
    def __init__(self, cas_session, api_url=None, verify_api_cert=True):
        self.__cas_session = cas_session
        self.__api_url = api_url
        self.__verify_api_cert = verify_api_cert
        self.__get_session_path = '/protected/get-session'
        self.__cas_session._get(self.__api_url + \
                                self.__get_session_path + '?ticket=' + \
                                self.__cas_session._get_service_ticket(self.__api_url + self.__get_session_path),
                                verify=self.__verify_api_cert)

    def close(self):
        self.__cas_session._get(self.__api_url + '/destroy-session', verify=self.__verify_api_cert)
        
class API(object):
    def __init__(self, rest_endpoint, session, verify_cert, url):
        self.__verify_cert = verify_cert
        self.__api_url = url
        self.rest_endpoint = rest_endpoint
        self.__session = session

    def get(self, id):
        return self._get(self.rest_endpoint + str(id))

    def all(self):
        return self._get(self.rest_endpoint)
    
    def _get(self, rest_endpoint):
        url = self.__api_url +  '/proxy-resource' + rest_endpoint
        result = self.__session._get(url,
                                     verify=self.__verify_cert)
        result.raise_for_status()
        return self._loads(result)
    
    def _post(self, rest_endpoint, o):
        url = self.__api_url + '/proxy-resource' + rest_endpoint
        result = self.__session._post(url,
                                      data=o.to_json(),
                                      verify=self.__verify_cert,
                                      headers={'content-type': 'application/json'})
        result.raise_for_status()
        location = result.headers['Location']
        return long(location[location.rfind('/') + 1:])

    @staticmethod
    def _loads(result):
        return json.loads(result.text, object_hook=lambda d: Struct(d))
        
@contextmanager
def connect(*args, **kwargs):
    eureka = None
    try:
        eureka = CASSession(*args, **kwargs)
        yield eureka
    finally:
        try:
            close_it = eureka.close
        except AttributeError:
            pass
        else:
            close_it()

def construct_api_session_context_manager(api_session_clz):
    @contextmanager
    def get_session(*args, **kwargs):
        api_session = None
        try:
            api_session = api_session_clz(*args, **kwargs)
            yield api_session
        finally:
            try:
                close_it = api_session.close
            except AttributeError:
                pass
            else:
                close_it()
    return get_session
            
class _Delegate(object):
    '''Delegate base class. Instances of this class will have all of the same
    methods and fields as the object provided in the constructor except for
    special methods.'''
    
    def __init__(self, obj):
        '''Constructs a delegate of the provided object. The object is
        available to subclasses as self._obj.'''
        self._obj = obj

    def __getattr__(self, *args, **kwargs):
        return getattr(self._obj, *args, **kwargs)
            
class _RetrySessionProxy(_Delegate):
    '''Proxies the request module's Session class. It provides the same
    methods as the request module's session class. For the get, post etc.
    methods, it optionally sets the timeout specified in the constructor.'''
    
    def __init__(self, session, timeout=None):
        '''Constructs a proxy of the provided Session object. Optional
        timeout argument is in seconds.'''
        super(_RetrySessionProxy, self).__init__(session)
        self.__timeout = timeout

    def get(self, *args, **kwargs):
        '''Same as session.get, except the timeout keyword argument is already
        set.'''
        return self.__request(self._obj.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        '''Same as session.post, except the timeout keyword argument is
        already set.'''
        return self.__request(self._obj.post, *args, **kwargs)

    def __request(self, method, *args, **kwargs):
        '''Calls the specified method with the specified arguments, and
        adds the timeout keyword argument.
        '''
        return method(*args, timeout=self.__timeout, **kwargs)

from analytics import client as analyticsclient
