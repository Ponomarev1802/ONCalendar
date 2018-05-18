# -*- coding: utf-8 -*-
import requests
import json
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import re
import datetime

class Alert:
    def __init__(self, text, attr, page):
        strdata = re.findall(r"{.*}", text)[0][1:-1]
        data = re.split(r"[\s:-]", strdata)
        self.hours = data[0]
        self.mins = data[1]
        self.day = data[2]
        self.month = data[3]
        self.year = data[4]
        self.page = page
        self.text = text[len(data):]
        self.date = datetime.date(self.year, self.month, self.day)
        self.time = datetime.time(self.hours, self.mins)
        self.last_call = 0
    def print(self):
        print("hours: " + self.hours + "mins: " + self.mins + "date: " + self.day + "month: " + self.month + "year: " + self.year)


def sign_in():
    driver = webdriver.Chrome('./chromedriver.exe')
    driver.get(
        "https://login.live.com/oauth20_authorize.srf?response_type=code&client_id=7ec7be29-a871-4cf3-861e-52c7a4efe95f&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&scope=office.onenote wl.signin wl.offline_access")
    try:
        success_sign_in = WebDriverWait(driver, 60).until(EC.title_is(""))
    except:
        print('Истек срок ожидания, попробуйте снова')
        exit()

    if success_sign_in:
        url = driver.current_url
        code = url[url.rfind("code=") + 5:]
        f = open("./data.txt", "w")
        f.write(code)
        f.close()
        driver.close()

def get_access_token():
    f = open("./data.txt", "r")
    code = f.read()
    f.close()
    uri = "https://login.live.com/oauth20_token.srf"
    data = {"grant_type": "authorization_code",
            "client_id": "7ec7be29-a871-4cf3-861e-52c7a4efe95f",
            "code": code,
            "redirect_uri": "https://login.microsoftonline.com/common/oauth2/nativeclient"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(uri, headers=headers, data=data)
    answer = eval(r.text)
    print(answer["access_token"])
    f = open('./access_token.txt', 'w')
    f.write(answer["access_token"])
    f.close()
    f = open('./refresh_token.txt', 'w')
    f.write(answer["refresh_token"])
    f.close()

def refresh_access_token():
    f = open("./data.txt", "r")
    code = f.read()
    f.close()
    f = open('./refresh_token.txt', 'r')
    refresh_token = f.read()
    f.close()
    uri = "https://login.live.com/oauth20_token.srf"
    data = {"grant_type": "refresh_token",
            "client_id": "7ec7be29-a871-4cf3-861e-52c7a4efe95f",
            "code": code,
            "redirect_uri": "https://login.microsoftonline.com/common/oauth2/nativeclient",
            "refresh_token": refresh_token
            }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(uri, headers=headers, data=data)
    print(r.text)
    answer = eval(r.text)
    if answer["access_token"]:
        f = open('./access_token.txt', 'w')
        f.write(answer["access_token"])
        f.close()
        f = open('./refresh_token.txt', 'w')
        f.write(answer["refresh_token"])
        f.close()
def ON_request(request):
    answer = {"error": "does not init"}
    while ("error" in answer):
        f = open('./access_token.txt', 'r')
        access_token = f.read()
        f.close()
        headers = {"Authorization": "bearer " + access_token}
        r = requests.get(request, headers=headers)
        if ("text/html" in (r.headers)["Content-Type"]):
            return r.text
        answer = (json.loads(r.text))
        if ("error" in answer):
            refresh_access_token()
    return answer

pages = ON_request("https://www.onenote.com/api/v1.0/me/notes/pages?top=10")

print(pages)
for page in pages['value']:
    content = ON_request(page["self"]+"/content")
    for elems in (pq(content).items("[data-tag]")):
        if ('highlight' in elems.attr("data-tag")):
            print(elems.text()+" in "+page["title"])
            alarm = Alert(elems.text(), elems.attr("data-tag"), page['title'])
            alarm.print()

