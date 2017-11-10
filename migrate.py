#! /usr/bin/env python
import requests
import time

source_pages = ["gplkhyvn1nh2","vfdq0lwd1hk7","46qjhlfcz2w3","mxyt2m7f2kvz"]
target_page = "hk277w25hzw7"
api_key = "Your API Key Here"














parent_ids = []
id_mappings = {}
subscriber_by_key = {}

from requests.auth import AuthBase

class ApiKeyAuth(AuthBase):
    """Attaches HTTP Pizza Authentication to the given Request object."""
    def __init__(self,api_key):
        # setup any auth-related data here
        self.api_key = api_key

    def __call__(self, r):
        # modify and return the request
        r.headers['Authorization'] = "OAuth " + self.api_key
        time.sleep(1.1) #hack ensures we dont exceed rate limit for our token
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
	return post(url,payload)


def getSubscriptions(page_id):
	url = "https://api.statuspage.io/v1/pages/" + page_id + "/subscribers.json"
	return get(url)

def postSubscriber(payload):
	url = "https://api.statuspage.io/v1/pages/" + target_page + "/subscribers.json"
	return post(url,payload)

def createComponent(component,allComponents):
	print "Creating component: " + component['name'] +":" + component['id']
	payload={
		'component[name]':component['name'],
		'component[description]':component['description']
		}
	if component['group_id']:
		if component['group_id'] in id_mappings:
			print "\tRelating to previously created parent ID " + id_mappings[component['group_id']]
			payload['component[group_id]'] = id_mappings[component['group_id']]
		else:
			print "\tAdding new parent name: " + allComponents[component['group_id']]['name']
			payload['component[group_name]'] = allComponents[component['group_id']]['name']
			#payload['component[group_description]'] = allComponents[component['group_id']]['description']
	else:
		# becuase it has no parent, it could be a parent
		if component['id'] in parent_ids:
			print "\tSkipping parent: " + component['name']
			return
	response = postComponent(payload)
	print "\t" + str(response.status_code)
	if response.status_code != 201:
		print response.text
	new_component = response.json()
	id_mappings[component['id']] = new_component['id']
	if 'group_id' in new_component:
		id_mappings[component['group_id']] = new_component['group_id']

def createSubscriber(subscriber_key):
	subscriber = subscriber_by_key[subscriber_key]
	#note this leave user inactive, and you'll need to manually or use /subscribers/reactivate to enable them
	payload=[]
	payload.append(('subscriber[skip_confirmation_notification]','true'))
	if 'phone_number' in subscriber:
		payload.append(('subscriber[phone_number]',subscriber['phone_number']))
		payload.append(('subscriber[phone_country]',subscriber['phone_country']))
	else:
		payload.append(('subscriber[email]',subscriber['email']))
	for old_component_id in subscriber['components']:
		payload.append(('subscriber[component_ids][]',id_mappings[old_component_id]))
	print payload
	response = postSubscriber(payload)
	print response.request.body
	print "\t" + str(response.status_code)
	if response.status_code != 201:
		print response.text


def addOrMergeSubscriber(subscriber,allPageComponentsById):
	print "\tcapturing subscriber details: " + subscriber['id']
	key=""
	if 'phone_number' in subscriber:
		key=subscriber['phone_number']
	else:
		key=subscriber['email']
	if 'components' not in subscriber:
		print "\t WARN: grandfathered subscriber with empty components, will subscribe to all components for this page."
		subscriber['components'] = allPageComponentsById.keys()
	if key in subscriber_by_key:
		target_subscriber = subscriber_by_key[key]
		subscriber['components'] = subscriber['components']  + target_subscriber['components']
	subscriber_by_key[key] = subscriber


#test subscriber function
#id_mappings["1"]="gv1xlvgs35n3"
#id_mappings["2"]="lrqbdgkvzflw"
#
#subscriber = {'email':'edward.webb@libertymutual.com','components':["1","2"]}
#subscriber_by_key["1"]=subscriber
#createSubscriber("1")
#exit()


for page in source_pages:
	print "\nMigrating page " + page

	response = getComponents(page)
	allComponentsById = dict_components_by_id(response.json())
	for component in response.json():
		if component['group_id']:
			if component['group_id'] not in parent_ids:
				print "marking component ID: " + component['group_id'] + " as a parent"
				parent_ids.append(component['group_id'])
	for component in response.json():
		createComponent(component,allComponentsById)

	response = getSubscriptions(page)
	for subscriber in response.json():
		addOrMergeSubscriber(subscriber,allComponentsById)


for subscriber_key in subscriber_by_key:
	print "Adding subscriber: " + subscriber_by_key[subscriber_key]['id'];
	createSubscriber(subscriber_key)



