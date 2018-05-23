import requests
import telepot
import urllib3



def send_Message(text):
    proxy_url = "http://static.163.141.4.46.clients.your-server.de:3128"

    telepot.api._pools = {
        'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
    }
    telepot.api._onetime_pool_spec = (
    urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))
    token = "579862720:AAGjj9zdAuneASuenwo7eFLJN6JkKljMgSM"
    TelegramBot = telepot.Bot(token)
    TelegramBot.sendMessage("165958974", text)
