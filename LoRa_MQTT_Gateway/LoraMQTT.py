""" Based on original LoRa nanogateway.py by Pycom-LoPy: Daniel Campora https://github.com/pycom/pycom-libraries/blob/master/examples/lorawan-nano-gateway/nanogateway.py"""
""" LoPy LoRa Nano Gateway to private MQTT Server for both publishing packets and subscribing to service updates. Can be used for both EU868 and US915. """

""" Modified by Nissanka Mendis on 18/11/2017"""

import errno
import machine
import ubinascii
import ujson
import uos
import usocket
import utime
import _thread
from micropython import const
from network import LoRa
from network import WLAN
from machine import Timer
from simple import  MQTTClient

PROTOCOL_VERSION = const(2)

PUSH_DATA = const(0)
PUSH_ACK = const(1)
PULL_DATA = const(2)
PULL_ACK = const(4)
PULL_RESP = const(3)

TX_ERR_NONE = 'NONE'
TX_ERR_TOO_LATE = 'TOO_LATE'
TX_ERR_TOO_EARLY = 'TOO_EARLY'
TX_ERR_COLLISION_PACKET = 'COLLISION_PACKET'
TX_ERR_COLLISION_BEACON = 'COLLISION_BEACON'
TX_ERR_TX_FREQ = 'TX_FREQ'
TX_ERR_TX_POWER = 'TX_POWER'
TX_ERR_GPS_UNLOCKED = 'GPS_UNLOCKED'

UDP_THREAD_CYCLE_MS = const(10)

STAT_PK = {
    'gtiD': '',
    'time': ''
}

RX_PK = {
    'gtiD': '',
    'time': '',
    'tmst': 0,
    'chan': 0,
    'rfch': 0,
    'freq': 0,
    'stat': 1,
    'modu': 'LORA',
    'datr': '',
    'codr': '4/5',
    'rssi': 0,
    'lsnr': 0,
    'size': 0,
    'data': ''
}

class NanoGateway:
    """
    Nano gateway class, configured to connect to private MQTT Server
    Configuration requried in config.py for wifi access and MQTT server connections and LoRa frequency.
    """

    def __init__(self, id, frequency, datarate, ssid, user, password, server, port, tpc_snd, tpc_mtce, ntp_server='pool.ntp.org', ntp_period=3600, bcast_pkt_gtw_period=60):
        self.id = id
        self.server = server
        self.port = port
        self.tpc_snd = tpc_snd
        self.tpc_mtce = tpc_mtce

        self.frequency = frequency
        self.datarate = datarate

        self.ssid = ssid
        self.user = user
        self.password = password

        self.ntp_server = ntp_server
        self.ntp_period = ntp_period

        self.server_ip = None


        self.sf = self._dr_to_sf(self.datarate)
        self.bw = self._dr_to_bw(self.datarate)

        self.stat_alarm = None

        self.wlan = None
        self.sock = None

        self.bcast_pkt_gtw_period = bcast_pkt_gtw_period

        #maintnenace MQTT subscription flag
        self.MQTTsub_stop = False

        self.lora = None
        self.lora_sock = None

        self.rtc = machine.RTC()

    def start(self):
        """
        Starts the LoRa nano gateway.
        """

        self._log('Starting LoRa MQTT nano gateway with id: {}', self.id)

        # setup WiFi as a station and connect
        self.wlan = WLAN(mode=WLAN.STA)
        self._connect_to_wifi()
        
        # get a time sync
        self._log('Syncing time with {} ...', self.ntp_server)
        self.rtc.ntp_sync(self.ntp_server, update_period=self.ntp_period)
        while not self.rtc.synced():
            utime.sleep_ms(50)
        self._log("RTC NTP sync complete")
		
		#MQTT Server connection
        self.client = MQTTClient(self.id, self.server, port=self.port)
        self.client.connect()
        self._log("MQTT Server connected")

        # push the first time immediatelly
        self._send_down_link(self._make_stat_packet(), self.datarate, self.frequency)

        # create the alarm for LoRa stats
        self.stat_alarm = Timer.Alarm(handler=lambda t: self._send_down_link(self._make_stat_packet(), self.datarate, self.frequency), s=self.bcast_pkt_gtw_period, periodic=True)

        # start the MQTT subscriber thread to receive data
        _thread.start_new_thread(self._MQTT_subscribe_thread, ())

        # initialize the LoRa radio in LORA mode
        self._log('Setting up the LoRa radio at {:.1f} Mhz using {}', self._freq_to_float(self.frequency), self.datarate)
        self.lora = LoRa(
            mode=LoRa.LORA,
            frequency=self.frequency,
            bandwidth=self.bw,
            sf=self.sf,
            preamble=8,
            coding_rate=LoRa.CODING_4_5,
			power_mode=LoRa.ALWAYS_ON,
            tx_iq=True
        )

        # create a raw LoRa socket
        self.lora_sock = usocket.socket(usocket.AF_LORA, usocket.SOCK_RAW)
        self.lora_sock.setblocking(False)
        self.lora_tx_done = False

        self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self._lora_cb)
        self._log('LoRaWAN MQTT nano gateway online')

    def stop(self):
        """
        Stops the LoRaWAN nano gateway.
        """

        self._log('Stopping...')

        # send the LoRa radio to sleep
        self.lora.callback(trigger=None, handler=None)
        self.lora.power_mode(LoRa.SLEEP)

        # stop the NTP sync
        self.rtc.ntp_sync(None)

        # cancel all the alarm
        self.stat_alarm.cancel()

        # disable WLAN
        self.wlan.disconnect()
        self.wlan.deinit()

    def _connect_to_wifi(self):
        self.wlan.connect(self.ssid, auth=(WLAN.WPA2_ENT, self.user, self.password ), identity=self.user)
        conn_cc = 0
        while not self.wlan.isconnected():
            utime.sleep_ms(50)
			conn_cc = conn_cc + 1
            if (conn_cc > 200) :
                machine.reset()
        self._log('WiFi connected to: {}', self.ssid)

    def _dr_to_sf(self, dr):
        sf = dr[2:4]
        if sf[1] not in '0123456789':
            sf = sf[:1]
        return int(sf)

    def _dr_to_bw(self, dr):
        bw = dr[-5:]
        if bw == 'BW125':
            return LoRa.BW_125KHZ
        elif bw == 'BW250':
            return LoRa.BW_250KHZ
        else:
            return LoRa.BW_500KHZ

    def _sf_bw_to_dr(self, sf, bw):
        dr = 'SF' + str(sf)
        if bw == LoRa.BW_125KHZ:
            return dr + 'BW125'
        elif bw == LoRa.BW_250KHZ:
            return dr + 'BW250'
        else:
            return dr + 'BW500'

    def _lora_cb(self, lora):
        """
        LoRa radio events callback handler.
        """

        events = lora.events()
        if events & LoRa.RX_PACKET_EVENT:
            rx_data = self.lora_sock.recv(256)
            stats = lora.stats()
            packet = self._make_node_packet(rx_data, self.rtc.now(), stats.rx_timestamp, stats.sfrx, self.bw, stats.rssi, stats.snr)
            self._push_data(packet)
            self._log('Received packet: {}', packet)
        if events & LoRa.TX_PACKET_EVENT:
            lora.init(
                mode=LoRa.LORA,
                frequency=self.frequency,
                bandwidth=self.bw,
                sf=self.sf,
                preamble=8,
                coding_rate=LoRa.CODING_4_5,
                tx_iq=True
                )

    def _freq_to_float(self, frequency):
        """
        MicroPython has some inprecision when doing large float division.
        To counter this, this method first does integer division until we
        reach the decimal breaking point. This doesn't completely elimate
        the issue in all cases, but it does help for a number of commonly
        used frequencies.
        """

        divider = 6
        while divider > 0 and frequency % 10 == 0:
            frequency = frequency // 10
            divider -= 1
        if divider > 0:
            frequency = frequency / (10 ** divider)
        return frequency

    def _make_stat_packet(self):
        now = self.rtc.now()
        STAT_PK["gtiD"] = self.id
        STAT_PK["time"] = "%d-%02d-%02dT%02d:%02d:%02d.%dZ" % (now[0], now[1], now[2], now[3], now[4], now[5], now[6])
        return ujson.dumps(STAT_PK)

    def _make_node_packet(self, rx_data, rx_time, tmst, sf, bw, rssi, snr):
        RX_PK["gtiD"] = self.id
        RX_PK["time"] = "%d-%02d-%02dT%02d:%02d:%02d.%dZ" % (rx_time[0], rx_time[1], rx_time[2], rx_time[3], rx_time[4], rx_time[5], rx_time[6])
        RX_PK["tmst"] = tmst
        RX_PK["freq"] = self._freq_to_float(self.frequency)
        RX_PK["datr"] = self._sf_bw_to_dr(sf, bw)
        RX_PK["rssi"] = rssi
        RX_PK["lsnr"] = snr
        RX_PK["data"] = ubinascii.b2a_base64(rx_data)
        RX_PK["size"] = len(rx_data)
        return ujson.dumps(RX_PK)

    def _push_data(self, data):
        packet = data
        try:
            self.client.publish(self.tpc_snd, packet)
        except Exception as ex:
            self._log('Failed to send packet to MQTT server: {}', ex)

    def _send_down_link(self, data, datarate, frequency):
        """
        Transmits a downlink message over LoRa.
        """
        #Reset to transmit mode
        self.lora = LoRa(
            mode=LoRa.LORA,
            frequency=self.frequency,
            bandwidth=self.bw,
            sf=self.sf,
            preamble=8,
            coding_rate=LoRa.CODING_4_5,
			power_mode=LoRa.TX_ONLY,
            tx_iq=False
            )
        self.lora_sock = usocket.socket(usocket.AF_LORA, usocket.SOCK_RAW)
        self.lora_sock.setblocking(False)
        self.lora_sock.send(data)
        self._log('Transmitted packet: {}', data)
        #Reset to receive mode
        self.lora = LoRa(
            mode=LoRa.LORA,
            frequency=self.frequency,
            bandwidth=self.bw,
            sf=self.sf,
            preamble=8,
            coding_rate=LoRa.CODING_4_5,
			power_mode=LoRa.ALWAYS_ON,
            tx_iq=True
            )

    def process_msg(self, msg_instruction):
        in_data = msg_instruction
        try:
            self.bcast_pkt_gtw_period = int(in_data)
            self.stat_alarm.cancel()
            sleep_time = int(machine.rng()/ (2**12))
            utime.sleep_ms(sleep_time)
            self.stat_alarm = Timer.Alarm(handler=lambda t: self._send_down_link(self._make_stat_packet(), self.datarate, self.frequency), s=self.bcast_pkt_gtw_period, periodic=True)
        except Exception as ex:
            self._log('Failed to process change of broadcast time alarm: {}', ex)
		

    def sub_cb(self, topic, msg):
        try:
            self.process_msg(msg)
        except Exception as ex:
            self._log('Failed to process incoming message: {}', ex)
        self._log((topic, msg))

    def _MQTT_subscribe_thread(self):
    #    """
    #    Subscribes to maintenance topic from MQTT server to control Gateway Signal Blocker
    #    """
        self.client.set_callback(self.sub_cb)
        try:
            self.client.subscribe(self.tpc_mtce)
        except Exception as ex:
            self._log('Failed to subscribe to MQTT server: {}', ex)
        fail_cc = 0
        while not self.MQTTsub_stop:
            try:
                self.client.check_msg()
            except Exception as ex:
                self._log('Failed to check message MQTT server: {}', ex)
                fail_cc = fail_cc + 1
                if (fail_cc >= 100) :
                    self._log('Failed to check message MQTT server, Restarting Device: {}', ex)
                    machine.reset() #Restart Board to try and re-connect to MQTT.
                

    def _log(self, message, *args):
        """
        Outputs a log message to stdout.
        """

        print('[{:>10.3f}] {}'.format(
            utime.ticks_ms() / 1000,
            str(message).format(*args)
            ))