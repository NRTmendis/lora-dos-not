""" LoPy LoRa Nano Gateway MQTT """

import config
from LoraMQTT import NanoGateway

if __name__ == '__main__':
    nanogw = NanoGateway(
        id=config.GATEWAY_ID,
        frequency=config.LORA_FREQUENCY,
        datarate=config.LORA_GW_DR,
        ssid=config.WIFI_SSID,
		user=config.WIFI_USER,
        password=config.WIFI_PASS,
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