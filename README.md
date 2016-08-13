# Eureka! Clinical Python Client
A client library for accessing Eureka! Clinical's web services APIs. It is in early development.

## Requirements
* Python 2.7.10 or higher. Installation instructions for CentOS 6 are available at http://toomuchdata.com/2014/02/16/how-to-install-python-on-centos/. We use virtualenv as described on that page.
* The requests module (can be installed using `sudo pip install requests`) version >= 2.11.0.

## Installation
On the command line, execute `python setup.py install`.

## Example
If you run eureka on your local machine using `mvn tomcat7:run`, you can access the REST APIs from python as follows:
```
from eurekaclinical.eureka import client

with client.connect('username', 'password', verify_cas_cert=False, verify_api_cert=False) as cn:
  print cn.users().me()
  print cn.concepts().get('ICD9:250.00')
  print cn.phenotypes().get('30-day readmission')
```

## Limitations
Only local user accounts can login using this client.

