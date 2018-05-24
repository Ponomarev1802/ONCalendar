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
import time
import telegram

class Alert:
    def __init__(self, text, attr, page):
        strdata = re.findall(r"{.*}", text)[0][1:-1]
        data = re.split(r"[\s:-]", strdata)

        now = datetime.datetime.now()
        self.dtime = {}

        try:
            self.dtime['minute'] = {"static": True, "value": int(data[1])}
        except:
            self.dtime['minute'] = {"static": True, "value": 0}

        try:
            self.dtime['hour'] = {"static": True, "value": int(data[0])}
        except:
            self.dtime['hour'] = {"static": False, "value": now.hour}

        try:
            self.dtime['day'] = {"static": True, "value": int(data[2])}
        except:
            self.dtime['day'] = {"static": False, "value": now.day}

        try:
            self.dtime['month'] = {"static": True, "value": int(data[3])}
        except:
            self.dtime['month'] = {"static": False, "value": now.month}

        try:
            self.dtime['year'] = {"static": True, "value": int(data[4])}
        except:
            self.dtime['year'] = {"static": False, "value": now.year}

        self.page = page
        self.text = text[len(strdata)+2:]

        self.next_call = datetime.datetime(self.dtime['year']['value'], self.dtime['month']['value'], self.dtime['day']['value'], self.dtime['hour']['value'], self.dtime['minute']['value'])

    def check_time(self):
        now = datetime.datetime.now()
        alert_time = datetime.datetime(self.dtime['year']['value'], self.dtime['month']['value'], self.dtime['day']['value'], self.dtime['hour']['value'], self.dtime['minute']['value'])
        if ((now - alert_time)<datetime.timedelta(0, 60, 0)) and ((now - alert_time)>datetime.timedelta(0, 0, 0)):
            print(now - alert_time)
            return True
        else:
            return False


    def alert(self):
        telegram.send_Message(self.text)

        if not (self.dtime["hour"]["static"]):
            next_call = self.next_call + datetime.timedelta(hours=1)
            self.dtime["hour"]["value"]= next_call.hour
            if (self.dtime["day"]["value"]!=next_call.day) and (not self.dtime["day"]["static"]):
                self.dtime["day"]["value"] = next_call.day
            if (self.dtime["month"]["value"]!=next_call.month) and (not self.dtime["month"]["static"]):
                self.dtime["month"]["value"] = next_call.month
            if (self.dtime["year"]["value"]!=next_call.year) and (not self.dtime["year"]["static"]):
                self.dtime["year"]["value"] = next_call.year
            return
        if not (self.dtime["day"]["static"]):
            next_call = self.next_call + datetime.timedelta(hours=24)
            self.dtime["day"]["value"]= next_call.day
            if (self.dtime["month"]["value"]!=next_call.month) and (not self.dtime["month"]["static"]):
                self.dtime["month"]["value"] = next_call.month
            if (self.dtime["year"]["value"]!=next_call.year) and (not self.dtime["year"]["static"]):
                self.dtime["year"]["value"] = next_call.year
            return
        if not (self.dtime["month"]["static"]):
            if (self.next_call.month == 12):
                next_call = datetime.datetime(self.next_call.year+1, 1, self.next_call.day, self.next_call.hour, self.next_call.minute)
            else:
                next_call = datetime.datetime(self.next_call.year, self.next_call.month+1, self.next_call.day, self.next_call.hour, self.next_call.minute)
            self.dtime["month"]["value"]= next_call.month
            if (self.dtime["year"]["value"]!=next_call.year) and (not self.dtime["year"]["static"]):
                self.dtime["year"]["value"] = next_call.year
            return

    def update(self):
        self.next_call = datetime.datetime(self.dtime['year']['value'], self.dtime['month']['value'],
                                           self.dtime['day']['value'], self.dtime['hour']['value'],
                                           self.dtime['minute']['value'])
        if (datetime.datetime.now()>self.next_call):
            return False
        else:
            return True



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

def get_alarms():
    pages = ON_request("https://www.onenote.com/api/v1.0/me/notes/pages?top=10")
    print(pages['value'])
    alarms = []
    for page in pages['value']:
        content = ON_request(page["self"] + "/content")
        print("Обращение к странице "+page['title'])
        for elems in (pq(content).items("[data-tag]")):
            if ('highlight' in elems.attr("data-tag")):
                print(elems.text() + " in " + page["title"])
                alarms.append(Alert(elems.text(), elems.attr("data-tag"), page['title']))
    return alarms


def start_alerts():
    while True:
        last_update_time = datetime.datetime.now()
        alarms = get_alarms()
        print("Массив объектов: ")
        for elems in alarms:
            print (elems.text+" in "+ elems.page)
        print("---------------------")
        while True:
            for elem in alarms:
                if (elem.check_time()):
                    elem.alert()
                    print(elem.next_call)
                    print(elem.text)
                    print(str(elem.dtime['hour']['value'])+":"+str(elem.dtime['minute']['value'])+" "+str(elem.dtime['day']['value'])+"-"+str(elem.dtime['month']['value'])+"-"+str(elem.dtime['year']['value']))
                    print("---------------------")
                    if (not elem.update()):
                        print("Удаляем объект")
                        alarms.remove(elem)
            time.sleep(60)
            if ((datetime.datetime.now() - last_update_time) > datetime.timedelta(0, 3600, 0)):
                break
start_alerts()



