import requests
import telepot
from urllib3.contrib.socks import SOCKSProxyManager



def send_Message(text):
    proxy_url = "socks5://s5.open44fz.ru:20180"

    telepot.api._pools = {
        'default': SOCKSProxyManager(proxy_url=proxy_url, username="advantage", password="Task!Work", num_pools=3, maxsize=10, retries=False, timeout=30),
    }
    telepot.api._onetime_pool_spec = (
    SOCKSProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))
    token = "579862720:AAGjj9zdAuneASuenwo7eFLJN6JkKljMgSM"
    TelegramBot = telepot.Bot(token)
    TelegramBot.sendMessage("165958974", text)
