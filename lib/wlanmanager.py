import binascii
import machine
import network
from network import LTE
import time
import sys

from config import Config

class WLanManager():

    def __init__(self, config):
        self.config = config
        self.wlan = network.WLAN()
        self.lte = LTE()

    def configure_antenna(self):
        # https://community.hiveeyes.org/t/signalstarke-des-wlan-reicht-nicht/2541/11
        # https://docs.pycom.io/firmwareapi/pycom/network/wlan/

        antenna_external = self.config.get_value('networking', 'wlan', 'antenna_external')
        print("Using Antenna: ", antenna_external)
        if antenna_external:
            antenna_pin = self.config.get_value('networking', 'wlan', 'antenna_pin')
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
        self.config.set_value('networking', 'wlan', 'available', ssids)
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

    def isconnected(self):
        return (self.wlan.mode() == network.WLAN.STA and self.wlan.isconnected()) or self.lte.isconnected()

    def disconnect_lte(self):
        print("starting dettaching")
        self.lte.disconnect()
        print("Disconnected")
        self.lte.dettach()
        print("LTE disconnected")

    def enable_lte(self):
        lte = LTE()         # instantiate the LTE object
        lte.attach()        # attach the cellular modem to a base station
        print("trying to attach")
        while not lte.isattached():
            time.sleep(0.25)
        lte.connect()       # start a data session and obtain an IP address
        print("trying to connect")
        while not lte.isconnected():
            time.sleep(0.25)
        print("Connected to LTE")

    def _enable_client(self):
        print("Connecting to WLAN")
        # Resolve mode to its numeric code
        mode = network.WLAN.STA

        ssid = self.config.get_value('networking', 'wlan', 'ssid')
        password = self.config.get_value('networking', 'wlan', 'password')
        encryption = int(self.config.get_value('networking', 'wlan', 'encryption'))

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


        try:
            ifconfig = self.config.get_value('networking', 'wlan', 'ifconfig')
            if ifconfig == 'static':
                ipaddress = self.config.get_value('networking', 'wlan', 'ipaddress')
                subnet = self.config.get_value('networking', 'wlan', 'subnet')
                gateway = self.config.get_value('networking', 'wlan', 'gateway')
                dns = self.config.get_value('networking', 'wlan', 'dns')

                ip_config = (ipaddress, subnet, gateway, dns)
                self.wlan.ifconfig(id=0, config=ip_config)
            else:
                self.wlan.ifconfig(id=0, config='dhcp')
        except:
            print("WLan ifconfig failed!")
            raise

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
