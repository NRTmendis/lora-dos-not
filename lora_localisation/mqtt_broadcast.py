"""Modified by Ayush Singh 18/03/2018"""
from datetime import datetime
import json
import base64
from time import strftime

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


def log(msg):
    print(strftime("[%H:%M:%S]: ") + msg)


def _make_mtce_packet(gateway, M_Angle, Broadcast_Rate):
    MTCE_PK["gtiD"] = str(gateway)
    MTCE_PK["time"] = (datetime.today()).strftime("%d-%b-%Y %H:%M:%S:%f")
    MTCE_PK["M_Angle"] = str(M_Angle)
    MTCE_PK["Broadcast_Rate"] = int(Broadcast_Rate)
    return json.dumps(MTCE_PK)


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        log("Unable to connect to MQTT Broker...")
    else:
        log("Connected with MQTT Broker: {}".format(str(M_Broker)))


def on_publish(client, userdata, mid):
    log("Published packet to MQTT Topic")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        pass


def publish(client, topic, message):
    client.publish(topic, message)
    # log("Published packet to MQTT Topic: {}".format(str(topic)))


def publish_MTCE_INFO_2_Gateways(client, recepient="All", m_angle="Nan",
                                 broadcast_rate=60):
    MTCE_pkt = _make_mtce_packet(recepient, m_angle, broadcast_rate)
    log("Packet constructed: {}".format(MTCE_pkt))
    MTCE_pkt_en = base64.b64encode(bytes(MTCE_pkt, "utf-8"))
    log("Packet encoded: {}".format(MTCE_pkt_en))
    publish(client, MQTT_Topic, MTCE_pkt_en)
