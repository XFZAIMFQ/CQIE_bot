import os

import requests

from module.tool.outputLog import log


def downloadFile(url, path=None, fileName=None):
    """ 下载文件 """
    log.info(f"开始下载文件{url}")
    response = requests.get(url)

    if response.status_code != 200:
        log.info(f'{url} 下载失败')
        return False

    if path is None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.join(current_dir, "../..")
        if '/' in target_dir:
            path = f'{target_dir}/download/imageFlie'
        else:
            path = f'{target_dir}\\download\\imageFlie'
    if fileName is None:
        fileName = url.split('/')[-1]

    saveRoute = f'{path}/{fileName}'

    if os.path.exists(saveRoute):
        log.info(f"文件已存在,取消下载")
        return fileName, path

    with open(saveRoute, 'wb') as f:
        f.write(response.content)
    log.info(f'文件 {fileName} 已下载完成,保存路径 {saveRoute}')

    return fileName, path
