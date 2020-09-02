from network import LTE
import _thread
import time
import usocket
from machine import Timer

class lte_M1():
    def __init__(self):
        self.lte = None

    def test(self):
        #print(usocket.getaddrinfo('pycom.io', 80))

        try:
            #print(socket.getaddrinfo('pycom.io', 80))
            s = usocket.socket()
            #s = ssl.wrap_socket(s)
            s.connect(usocket.getaddrinfo('www.google.com', 443)[0][-1])
            s.send(b"GET / HTTP/1.0\r\n\r\n")
            #print(s.recv(4096))
            s.close()
        except Exception as e:
            print("Error")
            print(e)
            self.lte.disconnect()
            self.lte.detach()


    def is_connected(self):
        return self.lte.isconnected()

    def enable_client(self):
        self.timeout = False
        self.timeoutLte = False
        alarm = Timer.Alarm(self.timeout_lte, 300)

        if self.lte == None:
            self.lte = LTE()         # instantiate the LTE object
        else:
            self.lte.deinit()

        print(self.lte.isconnected())
        print(self.timeoutLte)
        while not self.lte.isconnected() and not self.timeoutLte:
            self.lte.attach()        # attach the cellular modem to a base station
            print("trying to attach")
            t = Timer.Alarm(self.timeout_attaching, 60)
            while not self.lte.isattached() and not self.timeout:
                time.sleep(0.25)
            if not self.lte.isattached():
                self.lte.reset()
                continue
            t.cancel()
            self.timeout = False

            self.lte.connect()       # start a data session and obtain an IP address
            print("trying to connect")
            t = Timer.Alarm(self.timeout_connecting, 60)
            while not self.lte.isconnected() and not self.timeout:
                time.sleep(0.25)
            if not self.lte.isconnected():
                self.lte.reset()
                continue
            t.cancel()
            print("Connected to LTE")
        alarm.cancel()

    def timeout_attaching(self, alarm):
        self.timeout = True
        print("attaching Timeout")

    def timeout_connecting(self, alarm):
        self.timeout = True
        self.lte.detach()
        print("connecting Timeout")

    def timeout_lte(self, alarm):
        self.timeoutLte = True
        self.lte.deinit()
        print("could not connect to LTE M1!")
