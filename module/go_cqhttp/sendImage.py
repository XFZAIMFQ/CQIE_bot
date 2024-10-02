import time

import requests

from module.tool.outputLog import log


def friend_sendImage(qq_ID, imageurl):
    """ 发送图片 """
    time.sleep(2)
    url = 'http://127.0.0.1:5700/send_msg'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "message_type": "private",
        "user_id": qq_ID,
        "message": f"[CQ:image,file=签到码,url={imageurl}]",
    }
    post = requests.post(url, headers=headers, json=data)

    if post.json().get("status") == "ok":
        log.info(f'向 <{qq_ID}> 发送图片 "{imageurl.split("/")[-1]}" 发送成功')
    else:
        log.info(f'向 <{qq_ID}> 发送图片 "{imageurl.split("/")[-1]}" 发送失败')