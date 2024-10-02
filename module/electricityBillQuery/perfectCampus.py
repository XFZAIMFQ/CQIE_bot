import re

import requests

proxy = {'http': '127.0.0.1:7890', 'https': '127.0.0.1:7890'}


def get_wanmeielectricityFees(build, room):
    """ 获得寝室剩余电费 """
    url = 'https://www.cqie.edu.cn:809/epay/wxpage/wanxiao/eleresult'

    params = {
        'sysid': 1,
        'roomid': room,
        'areaid': 2,
        'buildid': build
    }

    headers = {
        'Referer': f'https://www.cqie.edu.cn:809/epay/wxpage/wanxiao/eleresult?sysid=1&roomid={room}&areaid=2&buildid={build}',
    }

    response = requests.get(url, params=params, headers=headers)
    # print(response.text)
    match = re.search(r'(\d+(\.\d+)?)度', response.text)
    if match:
        number = match.group(1)
        return float(number)
    else:
        return False


if __name__ == '__main__':
    print(get_wanmeielectricityFees(room=141, build=18))
