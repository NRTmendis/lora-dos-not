from flask import Flask
from flask_socketio import SocketIO
from time import strftime, sleep
import json
# from flask_cors import cross_origin, CORS
import sqlite3
import paho.mqtt.client as mqtt
import mqtt_broadcast
from threading import Thread


def log(msg):
    print(strftime("[%H:%M:%S]: ") + str(msg))


BROKER = "iot.eclipse.org"
PORT = 1883
KEEP_ALIVE = 60
TOPIC = "UCL4thYearLORA/gatewayUpdateDATA"

mqttc = mqtt.Client()
mqttc.loop_start()
mqttc.on_connect = mqtt_broadcast.on_connect
mqttc.on_disconnect = mqtt_broadcast.on_disconnect
mqttc.on_publish = mqtt_broadcast.on_publish
mqttc.connect(BROKER, int(PORT), int(KEEP_ALIVE))

app = Flask(__name__)
socketio = SocketIO(app)

# conn = sqlite3.connect('../LoRaDN_Server/lora_GTW.db')
# c = conn.cursor()

# State
curr_id = 0
TIMEOUT = 0.5  # seconds
nodes = {}


def is_node(pkt_data):
    return True if 'NiD' in pkt_data else False


def query_database():
    conn = sqlite3.connect('../LoRaDN_Server/lora_GTW.db')
    c = conn.cursor()
    while True:
        sleep(TIMEOUT)
        global curr_id, nodes
        max_id = c.execute(
            "SELECT MAX(ID) FROM Lora_Gateway_PKT_Data").fetchone()[0]
        if curr_id < max_id:
            new_data = c.execute(
                """
                SELECT
                    pkt_data,
                    pkt_longitude,
                    pkt_latitude
                FROM Lora_Gateway_PKT_Data
                WHERE ID BETWEEN ? AND ?
                """,
                (curr_id + 1, max_id))
            for entry in new_data:
                try:
                    pkt_data = json.loads(entry[0])
                    if is_node(pkt_data):
                        nodes[pkt_data['NiD']] = {
                            "lng": entry[1],
                            "lat": entry[2],
                            "lightVal": pkt_data['LVal']
                        }
                except Exception as e:
                    log("Error parsing packet data: {}".format(e))
                    continue
            curr_id = max_id
            log("Last ID pulled: {}.".format(curr_id))
            # socketio.emit('nodeUpdate', nodes)


thread = Thread(target=query_database)
thread.start()


@socketio.on('connect')
def connect():
    global nodes
    log("Client is connected.")
    socketio.emit('nodeUpdate', nodes)  # TODO

    @socketio.on('update')
    def update():
        global nodes
        socketio.emit('nodeUpdate', nodes)

    @socketio.on("gatewayUpdate")
    def update_gateway_settings(settings_json):
        settings_json = json.loads(settings_json)
        log("Received message: {}".format(settings_json))
        mqtt_broadcast.publish_MTCE_INFO_2_Gateways(
            mqttc,
            m_angle=settings_json['angle'],
            broadcast_rate=settings_json['broadcastRate']
        )


if __name__ == "__main__":
    socketio.run(app)
