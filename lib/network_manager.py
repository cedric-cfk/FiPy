from config import Config
from networks.wlan import WLan

class NetworkManager():

    def __init__(self, config):
        self.config = config
        self.network = WLan(config)
        #Starting network defined by config

    def enable_client(self):
        self.network._enable_client()

    def scan(self):
        return self.network.scan()

    def configure_antenna(self):
        self.network.configure_antenna()

    def enable_ap(self):
        self.network.enable_ap()
