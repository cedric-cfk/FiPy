import binascii
import machine
import network
import time
import sys

from config import Config

class WLan():

    def __init__(self, config):
        self.config = config
        self.wlan = network.WLAN()

    def is_connected(self):
        return self.wlan.mode() == network.WLAN.STA and self.wlan.isconnected()

    def is_inApMode(self):
        return self.wlan.mode() == network.WLAN.AP

    def joined_ap_info(self):
        return self.wlan.joined_ap_info()

    def configure_antenna(self):
        # https://community.hiveeyes.org/t/signalstarke-des-wlan-reicht-nicht/2541/11
        # https://docs.pycom.io/firmwareapi/pycom/network/wlan/

        antenna_external = self.config.get_value('networking', 'network_config', 'antenna_external')
        print("Using Antenna: ", antenna_external)
        if antenna_external:
            antenna_pin = self.config.get_value('networking', 'network_config', 'antenna_pin')
            print('WiFi: Using external antenna on pin %s', antenna_pin)

            # To use an external antenna, set P12 as output pin.
            from machine import Pin
            Pin(antenna_pin, mode=Pin.OUT)(True)

            # Configure external WiFi antenna.
            self.wlan.antenna(network.WLAN.EXT_ANT)
            print('Antenna set')

        else:
            print('WiFi: Using internal antenna')
            self.wlan.antenna(network.WLAN.INT_ANT)
            print('Antenna set')

    def scan(self):
        self.wlan.deinit()
        time.sleep(1)
        self.configure_antenna()
        # Scan to find all available SSIDs
        self.wlan.init(mode=network.WLAN.STA)
        scan = self.wlan.scan()
        ssids = [{
            'ssid': s.ssid,
            'bssid': binascii.hexlify(s.bssid).decode('utf-8'),
            'sec': s.sec,
            'channel': s.channel,
            'rssi': s.rssi} for s in scan]
        for ssid in ssids:
            print(ssid['ssid'])
            for item in ssid:
                print("{}: {}".format(item,ssid[item]))
        self.config.set_value('networking', 'network_config', 'available', ssids)
        self.config.write()
        self.wlan.deinit()
        return len(ssids)

    def enable_ap(self):

        # Resolve mode to its numeric code
        mode = network.WLAN.AP

        ssid = self.config.get_value('networking', 'accesspoint', 'ssid')
        password = self.config.get_value('networking', 'accesspoint', 'password')
        encryption = self.config.get_value('networking', 'accesspoint', 'encryption')
        channel = self.config.get_value('networking', 'accesspoint', 'channel')

        try:
            self.wlan.deinit()
            time.sleep(1)
            self.wlan.init(mode=mode,
                           ssid=ssid,
                           auth=(encryption, password),
                           channel=channel)
        except:
            print("WLan restart failed!")
            raise

        try:
            self.wlan.ifconfig(id=1,
                               config=('192.168.4.1',
                                       '255.255.255.0',
                                       '192.168.4.1',
                                       '192.168.4.1'))
        except:
            print("WLan ifconfig failed!")
            raise
        else:
            time.sleep(5)

    def _enable_client(self):
        print("wlan started")
        # Resolve mode to its numeric code
        mode = network.WLAN.STA
        print("wlan1")
        ssid = self.config.get_value('networking', 'network_config', 'ssid')
        password = self.config.get_value('networking', 'network_config', 'password')
        encryption = int(self.config.get_value('networking', 'network_config', 'encryption'))
        print("wlan1")
        if (not ssid) or (not password and encryption != 0):
            print("No WLan connection configured!")
            return

        try:
            self.wlan.deinit()
            time.sleep(1)
            self.configure_antenna()
            self.wlan.init(mode=mode)
        except:
            print("WLan restart failed!")
            raise
        print("wlan2")

        try:
            ifconfig = self.config.get_value('networking', 'network_config', 'ifconfig')
            if ifconfig == 'static':
                ipaddress = self.config.get_value('networking', 'network_config', 'ipaddress')
                subnet = self.config.get_value('networking', 'network_config', 'subnet')
                gateway = self.config.get_value('networking', 'network_config', 'gateway')
                dns = self.config.get_value('networking', 'network_config', 'dns')

                ip_config = (ipaddress, subnet, gateway, dns)
                self.wlan.ifconfig(id=0, config=ip_config)
            else:
                self.wlan.ifconfig(id=0, config='dhcp')
        except:
            print("WLan ifconfig failed!")
            raise
        print("wlan3")
        try:
            self.wlan.connect(ssid,
                              auth=(encryption, password),
                              timeout=5000)
        except:
            print("WLan connect failed!")
            print("SSID: {}, Enc: {}, PSK: {}".format(ssid,
                                                      encryption,
                                                      password))
            raise
        else:
            for i in range(10):
                if not self.wlan.isconnected():
                    time.sleep(1)
        print("fin")

    def enable_client(self):
        max_retries = 3
        for i in range(max_retries):
            try:
                self._enable_client()
            except:
                print("WLan connection failed, retry...")
            else:
                if self.wlan.mode() == network.WLAN.STA and self.wlan.isconnected():
                    return
