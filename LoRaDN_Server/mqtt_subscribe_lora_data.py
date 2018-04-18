""" Created by Nissanka Mendis on 18/03/2018"""
# MQTT subscriber and database transferer

import paho.mqtt.client as mqtt
from sql_lora_data_transfer import lora_Data_Handler

#MQTT Settings
MQTT_Broker = "iot.eclipse.org"
MQTT_Port = 1883
Keep_Alive_Interval = 5
MQTT_Topic = "UCL4thYearLORA/#"

#Subscribe to all gateway up and down data at base topic
def on_connect(mosq,obj,flags,rc):
	mqttc.subscribe(MQTT_Topic,0)

#Save Data to DB table
def on_rec_message(mosq, onj, msg):
	lora_Data_Handler(msg.topic, msg.payload)

def on_subscribe(mosq, obj, mid, granted_qos):
	pass

mqttc= mqtt.Client()

# Assign on event callbacks
mqttc.on_message = on_rec_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe

#Connect
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))

mqttc.loop_forever()
