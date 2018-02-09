#! /usr/bin/env python

#
# In case you goofed migration, this **COMPLETELY PURGES*** all components on page
#



import requests




target_page = "pageID"
api_key = "API KEY"



from requests.auth import AuthBase

class ApiKeyAuth(AuthBase):
    """Attaches HTTP Authentication to the given Request object."""
    def __init__(self,api_key):
        # setup any auth-related data here
        self.api_key = api_key

    def __call__(self, r):
        # modify and return the request
        r.headers['Authorization'] = "OAuth " + self.api_key
        return r

def get(url):
	return requests.get(url,auth=ApiKeyAuth(api_key))



def getComponents():
	url = "https://api.statuspage.io/v1/pages/" + target_page + "/components.json"
	return get(url)

def deleteComponent(component):
	url = "https://api.statuspage.io/v1/pages/" + target_page + "/components/" + component['id'] + ".json"
	return requests.delete(url,auth=ApiKeyAuth(api_key))



response = getComponents()

for component in response.json():
	print "Deleteing: " + component['name']
	response = deleteComponent(component)
	print response.text
