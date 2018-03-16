from flask import Flask
from flask.json import jsonify
from flask_socketio import SocketIO, emit
from time import strftime
import json
# from flask_cors import cross_origin, CORS
import sqlite3
import paho.mqtt.client as mqtt
import mqtt_broadcast

# MQTT Setup
# MQTT Settings
BROKER = "iot.eclipse.org"
PORT = 1883
KEEP_ALIVE = 60
TOPIC = "UCL4thYearLORA/gatewayUpdateDATA"

mqttc = mqtt.Client()
mqttc.on_connect = mqtt_broadcast.on_connect
mqttc.on_disconnect = mqtt_broadcast.on_disconnect
mqttc.on_publish = mqtt_broadcast.on_publish
mqttc.connect(BROKER, int(PORT), int(KEEP_ALIVE))

# Fake Data Input
# INSERT INTO
#   Lora_Gateway_PKT_Data
# VALUES (
#   562,
#   "240A14F01E023E3C",
#   "2018-02-14T15:57:43.447866Z",
#   -45,
#   8.0,
#   '{"NiD": "Test3", "LVal":56}',
#   36,
#   11,
#   6
# );

app = Flask(__name__)
socketio = SocketIO(app)
# CORS(app)

conn = sqlite3.connect('../LoRaDN_Server/lora_GTW.db')
c = conn.cursor()


def log(msg):
    print(strftime("[%H:%M:%S]: ") + msg)


def is_node(pkt_data):
    if 'NiD' in pkt_data:
        return True
    return False


@app.route('/latest/<gateway_id>', methods=['GET'])
def hello(gateway_id):
    x = c.execute(
        """
        SELECT
            *
        FROM Lora_Gateway_PKT_Data
        WHERE gateway_id=?
        ORDER BY ID DESC LIMIT 1
        """,
        (gateway_id,))
    return jsonify(items=list(x))


@socketio.on('connect', namespace="/")
def connect():
    log("Client is connected.")

    @socketio.on('update', namespace="/")
    def update_node_location(curr_id):
        max_id = c.execute(
            "SELECT MAX(ID) FROM Lora_Gateway_PKT_Data").fetchone()[0]
        if curr_id < max_id:
            new = c.execute(
                """SELECT
                    pkt_data,
                    pkt_longitude,
                    pkt_latitude
                FROM Lora_Gateway_PKT_Data
                WHERE ID BETWEEN ? AND ?""",
                (curr_id + 1, max_id))
            for entry in new:
                try:
                    pkt_data = json.loads(entry[0])
                    if is_node(pkt_data):
                        pkt_data["lng"] = entry[1]
                        pkt_data["lat"] = entry[2]
                        emit('nodeFound', pkt_data)
                except Exception as e:
                    log("Error parsing packet data: {}".format(e))
                    continue
            curr_id = max_id
            log("Last ID pulled: {}.".format(curr_id))
            emit('currIdChange', curr_id)

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
