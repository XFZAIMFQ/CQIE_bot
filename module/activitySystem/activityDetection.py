import json
import random
import re

import requests

from module.tool.encryptedPassword import DES_encryption
from module.tool.outputLog import log


# 获取活动查询的Cookie
def get_Activity_Cookie(username, password):
    url = 'http://a.cqie.edu.cn/cas/login'
    params = {
        'service': 'http://xs.cqie.edu.cn/xg/ssoLogin.jsp?rdPath=backstageNoNav.jsp?loadMainPage=spring:allhdzyz/FromQXHDMHView'
    }
    response = requests.get(url, params=params)
    # 根据需要处理响应内容
    cookie = response.headers['Set-Cookie'].split(';')[0]
    # 加密密码
    encrypted_pwd = DES_encryption(password)

    url = f'http://a.cqie.edu.cn/cas/login;jsessionid={cookie.split("=")[1]}'
    params = {
        'service': 'http://xs.cqie.edu.cn/xg/ssoLogin.jsp?rdPath=backstageNoNav.jsp?loadMainPage=spring:allhdzyz/FromQXHDMHView'
    }
    headers = {
        'Cookie': cookie
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
    response = requests.post(url, params=params, headers=headers, data=data, allow_redirects=False)

    if response.status_code == 200:
        # print("密码错误")
        return False

    Location = response.headers['Location']
    Set_Cookie = response.headers['Set-Cookie']

    url = Location
    response = requests.get(url, allow_redirects=False)

    Cookie = response.headers['Set-Cookie'].split(";")[0]
    Location = response.headers['Location']

    url = "http://xs.cqie.edu.cn/xg/acp/system/login?_rd=100&rdPath=backstageNoNav.jsp?loadMainPage=spring:allhdzyz/FromQXHDMHView"
    headers = {
        "Cookie": Cookie
    }
    response = requests.post(url, headers=headers)

    # print(response.status_code)
    return Cookie


# 活动的详情查询
def get_activityDetails_Query(Cookie, dataId):
    """
    活动的详情查询

    Parameters:
        param1 - 获取者Cookie
        param2 - 需获取活动ID

    Returns:
        活动的各项属性,学号,活动属性

    Raises:
        KeyError - raises an exception
    """
    randomNumber1 = round(random.uniform(0, 1), 16)
    randomNumber2 = round(random.uniform(0, 1), 16)
    url = f'http://xs.cqie.edu.cn/xg/allhdzyz/FromHDSQView?random={randomNumber1}&random={randomNumber2}'
    headers = {
        'Cookie': Cookie,
    }
    data = {
        'dataId': dataId
    }

    response = requests.post(url, headers=headers, data=data, allow_redirects=False)

    with open('activityDetailsQuery.html', 'w', encoding='utf-8') as fp:
        fp.write(response.text)

    if (response.status_code == 302):
        # print("活动ID: ", dataId, " 详情查询失败 ", "status_Code: ", response.status_code, " 请检测Cookie是否失效")
        log.info(f"活动ID < {dataId} > 详情查询失败 status_Code: <{response.status_code}> 请检测Cookie是否失效")
        return False

    # 定义匹配模式
    pattern = r'var data = ({.*?});'
    # 使用正则表达式匹配
    match = re.search(pattern, response.text)
    # 获取data
    if not match:
        # print("活动ID: ", dataId, " 获取data失败 ", "请检测活动ID是否有效")
        log.info(f"活动ID <{dataId}> 获取data失败 请检测活动ID是否有效")
        return False
    data = match.group(1)
    data = data.replace('"[', '[')
    data = data.replace(']"', ']')
    data = data.replace('\\"', '\"')
    data = data.replace('\\r\\n', '\\n')
    data = data.replace('\\t', '\\t')
    # 解析data
    loads_data = json.loads(data)

    pattern = r"var hdsxbj\s*=\s*'(.*?)';"
    match = re.search(pattern, response.text)
    if not match:
        # print("活动ID: ", dataId, " 获取hdsxbj失败 ", "请检测活动ID是否有效")
        log.info(f"活动ID <{dataId}> 获取hdsxbj失败 请检测活动ID是否有效")
        return False
    hdsxbj = match[0].split("'")[1].split("'")[0]

    pattern = r"var xh\s*=\s*'(.*?)'"
    match = re.search(pattern, response.text)
    if not match:
        # print("活动ID: ", dataId, " 获取xh失败 ", "请检测活动ID是否有效")
        log.info(f"活动ID <{dataId}> 获取xh失败 请检测活动ID是否有效")
        return False
    xh = match[0].split("'")[1].split("'")[0]

    return loads_data, xh, hdsxbj


# 活动查询 使用于多页
def get_activityQuery_Query(Cookie, type, curPage):
    """ 活动查询 使用于多页 """
    url = 'http://xs.cqie.edu.cn/xg/allhdzyz/queryQXHDMH'
    params = {
        'random': f'{round(random.uniform(0, 1), 16)}',
        'curPage': curPage,
        'type': type,
        'hdlb': '',
        'hdxn': '',
        'hdxq': ''
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Cookie': Cookie,
        'X-Requested-With': 'XMLHttpRequest'
    }
    response = requests.get(url, params=params, headers=headers, allow_redirects=False)

    if response.status_code == 302:
        # print("活动检测失败, 请检测Cookie是否过期")
        log.info('get_activityQuery_Query 活动检测失败, 请检测Cookie是否过期')
        return False

    Content_Type = response.headers.get('Content-Type')
    if Content_Type is not None and 'application/json' in Content_Type:
        return json.loads(response.text)
    else:
        # print("活动检测失败, 请检测Cookie是否过期")
        log.info('get_activityQuery_Query 活动检测失败, 请检测Cookie是否过期')
        return False


# 活动查询 获取单页
def get_activityQuery_Get(Cookie, type):
    url = "http://xs.cqie.edu.cn/xg/allhdzyz/getHDbyPage"
    params = {
        "random": f'{round(random.uniform(0, 1), 16)}',
        "type": f'{type}',
        "hdlb": "",
        "hdxn": "",
        "hdxq": ""
    }

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Cookie": Cookie,
        "X-Requested-With": "XMLHttpRequest"
    }

    response = requests.get(url, params=params, headers=headers, allow_redirects=False)
    if response.status_code == 302:
        # print('activityQuery_get 请求失败')
        log.info('activityQuery_get 请求失败')
        return False

    Content_Type = response.headers.get('Content-Type')
    if Content_Type is not None and 'application/json' in Content_Type:
        return json.loads(response.text)
    else:
        # print("活动检测失败, 请检测Cookie是否过期")
        log.info("活动检测失败, 请检测Cookie是否过期")
        return False


# 自动获取activity_Cookie
def automaticallyFetchActivity_Cookie(qq_ID, database):
    """ 自动获取activity_Cookie """
    user_password = database.get_UserPassword(qq_ID)
    if user_password:
        studentID = user_password[0]
        password = user_password[1]
    else:
        # print('用户:', qq_ID, '未绑定智慧校园平台,无法自动获取activity_Cookie')
        log.info(f'用户 <{qq_ID}> 未绑定智慧校园平台,无法自动获取activity_Cookie')
        return False

    # print('正在从数据库查询', '用户:', qq_ID, ' activity_Cookie')
    log.info(f'正在从数据库查询 用户 <{qq_ID}> activity_Cookie')
    query = "SELECT activity_Cookie FROM user_cookie_tab where QQ = %s ;"
    data = (qq_ID,)
    result = database.execution(query, data)  # 查询是否存在旧的activity_Cookie
    if result and result[0][0] is not None:
        # print('已从数据库查询到', '用户:', qq_ID, ' activity_Cookie')
        log.info(f'已从数据库查询到 用户 <{qq_ID}> activity_Cookie')
        activity_Cookie = result[0][0]  # 从数据库中取出cookie
        activity_query = get_activityQuery_Query(activity_Cookie, 1, 1)  # 随便查询一个活动
        if activity_query:
            # print('数据库 ', '用户:', qq_ID, ' activity_Cookie 有效')
            log.info(f'数据库 用户 <{qq_ID}> activity_Cookie 有效')
            return activity_Cookie
        else:
            # print('数据库 ', '用户:', qq_ID, ' activity_Cookie 无效')
            log.info('数据库 用户 <{qq_ID}> activity_Cookie 无效')
    else:
        # print('未从数据库查询到', '用户:', qq_ID, ' activity_Cookie')
        log.info(f'未从数据库查询到 用户 <{qq_ID}> activity_Cookie')

    if not result:
        sql = "INSERT INTO user_cookie_tab (activity_Cookie,QQ) values (%s,%s);"
    else:
        sql = "UPDATE user_cookie_tab SET activity_Cookie = %s WHERE QQ = %s ;"

    # print('自动获取 ', '用户:', qq_ID, ' activity_Cookie ')
    log.info(f'自动获取 用户 <{qq_ID}> activity_Cookie ')
    activity_cookie = get_Activity_Cookie(username=studentID, password=password)
    if activity_cookie:
        # print('已自动获取 ', '用户:', qq_ID, ' activity_Cookie')
        log.info(f'已自动获取 用户 <{qq_ID}> activity_Cookie')
        # insert = "INSERT INTO user_cookie_tab (QQ,activity_Cookie) values (%s,%s);"
        data = (activity_cookie, qq_ID)
        result = database.execution(sql, data)
        if result:
            # print('更新用户数据库 ', '用户:', qq_ID, ' activity_Cookie 信息成功')
            log.info(f'更新用户数据库 用户 <{qq_ID}> activity_Cookie 信息成功')
            return activity_cookie
        else:
            # print('更新用户数据库 ', '用户:', qq_ID, ' activity_Cookie信息失败')
            log.info(f'更新用户数据库 用户 <{qq_ID}> activity_Cookie信息失败')
            return False
    else:
        # print('自动获取 ', '用户:', qq_ID, ' activity_cookie 失败')
        log.info(f'自动获取 用户 {qq_ID} activity_cookie 失败')
        return False
