import machine
import sys
import micropython
import network

import logger
from config import Config
from networks.wlan import WLan

class NetworkManager():

    def __init__(self, config):
        self.config = config
        self.network = None
        self.wlan = None

    def enable_client(self):
        #Initialising network defined by config
        if self.network is None:
            s = Switcher()
            self.network = s.indirect(self.config.get_value('networking', 'general', 'using'), self.config)
        print("starting client")
        self.network.enable_client()

    #def scan(self):
    #    return self.network.scan()

    def enable_ap(self):
        print("AP enabled--------------------------")
        if self.wlan is None:
            self.wlan = WLan(self.config)

        self.wlan.enable_ap()

    def is_connected(self):
        return self.network.is_connected()

class Switcher(object):
    def indirect(self, method_name, config):
        self.config = config
        method=getattr(self, method_name, lambda : self.invalid())
        return method()
    def wlan1(self):
        return WLan(self.config)
    def wlan2(self):
        return WLan(self.config)
    def invalid(self):
        raise ValueError('invalid network configured in settings.json')

'''
    def log_data(self, data, _csv):
        print('   WLAN:   ', end = ' ')
        # log measured values, if possible
        if ( self.config.get_value('networking', 'wlan', 'enabled')
                and self.wlan.mode() == network.WLAN.STA
                and self.wlan.isconnected()
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
                and ((not self.wlan.mode() == network.WLAN.STA) or
                (not self.wlan.isconnected()))
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
                if self.wlan.mode() == network.WLAN.STA and self.wlan.isconnected():
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
                self.wlan.deinit()
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
