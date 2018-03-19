import paho.mqtt.client as mqtt
from datetime import datetime
import json
import base64
from datetime import datetime

# MQTT Settings 
M_Broker = "iot.eclipse.org"
M_Port = 1883
Keep_Alive = 60
MQTT_Topic = "UCL4thYearLORA/gatewayUpdateDATA"

MTCE_PK = {
    'gtiD': '',
    'time': '',
	'M_Angle': '',
	'Broadcast_Rate': ''
}

def _make_mtce_packet(gateway,M_Angle,Broadcast_Rate):
	MTCE_PK["gtiD"] = str(gateway)
	MTCE_PK["time"] = (datetime.today()).strftime("%d-%b-%Y %H:%M:%S:%f")
	MTCE_PK["M_Angle"] = str(M_Angle)
	MTCE_PK["Broadcast_Rate"] = int(Broadcast_Rate)
	return json.dumps(MTCE_PK)
		
def on_connect(client, userdata, rc):
	if rc != 0:
		pass
		print("Unable to connect to MQTT Broker...")
	else:
		print("Connected with MQTT Broker: " + str(M_Broker))

def on_publish(client, userdata, mid):
	pass
		
def on_disconnect(client, userdata, rc):
	if rc !=0:
		pass
				
def publish(topic, message):
	mqttc.publish(topic,message)
	print ("Published message on MQTT Topic: " + str(topic))

def publish_MTCE_INFO_2_Gateways(recepient="All", M_Angle=0, Broadcast_Rate=60):
	MTCE_pkt = _make_mtce_packet(recepient, M_Angle, Broadcast_Rate)
	print("Packet Made")
	print(MTCE_pkt)
	MTCE_pkt_en = base64.b64encode(bytes(MTCE_pkt, "utf-8"))
	print("Packet Encoded")
	publish(MQTT_Topic, MTCE_pkt_en)
	

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.connect(M_Broker, int(M_Port), int(Keep_Alive))	

eggs=True
while (eggs==True):
	mqttc = mqtt.Client()
	mqttc.on_connect = on_connect
	mqttc.on_disconnect = on_disconnect
	mqttc.on_publish = on_publish
	mqttc.connect(M_Broker, int(M_Port), int(Keep_Alive))	
	b_rate = input("What period would you like to set the LoRa Broadcast rate of the gateways?")
	try:
		b_rate_num = int(b_rate)
		publish_MTCE_INFO_2_Gateways(Broadcast_Rate=b_rate_num)
	except Exception as ex:
		print("Error: " + str(ex))