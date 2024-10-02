import time

import requests

from module.tool.outputLog import log


def friend_sendMessage(qq_ID, message):
    time.sleep(2)
    url = 'http://127.0.0.1:5700/send_msg'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "message_type": "private",
        "user_id": qq_ID,
        "message": message,
    }
    post = requests.post(url, headers=headers, json=data)

    if post.json().get("status") == "ok":
        log.info(f'向 <{qq_ID}> 发送消息 "{repr(message)}" 发送成功')
    else:
        log.info(f'向 <{qq_ID}> 发送消息 "{repr(message)}" 发送失败')

