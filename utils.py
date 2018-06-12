# Module containing all methods required by other Python files
# Author: Ayush Singh

import json

settings_json = {
    'current_world': '',
    'current_model': ''
}

def get_current_model(settings_file='../settings.json'):
    return json.loads(open(settings_file).read())['current_model']
	
def get_current_world(settings_file='../settings.json'):
    return json.loads(open(settings_file).read())['current_world']
	
def set_current_model(new_model_name, settings_file='../settings.json'):
	settings_json["current_world"] = json.loads(open(settings_file).read())['current_world']
	settings_json["current_model"] = str(new_model_name)
	with open(settings_file,'w') as outfile:
		json.dump(settings_json, outfile)


def get_world(world_code, worlds_file='../worlds.json'):
    return json.loads(open(worlds_file).read())[world_code]


def listify(gateways_dict):
    return [
        [str(gateway), data['lat'], data['lng']]
        for gateway, data in gateways_dict.items()
    ]


def get_gateways(world_code, lists=False):
    if lists:
        return listify(get_world(world_code)['gateways'])
    else:
        return get_world(world_code)['gateways']

