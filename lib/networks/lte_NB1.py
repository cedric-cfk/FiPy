from network import LTE
import _thread
import time
from machine import Timer

class lte_NB1():
    def is_connected(self):
        return self.lte.isconnected()

    def enable_client(self):
        self.lte = LTE()

        self.lte.disconnect()
        time.sleep(0.25)
        self.lte.dettach()
        time.sleep(0.25)

        self.lte.attach(band=8, apn="iot.1nce.net")
        while not self.lte.isattached():
            print("tryng to connecting")
            time.sleep(0.25)
        self.lte.connect()       # start a data session and obtain an IP address
        while not self.lte.isconnected():
            time.sleep(0.25)
        print(self.lte.isattached())
        print(self.lte.isconnected())
