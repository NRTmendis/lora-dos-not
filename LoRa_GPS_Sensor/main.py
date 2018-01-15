""" LoRa GPS Sensor """

Nissanka Mendis 15/01/2018
​
from network import LoRa
import usocket
import binascii
import ujson
import time
import machine
import ubinascii
from gps import GPS_UART_start
from gps import NmeaParser
​
WIFI_MAC = ubinascii.hexlify(machine.unique_id()).upper()

TX_PK = {
    'NiD': '',
    'Latitude': '',
	'Longitude': '',
	'Fix-Time': ''
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

def _make_node_packet(val1,val2,val3):
        TX_PK["NiD"] = WIFI_MAC
        TX_PK["Lat"] = val1
		TX_PK["Long"] = val2
		TX_PK["Fx-T"] = val3
        return ujson.dumps(TX_PK)

# for EU868
LORA_FREQUENCY = 868100000
LORA_GW_DR = "SF7BW125" # DR_5
LORA_NODE_DR = 5

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
​def GPS_run():
    while (True):
        if (com.any()):
            data =com.readline()
            if (len(data) >= 67):
                if (data[0:7] == b'$GPGGA,'):
                    place = NmeaParser()
                    place.update(data)
					return _make_node_packet(place.latitude,place.longitude,place.fix_time)

def val_send(value):
   lora_sock.send(value)
   time.sleep(2)
   #rx, port = lora_sock.recvfrom(256)
   #if rx:
   #    print('Received: {}, on port: {}'.format(rx, port))
   #time.sleep(6.0)

   
print('GPS start')
com = GPS_UART_start()
while (True):
   valPKT=GPS_run()
   print(valPKT)
   val_send(valPKT)