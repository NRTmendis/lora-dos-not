import sqlite3
import csv
import sys
import time

#SQlite DB name
Lora_GTW_DB = "lora_GTW.db"

#Convert SQL database to csv

def updateDatabaseCSV():

	SVR = sqlite3.connect(Lora_GTW_DB)
	cursor = SVR.cursor()
	cursor.execute('SELECT * FROM Lora_Gateway_PKT_Data')
	with open('lora_DB.csv','wb') as out_csv_file:
	  csv_out = csv.writer(out_csv_file)                      
	  csv_out.writerow([d[0] for d in cursor.description])                         
	  for result in cursor:
	    csv_out.writerow(result)
	SVR.close()


while(True):
	updateDatabaseCSV()
	time.sleep(2)