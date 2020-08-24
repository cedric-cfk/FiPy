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

    #def scan(self):
    #    return network.scan()

    def ap_enabled(self):
        if wlan is not None and wlan.mode() == network.WLAN.AP:
            return True
        return False

    def enable_ap(self):
        print("AP enabled--------------------------")
        global wlan
        if wlan is None:
            wlan = WLan(config)

        wlan.enable_ap()

    def is_connected(self):
        return netwok.is_connected()

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
        global netwok
        netwok = lte_M1()
    def lte_NB1(self):
        #global netwok
        #netwok = lte_NB1()
        raise ValueError('network lte_NB1 not jet implemented')
    def invalid(self):
        raise ValueError('invalid network configured in settings.json')

'''
    def log_data(self, data, _csv):
        print('   WLAN:   ', end = ' ')
        # log measured values, if possible
        if ( self.config.get_value('networking', 'wlan', 'enabled')
                and wlan.mode() == network.WLAN.STA
                and wlan.isconnected()
                and self.beep is not None):
            self.beep.add(data)
        log(_csv, data)
        """ Data on SD-Card """
        # print('   Data on SD-Card')
        if _csv is not None:
            # _csv.add_dict(data)
            _csv.add_data_didi(data, self.config.get_value('general', 'general', 'plt'), cycle)
        ms_main.log_data = perf.read_ms() - ms_ds_read

        # Trying to reconnect to wifi if possible:

        if ( self.config.get_value('networking', 'wlan', 'enabled')
                and self.beep is not None
                and ((not wlan.mode() == network.WLAN.STA) or
                (not wlan.isconnected()))
                ):
            log(_csv, "wlan is enabled but not connected.")
            until_wifi_reconnect -= 1
            log(_csv, "trying to reconnect in {} intervals".format(until_wifi_reconnect))
            if until_wifi_reconnect <= 0:
                log('wlan not connected try to reconnect')
                wdt.init(timeout=1*60*1000)
                enable_client()
                until_wifi_reconnect = self.config.get_value('general', 'general', 'until_wifi_reconnect')
                wdt.init(timeout=3*measurement_interval*1000)
        else:
            until_wifi_reconnect = self.config.get_value('general', 'general', 'until_wifi_reconnect')

    def start_network(self, wdt, rtc, _csv):
        log(_csv, "Start -> Starting measurement setup...")
        wdt.feed()
        try:
            if self.config.get_value('networking', 'wlan', 'enabled'):
                log(_csv, "WLan is enabled, trying to connect.")
                #print("calling ")
                self.enable_client()
                self.beep = logger.beep

                # add to time server
                if wlan.mode() == network.WLAN.STA and wlan.isconnected():
                    try:
                        rtc.ntp_sync("pool.ntp.org")
                    except:
                        pass
                    if (reset_causes[machine.reset_cause()]=='PWRON'
                                and not self.config.get_value('general', 'general', 'button_ap_enabled')):
                            enable_ap()
                            wdt.init(timeout=10*60*1000)
                            log(_csv, "starting Accesspoint after PowerOn for 10 min")
                    else:
                        return
                else:
                    log(_csv, "No network connection.")
                    if ((self.config.get_value('networking', 'accesspoint', 'enabled')
                            or _csv is None)
                             and not self.config.get_value('general', 'general', 'button_ap_enabled')
                            and reset_causes[machine.reset_cause()]=='PWRON'):
                        enable_ap()
                        wdt.init(timeout=5*60*1000)
                    else:
                        return
            else:
                log(_csv, "Measuring without network connection.")
                wlan.deinit()
                return

        except Exception as e:
            log(_csv, "Exception am Ende des Programms")
            print(e)
            log(_csv, "Error, dumping memory")
            log(_csv, sys.exc_info())
            micropython.mem_info(True)
            #machine.reset()

def log(_csv, message):
    if _csv is not None:
        _csv.log(message)
    else:
        print(message)
        '''
