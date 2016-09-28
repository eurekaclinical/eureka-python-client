from eurekaclinical import APISession, API, Struct, construct_api_session_context_manager

class Job(Struct):
    def __init__(self):
        super(Job, self).__init__()
        self.sourceConfigId = None
        self.destinationId = None
        self.dateRangePhenotypeKey = None
        self.earliestDate = None
        self.earliestDateSide = 'START'
        self.latestDate = None
        self.latestDateSide = 'START'
        self.updateData = False
        self.prompts = None
        self.propositionIds = []
        self.name = None
            
class Users(APIPart):
    def __init__(self, *args, **kwargs):
        super(Users, self).__init__('/users/', *args, **kwargs)

    def me(self):
        return self._get(self.rest_endpoint + "me")

class Phenotypes(APIPart):
    def __init__(self, *args, **kwargs):
        super(Phenotypes, self).__init__('/phenotypes/', *args, **kwargs)

class Concepts(APIPart):
    def __init__(self, *args, **kwargs):
        super(Concepts, self).__init__('/concepts/', *args, **kwargs)

    def get(self, key, summarize=False):
        return self._get(self.rest_endpoint + key + "?summarize=" + str(summarize))

class Jobs(APIPart):
    def __init__(self, *args, **kwargs):
        super(Jobs, self).__init__('/jobs/', *args, **kwargs)

    def submit(self, job):
        return self._post(self.rest_endpoint, job)
    
class EurekaSession(APISession):
    def __init__(self, cas_session,
                 api_url='https://localhost:8443/eureka-webapp', verify_api_cert=True):
        super(EurekaSession, self).__init__(cas_session, api_url=api_url, verify_api_cert=verify_api_cert)
        self.__api_args = (cas_session, verify_api_cert, api_url)

    @property
    def users(self):
        return Users(*self.__api_args)

    @property
    def phenotypes(self):
        return Phenotypes(*self.__api_args)

    @property
    def concepts(self):
        return Concepts(*self.__api_args)

    @property
    def jobs(self):
        return Jobs(*self.__api_args)

get_session = construct_api_session_context_manager(EurekaSession)

