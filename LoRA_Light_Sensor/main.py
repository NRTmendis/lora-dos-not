""" LoRa Light Sensor """
​
from network import LoRa
import usocket
import binascii
import ujson
import struct
import time
import machine
import ubinascii
import uos
​
WIFI_MAC = ubinascii.hexlify(machine.unique_id()).upper()
DEVICE_ID = 0x01

TX_PK = {
    'NiD': '',
    'LVal': ''
}

def dr_to_sf(dr):
	sf = dr[2:4]
	if sf[1] not in '0123456789':
		sf = sf[:1]
	return int(sf)

def dr_to_bw(dr):
	bw = dr[-5:]
	if bw == 'BW125':
		return LoRa.BW_125KHZ
	elif bw == 'BW250':
		return LoRa.BW_250KHZ
	else:
		return LoRa.BW_500KHZ

def _make_node_packet(val):
        TX_PK["NiD"] = WIFI_MAC
        TX_PK["LVal"] = val
        return ujson.dumps(TX_PK)

# for EU868
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5
_LORA_PKG_FORMAT = "BB%ds"
# initialize LoRa in LORAWAN mode.
lora = LoRa(
	mode=LoRa.LORA,
	frequency=LORA_FREQUENCY,
	bandwidth=dr_to_bw(LORA_GW_DR),
	sf=dr_to_sf(LORA_GW_DR),
	preamble=8,
	coding_rate=LoRa.CODING_4_5,
	)

# set the 3 default channels to the same frequency
lora.add_channel(0, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(1, frequency=868100000, dr_min=0, dr_max=5)
lora.add_channel(2, frequency=868100000, dr_min=0, dr_max=5)

# remove all the non-default channels
for i in range(3, 16):
    lora.remove_channel(i)

# create a LoRa socket
lora_sock = usocket.socket(usocket.AF_LORA, usocket.SOCK_RAW)
lora_sock.setsockopt(usocket.SOL_LORA, usocket.SO_DR, 5)
​
# make the socket blocking
lora_sock.setblocking(False)
​
adc = machine.ADC()             # create an ADC object
apin = adc.channel(pin='P13')   # create an analog pin on P13
​

def val_send(value):
   lora_sock.send(value)
   time.sleep(10)
   #rx, port = lora_sock.recvfrom(256)
   #if rx:
   #    print('Received: {}, on port: {}'.format(rx, port))
   #time.sleep(6.0)


while (True):
   val = apin()                  # read an analog value
   val2 = int(val)
   #val2 = (uos.urandom(12)[4])
   valPKT=_make_node_packet(val2)
   print(valPKT)
   val_send(valPKT)