""" LoPy LoRa Nano Gateway MQTT """
""" Based on original LoRa nanogateway.py by Pycom-LoPy: Daniel Campora https://github.com/pycom/pycom-libraries/blob/master/examples/lorawan-nano-gateway/nanogateway.py"""
""" Modified by Nissanka Mendis on 18/03/2018"""

import config
from LoraMQTT import NanoGateway

if __name__ == '__main__':
    nanogw = NanoGateway(
        id=config.GATEWAY_ID,
        frequency=config.LORA_FREQUENCY,
        datarate=config.LORA_GW_DR,
        ssid=config.WIFI_SSID,
        password=config.WIFI_PASS,
        user=config.WIFI_USER,
        server=config.SERVER,
        port=config.PORT,
		tpc_snd=config.SND_TPC,
		tpc_mtce=config.MTCE_TPC,
        ntp_server=config.NTP,
        ntp_period=config.NTP_PERIOD_S
        )

    nanogw.start()
    nanogw._log('You may now press ENTER to enter the REPL')
    input()