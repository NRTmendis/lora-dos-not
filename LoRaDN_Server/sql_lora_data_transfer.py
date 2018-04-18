""" Created by Nissanka Mendis on 18/03/2018"""
# SQL database data handler

import json
import sqlite3
import base64
import sys
sys.path.insert(1, '..')
from utils import get_current_world, get_gateways

Lora_GTW_DB = "lora_GTW.db"

# SETTINGS CONSTANTS
CURRENT_WORLD = get_current_world()

# Gateway Locations (Change according to preset location)
#		[Gateway ID,	Lattitude, Longitude]
Gw_Loc_db = get_gateways(CURRENT_WORLD, lists=True)


# Database Manager Class
class DatabaseManager():
    def __init__(self):
        self.conn = sqlite3.connect(Lora_GTW_DB)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()

    def add_del_update_db_record(self, sql_query, args=()):
        self.cur.execute(sql_query, args)
        self.conn.commit()
        return

    def __del__(self):
        self.cur.close()
        self.conn.close()


def Gateway_Location(jsonData):
    try:
        json_Dict = json.loads(jsonData)
        gw_id = str(json_Dict['gtiD'])
        for x in range(0, len(Gw_Loc_db)):
            if Gw_Loc_db[x][0] == gw_id:
                return (str(Gw_Loc_db[x][1]), str(Gw_Loc_db[x][2]))
        return ("", "")
    except:
        return ("", "")


def Lora_Gateway_PKT_Data_handler(jsonData):
    # Parse Data
    json_Dict = json.loads(jsonData)
    gateway_id = json_Dict['gtiD']
    pkt_date_and_time = json_Dict['time']
    pkt_rssi = json_Dict['rssi']
    pkt_snr = json_Dict['lsnr']
    pkt_size = json_Dict['size']
    gw_loc = ("", "")
    try:
        dec_data = json_Dict['data']
        pkt_data = base64.b64decode(dec_data)
        gw_loc = Gateway_Location(pkt_data)
    except:
        print("Error decoding data in PKT")
        return
    # Set GW locations if PKT=Gateway PKT
    pkt_latitude = gw_loc[0]
    pkt_longitude = gw_loc[1]

    # Push to DB
    dbObj = DatabaseManager()
    dbObj.add_del_update_db_record("insert into Lora_Gateway_PKT_Data (gateway_id, pkt_date_and_time, pkt_rssi, pkt_snr, pkt_data, pkt_size, pkt_latitude, pkt_longitude) values (?,?,?,?,?,?,?,?)", [
                                   gateway_id, pkt_date_and_time, pkt_rssi, pkt_snr, pkt_data, pkt_size, pkt_latitude, pkt_longitude])
    del dbObj


def Lora_Gateway_Send_Data(jsonData):
    # Parse Data
    json_Dict = json.loads(jsonData)
    snd_recp = json_Dict['recp']
    snd_date_and_time = json_Dict['time']
    snd_data = json_Dict['data']

    # Push to DB
    dbObj = DatabaseManager()
    dbObj.add_del_update_db_record("insert into Lora_Gateway_Send_Data (snd_recp, snd_date_and_time, snd_data) values (?,?,?)", [
                                   snd_recp, snd_date_and_time, snd_data])
    del dbObj

# Select function to select DB function based on MQTT topic


def lora_Data_Handler(Topic, jsonData):
    try:
        if Topic == "UCL4thYearLORA/NodeDATA":
            Lora_Gateway_PKT_Data_handler(jsonData)
        elif Topic == "UCL4thYearLORA/gatewayUpdateDATA":
            Lora_Gateway_Send_Data(jsonData)
    except:
        print("Error parsing PKT to database")
