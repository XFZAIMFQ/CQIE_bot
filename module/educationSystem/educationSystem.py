import base64

import requests
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad

from module.educationSystem.course import get_currentSemester
from module.tool.encryptedPassword import DES_encryption
from module.tool.outputLog import log


def getEducationSystem_Cookie(username, password):
    # 设置请求的URL和请求头
    url = 'http://jw.cqie.edu.cn/cqgccaslogin'

    # 发送GET请求
    response = requests.get(url, allow_redirects=False)
    educationSystem_Cookie = response.headers['Set-Cookie'].split(';')[0]
    location = response.headers['Location']
    # print('educationSystem_Cookie:', educationSystem_Cookie)

    url = location
    response = requests.get(url, allow_redirects=False)
    authenticate_cookie = response.headers['Set-Cookie'].split(';')[0]
    # print('authenticate_cookie:', authenticate_cookie)

    url = f'http://a.cqie.edu.cn/cas/login;jsessionid={authenticate_cookie.split("=")[1]}?' \
          f'service=http%3A%2F%2Fa.cqie.edu.cn%2Fcas%2Foauth2.0%2FcallbackAuthorize&' \
          f'originalRequestUrl=http%3A%2F%2Fa.cqie.edu.cn%2Fcas%2Foauth2.0%2Fauthorize%3Fclient' \
          f'_id%3Dcastestjw%26redirect_uri%3Dhttp%253A%252F%252Fjw.cqie.edu.cn%253A80%252Fcqgccas' \
          f'login%26response_type%3Dcode%26scope%3Dsimple%26state%3Dcqgc'
    headers = {
        "Cookie": authenticate_cookie
    }
    response = requests.get(url, headers=headers, allow_redirects=False)
    # print(response.status_code)

    encrypted_pwd = DES_encryption(password)

    # 设置请求的URL和请求头
    url = 'http://a.cqie.edu.cn/cas/login?service=http%3A%2F%2Fa.cqie.edu.cn%2Fcas%2Foauth2.0%2FcallbackAuthorize&' \
          'originalRequestUrl=http%3A%2F%2Fa.cqie.edu.cn%2Fcas%2Foauth2.0%2Fauthorize%3Fclient_id%3Dcastestjw%26redirec' \
          't_uri%3Dhttp%253A%252F%252Fjw.cqie.edu.cn%253A80%252Fcqgccaslogin%26response_type%3Dcode%26scope%3Dsimple%26state%3Dcqgc'
    headers = {
        'Cookie': authenticate_cookie
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
    # 发送POST请求
    requests_post = requests.post(url, headers=headers, data=data, allow_redirects=False)

    location = requests_post.headers['Location']
    CASTGC = 'CASTGC="' + requests_post.headers['Set-Cookie'].split('CASTGC="')[1].split(';')[0]

    # print(location)
    # print(CASTGC)

    url = location
    headers = {
        'Cookie': f'{authenticate_cookie}; {CASTGC}',
    }
    response = requests.get(url, headers=headers, allow_redirects=False)
    location = response.headers['Location']
    # print(location)

    url = location
    headers = {
        'Cookie': educationSystem_Cookie
    }
    response = requests.get(url, headers=headers, allow_redirects=False)
    # location = response.headers['Location']
    # print(location)

    return educationSystem_Cookie


def automaticAcquisition_educationSystem_Cookie(qq_ID, database):
    user_password = database.get_UserPassword(qq_ID)
    if user_password:
        studentID = user_password[0]
        password = user_password[1]
    else:
        # print('用户:', qq_ID, '未绑定智慧校园平台 无法自动获取 educationSystem_Cookie')
        log.info(f'用户: {qq_ID} 未绑定智慧校园平台 无法自动获取 educationSystem_Cookie')
        return False

    # print('正在从数据库查询', '用户:', qq_ID, ' educationSystem_Cookie')
    log.info(f'正在从数据库查询 用户: {qq_ID} educationSystem_Cookie')
    sql = "SELECT educationSystem_Cookie FROM user_cookie_tab WHERE QQ = %s;"
    date = (qq_ID)
    result = database.execution(sql, date)  # 查询数据库中是否存在 educationSystem_Cookie
    if result and result[0][0] is not None:
        # print('已从数据库查询到', '用户:', qq_ID, ' educationSystem_Cookie')
        log.info(f'已从数据库查询到 用户: {qq_ID} educationSystem_Cookie')
        educationSystem_Cookie = result[0][0]
        semester = get_currentSemester(educationSystem_Cookie)  # 检测 Cookie是否过期
        if semester:
            # print('数据库', '用户:', qq_ID, ' educationSystem_Cookie 有效')
            log.info(f'数据库 用户 {qq_ID} educationSystem_Cookie 有效')
            return educationSystem_Cookie
        else:
            # print('数据库', '用户:', qq_ID, ' educationSystem_Cookie 无效')
            log.info(f'数据库 用户: {qq_ID} educationSystem_Cookie 无效')
    else:
        # print('未从数据库查询到', '用户:', qq_ID, ' educationSystem_Cookie')
        log.info(f'未从数据库查询到 用户:  {qq_ID} educationSystem_Cookie')
    if not result:
        sql = "INSERT INTO user_cookie_tab (educationSystem_Cookie,QQ) values (%s,%s);"
    else:
        sql = "UPDATE user_cookie_tab SET educationSystem_Cookie = %s WHERE QQ = %s ;"

    # print('自动获取 ', '用户:', qq_ID, ' activity_Cookie ')
    log.info(f'自动获取 用户: {qq_ID} activity_Cookie ')
    educationSystem_Cookie = getEducationSystem_Cookie(studentID, password)  # 获取最新的Cookie
    if not educationSystem_Cookie:
        # print('自动获取 ', '用户:', qq_ID, ' activity_Cookie 失败')
        log.info(f'自动获取 用户: {qq_ID} activity_Cookie 失败')
        return False
    # insert = "insert into user_cookie_tab (QQ,educationSystem_Cookie) values (%s,%s)"
    date = (educationSystem_Cookie, qq_ID)
    execution = database.execution(sql, date)
    if execution:
        # print('数据库更新 ', '用户:', qq_ID, ' educationSystem_Cookie 成功')
        log.info(f'数据库更新  用户: {qq_ID} educationSystem_Cookie 成功')
        return educationSystem_Cookie
    else:
        # print('数据库更新 ', '用户:', qq_ID, ' educationSystem_Cookie 失败')
        log.info(f'数据库更新 用户: {qq_ID} educationSystem_Cookie 失败')
        return False
