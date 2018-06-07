"""Created by Ayush Singh 18/03/2018"""
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


# MQTT
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

# State
curr_id = 0
DATABASE_LOCATION = '../LoRaDN_Server/lora_GTW.db'
TIMEOUT = 1  # seconds
BACKTRACK_RATE = 100
nodes = {}


def is_node(pkt_data):
    return True if 'NiD' in pkt_data else False


def get_max_id(db_cursor):
    return db_cursor.execute(
        "SELECT MAX(ID) FROM Lora_Gateway_PKT_Data"
    ).fetchone()[0]


def get_all_pkt_data(db_cursor):
    return db_cursor.execute("""
        SELECT
            pkt_data,
            pkt_longitude,
            pkt_latitude
        FROM Lora_Gateway_PKT_Data
    """)


def get_sliced_pkt_data(db_cursor, id_from, id_to):
    return db_cursor.execute("""
        SELECT
            pkt_data,
            pkt_longitude,
            pkt_latitude
        FROM Lora_Gateway_PKT_Data
        WHERE ID BETWEEN ? AND ?
    """, (id_from, id_to))


def query_database():
    db_connection = sqlite3.connect(DATABASE_LOCATION)
    db_cursor = db_connection.cursor()
    while True:
        sleep(TIMEOUT)
        global curr_id, nodes
        max_id = get_max_id(db_cursor)
        if curr_id < max_id:
            new_data = None
            if max_id < BACKTRACK_RATE:
                new_data = get_all_pkt_data(db_cursor)
            else:
                new_data = get_sliced_pkt_data(
                    db_cursor,
                    curr_id - BACKTRACK_RATE,
                    max_id
                )
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
            socketio.emit('nodeUpdate', nodes)
            curr_id = max_id
            log("Last ID pulled: {}.".format(curr_id))


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
