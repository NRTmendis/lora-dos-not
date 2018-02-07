""" LoPy LoRaWAN Nano Gateway configuration options """

import machine
import ubinascii

WIFI_MAC = ubinascii.hexlify(machine.unique_id()).upper()
# Set  the Gateway ID to be the first 3 bytes of MAC address + 'F01E' + last 3 bytes of MAC address
GATEWAY_ID = WIFI_MAC[:6] + "F01E" + WIFI_MAC[6:12]

SERVER = 'iot.eclipse.org'
PORT = 1883

SND_TPC = 'UCL4thYearLORA/NodeDATA'
MTCE_TPC = 'UCL4thYearLORA/gatewayUpdateDATA'

NTP = "time.google.com"
NTP_PERIOD_S = 180

WIFI_SSID = 'eduroam'
WIFI_USER = 'XXXXXXXXXXXXXX'
WIFI_PASS = 'XXXXXXXXXXX'

# for EU868
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5

# for US915
# LORA_FREQUENCY = 903900000
# LORA_GW_DR = "SF7BW125" # DR_3
# LORA_NODE_DR = 3