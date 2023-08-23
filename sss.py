import requests

apikey = 'plv7ln2583k25eg32fgub3bdp5'
target_url = "http://localhost:8090/bodgeit"
# Include  target URL in Context
includeincontexturl = f'http://localhost:8080/JSON/context/action/includeInContext/?apikey={apikey}&regex={target_url}' 
includecontextresponse = requests.get(includeincontexturl)
# Set Authentication method 
context_id = 1 
authmethod = "formBasedAuthentication"
credential = "username={%username%}&password={%password%}"
Configpara = f'loginUrl=http://localhost:8090/bodgeit/login.jsp&loginRequestData={credential}'
setauthmethodurl = f'http://localhost:8080/JSON/authentication/action/setAuthenticationMethod/?apikey={apikey}&contextId={context_id}&authMethodName={authmethod}&authMethodConfigParams={Configpara}'
setauthmethodresponse = requests.get(setauthmethodurl)