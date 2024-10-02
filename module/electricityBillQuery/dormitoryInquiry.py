import base64
import hashlib
import time
import requests
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad
from bs4 import BeautifulSoup

from module.tool.encryptedPassword import DES_encryption
from module.tool.outputLog import log

'''
此文件是用于自动获取寝室
'''


def passworDencryption(password):
    a = hashlib.md5(password.encode()).hexdigest()
    if len(a) > 5:
        a = a[:5] + "a" + a[5:]

    if len(a) > 10:
        a = a[:10] + "b" + a[10:]

    a = a[:-2]

    return a


def get_DormCookie_direct(username, password):
    url = 'http://bd.cqie.edu.cn/index'

    response = requests.get(url)
    cookie = response.headers['Set-Cookie'].split(';')[0]
    # print(cookie)

    url = 'http://bd.cqie.edu.cn/website/login'
    headers = {
        'Cookie': cookie
    }
    data = {
        'uname': username,
        'pd_mm': passworDencryption(password)
    }
    response = requests.post(url, headers=headers, data=data)
    # print(response.text)

    if 'error' in response.text:
        # print('获取DormCookie失败')
        log.info('获取DormCookie失败')
        return False
    return cookie


def get_DormCookie_wisdomplatform(username, password):
    url = "http://a.cqie.edu.cn/cas/login?service=http%3A%2F%2Fbd.cqie.edu.cn%2Fcas"
    response = requests.get(url)
    cookie = response.headers['Set-Cookie'].split(';')[0]
    # print(cookie)

    encrypted_pwd = DES_encryption(password)

    url = f"http://a.cqie.edu.cn/cas/login;jsessionid={cookie.split('=')[1]}?service=http%3A%2F%2Fbd.cqie.edu.cn%2Fcas"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Length": "141",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookie,
        "Host": "a.cqie.edu.cn",
        "Origin": "http://a.cqie.edu.cn",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://a.cqie.edu.cn/cas/login?service=http%3A%2F%2Fbd.cqie.edu.cn%2Fcas",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }
    data = {
        "username": f"{username}",
        "password": f"{encrypted_pwd}",
        "authCode": "",
        "lt": "abcd1234",
        "execution": "e1s1",
        "_eventId": "submit",
        "isQrSubmit": "false",
        "qrValue": "",
        "isMobileLogin": "false"
    }
    response = requests.post(url, headers=headers, data=data, allow_redirects=False)
    if response.status_code != 302:
        return False

    location_url = response.headers['Location']
    response = requests.get(url=location_url, allow_redirects=False)
    if response.status_code != 302:
        return False

    location_url = response.headers['Location']
    cookie = response.headers['Set-Cookie'].split(';')[0]
    response = requests.get(url=location_url, headers={'Cookie': cookie}, allow_redirects=False)
    if response.status_code != 302:
        return False

    return cookie


# 获取寝室
def get_Bedroom(cookie):
    current_timestamp = int(time.time() * 1000)  # 将秒转换为毫秒
    url = f'http://bd.cqie.edu.cn/content/menu/stu/welcome/xxcx?_t_s_={current_timestamp}'
    headers = {
        'Cookie': cookie,
    }
    response = requests.get(url, headers=headers)
    # print(response.text)  # 打印响应内容
    soup = BeautifulSoup(response.text, "html.parser")
    find_all = soup.find_all("div", class_="view-text")
    dormitoryInformation = find_all[0].text.strip()
    # print(dormitoryInformation)

    if dormitoryInformation == '未交清学杂费不允许查看！':
        return False
    dormitoryInformations = dormitoryInformation.split("\u2002")

    bedroomBuilding = dormitoryInformations[0]  # 寝室楼
    bedroomID = dormitoryInformations[3]  # 寝室号
    return bedroomBuilding, bedroomID


def get_ADormAutomatically(username, password):
    cookie = get_DormCookie_wisdomplatform(username, password)
    return get_Bedroom(cookie)
