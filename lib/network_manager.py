import machine
import sys
import micropython
import network

import logger
from config import Config
from networks.wlan import WLan
from networks.lte_M1 import lte_M1

netwok = None
wlan = None

class NetworkManager():

    def __init__(self, _config):
        global config
        config = _config

    def enable_client(self):
        #Initialising network defined by config
        if netwok is None:
            Switcher().indirect(config.get_value('networking', 'general', 'using'))
        print("starting client")
        netwok.enable_client()

    def is_connected(self):
        return netwok.is_connected()

    def scan(self):
        global wlan
        if wlan is None:
            wlan = WLan(config)
        return wlan.scan()

    def ap_enabled(self):
        if wlan is None or not wlan.is_inApMode():
            return False
        return True

    def enable_ap(self):
        print("AP enabled--------------------------")
        global wlan
        if wlan is None:
            wlan = WLan(config)
        wlan.enable_ap()

    def joined_ap_info(self):
        return wlan.joined_ap_info()

class Switcher(object):
    def indirect(self, method_name):
        method=getattr(self, method_name, lambda : self.invalid())
        return method()
    def wlan(self):
        global netwok
        netwok = WLan(config)
        global wlan
        wlan = netwok
    def lte_M1(self):
        global netwok, wlan
        netwok = lte_M1()
        wlan = None
    def lte_NB1(self):
        #global netwok, wlan
        #netwok = lte_NB1()
        #wlan = None
        raise ValueError('network lte_NB1 not jet implemented')
    def invalid(self):
        raise ValueError('invalid network configured in settings.json')
