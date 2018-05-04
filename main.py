# -*- coding: utf-8 -*-
import requests
import json
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq


def sign_in():
    driver = webdriver.Chrome('./chromedriver.exe')
    driver.get(
        "https://login.live.com/oauth20_authorize.srf?response_type=code&client_id=7ec7be29-a871-4cf3-861e-52c7a4efe95f&redirect_uri=https://login.microsoftonline.com/common/oauth2/nativeclient&scope=office.onenote_update")
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

def refresh_access_token():
    f = open("./data.txt", "r")
    code = f.read()
    f.close()
    f = open('./access_token.txt', 'r')
    access_token = f.read()
    f.close()
    uri = "https://login.live.com/oauth20_token.srf"
    data = {"grant_type": "refresh_token",
            "client_id": "7ec7be29-a871-4cf3-861e-52c7a4efe95f",
            "code": code,
            "redirect_uri": "https://login.microsoftonline.com/common/oauth2/nativeclient",
            "refresh_token": access_token
            }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(uri, headers=headers, data=data)
    print(r.text)
    answer = eval(r.text)
    f = open('./access_token.txt', 'w')
    f.write(answer["access_token"])
    f.close()


sign_in()
get_access_token()
f = open ('./access_token.txt', 'r')
access_token = f.read()
f.close()
headers={"Authorization": "bearer " + access_token}
r = requests.get("https://www.onenote.com/api/v1.0/me/notes/pages", headers=headers)
answer = (json.loads(r.text))
print(answer)
print(answer["value"][0]["self"])
r = requests.get(answer["value"][0]["self"]+"/content", headers=headers)
answer = (r.text)
print(pq(answer).find("[data-tag='highlight']"))