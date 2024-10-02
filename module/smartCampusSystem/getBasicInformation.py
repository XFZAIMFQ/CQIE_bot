import requests
def get_basicInformation(cookie):
    """获取基本信息"""
    url = 'http://i.cqie.edu.cn/GeRenZhongXingJbxx/queryJbxx'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Cookie': cookie,
    }

    response = requests.post(url, headers=headers)
    if response.status_code == 200 and 'XH' in response.text:
        json_data = response.json()
        return json_data
    else:
        return False
