# eureka-python-client
Clients for accessing Eureka!'s web services APIs

## Example
If you run eureka on your local machine using `mvn tomcat7:run`, you can access the REST APIs as follows:
```
from eurekaclinical.eureka import client

with client.connect('username', 'password', verify_cas_cert=False, verify_api_cert=False) as cn:
  print cn.users().me()
  print cn.concepts().get('ICD9:250.00')
```
