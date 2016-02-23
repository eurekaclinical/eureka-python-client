# eureka-python-client
Clients for accessing Eureka!'s web services APIs

## Example
```
from eurekaclinical.eureka import client

# Assumes eureka-webapp and cas are running on localhost
with client.connect('username', 'password') as cn:
  print cn.users().me()
  print cn.concepts().get('ICD9:250.00')
```
