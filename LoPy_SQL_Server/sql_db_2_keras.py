#Author Nissanka Mendis
#SQL DB data to Machine Learning CSV format parser

import sqlite3
import csv
import json

#SQlite DB name
Lora_GTW_DB = "lora_GTW.db"

#CSV Out name
Lora_GTW_PP = "lora_GTW_PP.csv"

Gw_Loc_db = [
		["240AC4F01E023C54",9.05,4.58],	#A
		["240AC4F01E0286DC",9.05,1.5],	#B
		["240AC4F01E025FF4",0.66,4.58],	#C
		["240AC4F01E023E3C",0.66,0.33]	#D
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
		
def new_cell_for_ML(cell_row, db_ids):
	#Set all Gateway RSSI to -150dB, noise floor level
	Gw_RSSI = [-150]
	for x in range(1, len(Gw_Loc_db)):
		Gw_RSSI.append(-150)
	#Get the PKTs Longitude and Lattitude, if they are gateway PKTs
	curs.execute('SELECT pkt_longitude FROM Lora_Gateway_PKT_Data WHERE id ='+ str(db_ids[0]))
	pkt_long = curs.fetchone()[0]
	if pkt_long is None:
		pkt_long = 0
		
	curs.execute('SELECT pkt_latitude FROM Lora_Gateway_PKT_Data WHERE id ='+ str(db_ids[0]))
	pkt_lat = curs.fetchone()[0]
	if pkt_lat is None:
		pkt_lat = 0
	
	for x in db_ids:
		curs.execute('SELECT gateway_id FROM Lora_Gateway_PKT_Data WHERE id ='+ str(x))
		pkt_gtiD = curs.fetchone()[0]
		curs.execute('SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id ='+ str(x))
		pkt_data = curs.fetchone()[0]
		gw_check_id = Gateway_Check(pkt_data)
		#Set RSSI values from gateways
		for y in range(0, len(Gw_Loc_db)):
			if Gw_Loc_db[y][0] == pkt_gtiD:
				curs.execute('SELECT pkt_rssi FROM Lora_Gateway_PKT_Data WHERE id ='+ str(x))
				pkt_rssi = int(curs.fetchone()[0])
				Gw_RSSI[y] = pkt_rssi
			if gw_check_id != "Not Found":
				if Gw_Loc_db[y][0] == gw_check_id:
					Gw_RSSI[y] = -20	#The packet was from a gateway so max dB set
	
	new_cell_row = Gw_RSSI
	new_cell_row.insert(0,(cell_row+1)) #Add iD to front
	new_cell_row.append(pkt_long)
	new_cell_row.append(pkt_lat)
	return (new_cell_row)

conn = sqlite3.connect(Lora_GTW_DB)
curs = conn.cursor()
curs.execute('SELECT max(id) FROM Lora_Gateway_PKT_Data')
max_id = int(curs.fetchone()[0])

row=1
cell_row=0
DATA_to_CSV = []

while row <= max_id:
	curs.execute('SELECT pkt_data FROM Lora_Gateway_PKT_Data WHERE id ='+ str(row))
	pkt_data_one = curs.fetchone()[0]
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
	if pkt_matrix_ids is not None:
		if len(pkt_matrix_ids) >= 3:
			DATA_to_CSV.append(new_cell_for_ML(cell_row, pkt_matrix_ids))
			cell_row = cell_row + 1
	row = row + 1

#Close SQL DB
conn.close()
#Create CSV Header
max_GW = len(DATA_to_CSV[0])-3
CSV_header = ["iD"]
for x in range(0, max_GW):
	CSV_header.append("GW_RSSI_"+str(x+1))
CSV_header.append("GW_Long")
CSV_header.append("GW_Lat")
#Write to CSV
with open(Lora_GTW_PP,'w', newline='') as out_csv_file:
	csv_out = csv.writer(out_csv_file)
	csv_out.writerow(CSV_header)
	csv_out.writerows(DATA_to_CSV)