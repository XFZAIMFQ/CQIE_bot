import requests

from module.tool.encryptedPassword import DES_encryption
from module.tool.outputLog import log


def get_smartCampus_Cookie(username, password):
    url = 'http://i.cqie.edu.cn/'
    response = requests.get(url, allow_redirects=False)
    smartCampus_Cookie = response.headers['Set-Cookie'].split(';')[0]

    url = "http://a.cqie.edu.cn/cas/login?service=http%3A%2F%2Fi.cqie.edu.cn%2Fportal_main%2FtoPortalPage"
    response = requests.get(url, allow_redirects=False)
    a_smartCampus_Cookie = response.headers['Set-Cookie'].split(';')[0]

    encrypted_pwd = DES_encryption(password)

    url = (f"http://a.cqie.edu.cn/cas/login;jsessionid={a_smartCampus_Cookie.split('=')[1]}?"
           f"service=http%3A%2F%2Fi.cqie.edu.cn%2Fportal_main%2FtoPortalPage")
    headers = {
        "Cookie": a_smartCampus_Cookie
    }
    # 设置请求的数据参数
    data = {
        # 在这里添加需要发送的表单数据
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
    requests_post = requests.post(url, headers=headers, data=data, allow_redirects=False)

    location = requests_post.headers['Location']
    headers = {
        "Cookie": smartCampus_Cookie
    }
    requests_get = requests.get(url=location, headers=headers, allow_redirects=False)

    location = requests_get.headers['Location']
    headers = {
        "Cookie": smartCampus_Cookie
    }
    requests_get = requests.get(url=location, headers=headers, allow_redirects=False)
    if requests_get.status_code == 200:
        log.info(f'获取智慧校园平台Cookie成功')
        return smartCampus_Cookie
