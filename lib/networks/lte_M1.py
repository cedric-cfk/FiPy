from network import LTE
import time

class lte_M1():
    def is_connected(self):
        return self.lte.isconnected()

    def enable_client(self):
        self.lte = LTE()         # instantiate the LTE object
        self.lte.attach()        # attach the cellular modem to a base station
        print("trying to attach")
        while not self.lte.isattached():
            time.sleep(0.25)
        self.lte.connect()       # start a data session and obtain an IP address
        print("trying to connect")
        while not self.lte.isconnected():
            time.sleep(0.25)
        print("Connected to LTE")
