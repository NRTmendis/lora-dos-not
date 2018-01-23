# Author Nissanka Mendis
# SQL database data handler

import json
import sqlite3

Lora_GTW_DB = "lora_GTW.db"

#Database Manager Class
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
	
def Lora_Gateway_PKT_Data_handler(jsonData):
	#Parse Data
	json_Dict = json.loads(jsonData)
	gateway_id = json_Dict['gtiD']
	pkt_date_and_time = json_Dict['time']
	pkt_rssi = json_Dict['rssi']
	pkt_snr = json_Dict['lsnr']
	pkt_size = json_Dict['size']
	try:
		dec_data = json_Dict['data']
		pkt_data = dec_data.decode("base64")
	except: 
		print("Error decoding data in PKT")
		return

	#Push to DB
	dbObj = DatabaseManager()
	dbObj.add_del_update_db_record("insert into Lora_Gateway_PKT_Data (gateway_id, pkt_date_and_time, pkt_rssi, pkt_snr, pkt_data, pkt_size) values (?,?,?,?,?,?)",[gateway_id, pkt_date_and_time, pkt_rssi, pkt_snr, pkt_data, pkt_size])
	del dbObj

def Lora_Gateway_Send_Data(jsonData):
	#Parse Data
	json_Dict = json.loads(jsonData)
	snd_recp = json_Dict['recp']
	snd_date_and_time = json_Dict['time']
	snd_data = json_Dict['data']

	#Push to DB
	dbObj = DatabaseManager()
	dbObj.add_del_update_db_record("insert into Lora_Gateway_Send_Data (snd_recp, snd_date_and_time, snd_data) values (?,?,?)",[snd_recp, snd_date_and_time, snd_data])
	del dbObj

#Select function to select DB function based on MQTT topic

def lora_Data_Handler(Topic, jsonData):
	try:
		if Topic == "UCL4thYearLORA/NodeDATA":
			Lora_Gateway_PKT_Data_handler(jsonData)
		elif Topic == "UCL4thYearLORA/gatewayUpdateDATA":
			Lora_Gateway_Send_Data(jsonData)
	except:
		print("Error parsing PKT to database")