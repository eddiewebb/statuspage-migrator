#! /usr/bin/env python
import requests

source_pages = ["gplkhyvn1nh2"]
target_page = "hk277w25hzw7"
api_key = "20a337bf86ccf339f4c4c25be8d4a47fd38aa2949c682e601260c1a1de23f237"
group_id_mappings = {}


from requests.auth import AuthBase

class ApiKeyAuth(AuthBase):
    """Attaches HTTP Pizza Authentication to the given Request object."""
    def __init__(self,api_key):
        # setup any auth-related data here
        self.api_key = api_key

    def __call__(self, r):
        # modify and return the request
        r.headers['Authorization'] = "OAuth " + self.api_key
        return r


# creates new dict intstead of list where index is the component ID
def dict_components_by_id(components):
	return dict((d['id'],dict(d,index=index)) for (index, d) in enumerate (components))

def replace_group_id(old_id):
	if old_id:
		return group_id_mappings[old_id]
	else:
		return ""

def get(url):
	return requests.get(url,auth=ApiKeyAuth(api_key))

def post(url,data):
	return requests.post(url,auth=ApiKeyAuth(api_key), data=data)


def getComponents(page_id):
	url = "https://api.statuspage.io/v1/pages/" + page_id + "/components.json"
	return get(url)

def postComponent(component):
	url = "https://api.statuspage.io/v1/pages/" + target_page + "/components.json"
	payload={
		'component[name]':component['name'],
		'component[description]':component['description'],
		'component[group_id]':replace_group_id(component['group_id'])
		}
	print "sending"
	print payload
	return post(url,payload)

def createComponent(component):
	print "Creating component: " + component['name'] +":" + component['id']
	response = postComponent(component)
	print response
	print response.text
	new_component = response.json()
	if 'id' in new_component:
		group_id_mappings[component['id']] = new_component['id']
		print group_id_mappings


#this method will act recursively to ensure highest level parent exists before creating child.
def createComponentTree(component_id, remainingComponents):
	if component_id in remainingComponents:
		component = remainingComponents[component_id]
		if component['group_id']:
			print "Component " + component['name'] + " has parent, build further up tree"
			createComponentTree(component['group_id'],remainingComponents)
		createComponent(component)
		del remainingComponents[component_id]
	else:
		print "Component " + component_id + " was previously created."


for page in source_pages:
	print "Migrating page " + page
	response = getComponents(page)
	createdComponents = []
	remainingComponents = dict_components_by_id(response.json())
	
	for component in response.json():
		createComponentTree(component['id'],remainingComponents)


