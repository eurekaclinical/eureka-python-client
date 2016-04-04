# eureka-python-client
Clients for accessing Eureka!'s web services APIs

## Requirements
* Requires Python 2.7.10 or higher and the requests module (can be
  installed using pip)

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

