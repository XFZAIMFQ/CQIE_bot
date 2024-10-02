import time

import requests


def sendFile(qq_ID, file, name):
    time.sleep(2)
    url = 'http://127.0.0.1:5700/upload_private_file'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "user_id": qq_ID,
        "file": file,
        "name": name
    }
    post = requests.post(url, headers=headers, json=data)
