#Author Nissanka Mendis
#SQL DB data to Machine Learning CSV format parser
#Nissanka Mendis 2018 Feb. 

import sqlite3
import csv
import json
from ML_localisation import train_localisation_model
from ML_localisation import loc_single_predict
import sched
import time

#SQlite DB name
Lora_GTW_DB = "lora_GTW.db"

#GTW training CSV Out name
Lora_GTW_PP = "lora_GTW_PP.csv"

#PKT query CSV Out name
Lora_NODE_PP = "Lora_NODE_PP.csv"

Gw_Loc_db = [
		["240AC4F01E023C54",6.738,12.291],
		["240AC4F01E0286DC",7.34,0.555],
		["240AC4F01E025FF4",0.363,11.976],
		["240AC4F01E023E3C",0.733,0.531]
	    ]
		
def Gateway_Check(jsonData):
	try:
		json_Dict = json.loads(jsonData)
		gw_id = str(json_Dict['gtiD'])
		for x in range(0, len(Gw_Loc_db)):
			if Gw_Loc_db[x][0] == gw_id:
				return (gw_id)
		return ("Not Found")	#Not a gateway id
	except:
		return ("Not Found")	#Not a gateway packet
		
def create_CSV(csvfile, DATA_to_CSV):
	try:
		max_GW = len(DATA_to_CSV[0])-3 #3 rows are not gateway rssi
	except:
		return
	CSV_header = ["iD"]
	for x in range(0, max_GW):
		CSV_header.append("GW_RSSI_"+str(x+1))
	CSV_header.append("GW_Long")
	CSV_header.append("GW_Lat")
	#Write to CSV
	with open(csvfile,'w', newline='') as out_csv_file:
		csv_out = csv.writer(out_csv_file)
		csv_out.writerow(CSV_header)
		csv_out.writerows(DATA_to_CSV)
	
def new_cell_for_ML(db_ids):
	#Re-connect to server
	conn = sqlite3.connect(Lora_GTW_DB)
	curs = conn.cursor()
	#Set all Gateway RSSI to -150dB, noise floor level
	
	Gw_RSSI = [-150]
	for x in range(1, len(Gw_Loc_db)):
		Gw_RSSI.append(-150)
	#Get the PKTs Longitude and Lattitude
	curs.execute('SELECT pkt_longitude FROM Lora_Gateway_PKT_Data WHERE id ='+ str(db_ids[0]))
	pkt_long = curs.fetchone()[0]
	if (pkt_long is None) or (pkt_long == ""):
		pkt_long = 0
		
	curs.execute('SELECT pkt_latitude FROM Lora_Gateway_PKT_Data WHERE id ='+ str(db_ids[0]))
	pkt_lat = curs.fetchone()[0]
	if (pkt_lat is None) or (pkt_lat == ""):
		pkt_lat = 0
	
	for x in db_ids:
		curs.execute('SELECT gateway_id FROM Lora_Gateway_PKT_Data WHERE id ='+ str(x))
		pkt_gtiD = curs.fetchone()[0]
		curs.execute('SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id ='+ str(x))
		pkt_data = curs.fetchone()[0]
		gw_check_id = Gateway_Check(pkt_data)
		curs.execute('SELECT pkt_rssi FROM Lora_Gateway_PKT_Data WHERE id ='+ str(x))
		pkt_rssi = int(curs.fetchone()[0])
		#Set RSSI values from gateways
		for y in range(0, len(Gw_Loc_db)):
			if Gw_Loc_db[y][0] == pkt_gtiD:
				Gw_RSSI[y] = pkt_rssi 
				if gw_check_id == "Not Found":
					Gw_RSSI[y] = pkt_rssi + 60 #For non-antenna connections
			if gw_check_id != "Not Found":
				if Gw_Loc_db[y][0] == gw_check_id:
					Gw_RSSI[y] = -20 #The packet was from a gateway so max dB set
	
	new_cell_row = Gw_RSSI
	new_cell_row.insert(0,(db_ids[0])) #Add iD to front
	new_cell_row.append(pkt_long)
	new_cell_row.append(pkt_lat)
	conn.close()
	return (new_cell_row)

def update_CSVs_from_DB():
	conn = sqlite3.connect(Lora_GTW_DB)
	curs = conn.cursor()
	curs.execute('SELECT max(id) FROM Lora_Gateway_PKT_Data')
	max_id = int(curs.fetchone()[0])+1
	conn.close()
	row=1
	DATA_to_GTW_CSV = []
	DATA_to_NODE_CSV = []
	node_matrix_ids = []

	while row <= max_id:
		conn = sqlite3.connect(Lora_GTW_DB)
		curs = conn.cursor()
		curs.execute('INSERT INTO Lora_Gateway_PKT_Data DEFAULT VALUES')
		curs.execute('SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id ='+ str(row))
		pkt_data_one = curs.fetchone()[0]
		curs.execute('SELECT pkt_longitude FROM Lora_Gateway_PKT_Data WHERE id ='+ str(row))
		pkt_long = curs.fetchone()[0]
		pkt_matrix_ids = None
		pkt_matrix_ids = [row]
		row_max = row+12
		while row_max > max_id:
			row_max = row_max-1
		for x in range (row+1, row_max):
			curs.execute('SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id ='+ str(x))
			pkt_data_query = curs.fetchone()[0]
			if pkt_data_query == pkt_data_one:
				pkt_matrix_ids.append(x)
		curs.execute('DELETE FROM Lora_Gateway_PKT_Data WHERE id ='+ str(max_id))
		conn.close()
		row = row + 1
		if pkt_matrix_ids is not None:
			if len(pkt_matrix_ids) >= 3:
				gw_check_id = Gateway_Check(pkt_data_one)
				if gw_check_id != "Not Found":
					DATA_to_GTW_CSV.append(new_cell_for_ML(pkt_matrix_ids))
				else:
					if (pkt_long is None) or (pkt_long == ""):
						DATA_to_NODE_CSV.append(new_cell_for_ML(pkt_matrix_ids))
						node_matrix_ids.append(pkt_matrix_ids)
	for x in range(0,len(node_matrix_ids)-1):
		try:
			if set(node_matrix_ids[x]).issuperset(set(node_matrix_ids[x+1])) :
				del node_matrix_ids[x+1]
				del DATA_to_NODE_CSV[x+1]
		except:
			print("reached end")
	conn = sqlite3.connect(Lora_GTW_DB)
	curs = conn.cursor()
	conn.close()
	#Create CSV for Gateway data to train model
	create_CSV(Lora_GTW_PP, DATA_to_GTW_CSV)
	#Create CSV for Node data to query model
	create_CSV(Lora_NODE_PP, DATA_to_NODE_CSV)
	return (DATA_to_NODE_CSV, node_matrix_ids)

#Update the SQL database with the estimated locations
def update_SQL_DB_loc(node_loc_ARR, node_ID_ARR):
	conn = sqlite3.connect(Lora_GTW_DB)
	curs = conn.cursor()
	for x in range(0, len(node_ID_ARR)):
		for id_Z in node_ID_ARR[x]:
			curs.execute('''UPDATE Lora_Gateway_PKT_Data SET pkt_longitude = ? WHERE id = ?''', (node_loc_ARR[x][0], id_Z))
			curs.execute('''UPDATE Lora_Gateway_PKT_Data SET pkt_latitude = ? WHERE id = ?''', (node_loc_ARR[x][1], id_Z))
	conn.commit()
	conn.close()
	
#***************Main Code Here*********************************************************************************************

#train_localisation_model()
while True:
	node_loc_queries, node_matrix_id = update_CSVs_from_DB()
	print(node_loc_queries)
	if len(node_loc_queries) > 0:
		node_loc_answer = loc_single_predict(node_loc_queries)
		print(node_loc_answer)
		update_SQL_DB_loc(node_loc_answer, node_matrix_id)
	time.sleep(1)
	print("Next Round")
	