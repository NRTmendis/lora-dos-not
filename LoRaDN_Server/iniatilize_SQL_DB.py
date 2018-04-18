""" Created by Nissanka Mendis on 18/03/2018"""
# UCL 4th Year LoraWAN project SQL db

import sqlite3

#SQlite DB name
Lora_GTW_DB = "lora_GTW.db"

#SQlite set up tables in database
Table_schm="""
drop table if exists Lora_Gateway_PKT_Data ;
create table Lora_Gateway_PKT_Data (
	id integer primary key autoincrement,
	gateway_id text,
	pkt_date_and_time text,
	pkt_rssi text,
	pkt_snr text,
	pkt_data text,
	pkt_size integer,
	pkt_longitude text,
	pkt_latitude text
);

drop table if exists Lora_Gateway_Send_Data ;
create table Lora_Gateway_Send_Data (
	id integer primary key autoincrement,
	snd_recp text,
	snd_date_and_time text,
	snd_data text
);

"""

#Connect/Create Database File
conn = sqlite3.connect(Lora_GTW_DB)
curs = conn.cursor()

#Create Tables
sqlite3.complete_statement(Table_schm)
curs.executescript(Table_schm)

#Close Database
curs.close()
conn.close()
