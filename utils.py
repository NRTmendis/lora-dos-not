# Module containing all methods required by other Python files
# Author: Ayush Singh
"""Created by Ayush Singh 18/03/2018"""

import json


def get_current_model(settings_file='../settings.json'):
    return json.loads(open(settings_file).read())['current_model']


def get_current_world(settings_file='../settings.json'):
    return json.loads(open(settings_file).read())['current_world']


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
