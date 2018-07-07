import requests
from lxml import html

class Proxifier:
    def __init__(self):
        self.BASE_URL = "https://free-proxy-list.net/"
        self.XPATH_IP = "//*[(@id = \"proxylisttable\")]//td[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]/text()"
        self.XPATH_PORT = "//*[(@id = \"proxylisttable\")]//td[(((count(preceding-sibling::*) + 1) = 2) and parent::*)/text()]"
        self.PROXIES = []
    
    def parse_proxy(self, IP, PORT):
        return {
            "ip": IP,
            "port": PORT,
            "used": False
        }
    
    def parse_proxies(self, IPs, PORT):
        return [
            self.parse_proxy(IPs[x], PORT[x]) 
            for x in range(len(IPs))
        ]
    
    def load_proxies(self):
        req = requests.get(self.BASE_URL)
        tree = html.fromstring(req.content)
        ips = tree.xpath(self.XPATH_IP)
        ports = tree.xpath(self.XPATH_PORT)
        return self.parse_proxies(ips, ports)

    def get_new_proxy(self):
        proxy = self.PROXIES[0]
        del self.PROXIES[0]
        return "http://%s:%s" % (proxy.get("ip"), proxy.get("port"),)

    def get_through_proxy(self, url, **kwargs):
        return requests.get(url, proxies={
            "http": self.get_new_proxy()
        },
         **kwargs)