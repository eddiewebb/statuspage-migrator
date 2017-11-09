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

def postComponent(payload):
	url = "https://api.statuspage.io/v1/pages/" + target_page + "/components.json"
	print "sending"
	print payload
	return post(url,payload)

def createComponent(component,allComponents):
	print "Creating component: " + component['name'] +":" + component['id']
	payload={
		'component[name]':component['name'],
		'component[description]':component['description']
		}
	if component['group_id']:
		if group_id_mappings[component['group_id']]:
			print "\tAdding previously created parent ID " + group_id_mappings[component['group_id']]
			payload['component[group_id]'] = group_id_mappings[component['group_id']]
		else:
			print "\tAdding new parent name: " + allComponents[component['group_id']]['name']
			payload['component[group_name]'] = allComponents[component['group_id']]['name']
	else:
		# becuase it has no parent, it could be a parent
		if component['id'] in group_id_mappings:
			print "\tSkipping parent: " + component['name']
			return
	response = postComponent(payload)
	new_component = response.json()
	if 'group_id' in new_component:
		group_id_mappings[component['group_id']] = new_component['group_id']




for page in source_pages:
	print "Migrating page " + page
	response = getComponents(page)
	allComponentsById = dict_components_by_id(response.json())



	for component in response.json():
		if component['group_id']:
			if component['group_id'] not in group_id_mappings:
				print "marking component ID: " + component['group_id'] + " as a parent"
				group_id_mappings[component['group_id']]=""

	for component in response.json():
		createComponent(component,allComponentsById)


