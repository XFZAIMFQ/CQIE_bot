from module.tool.outputLog import log


def databaseKeepalive(database):
    try:
        execution = database.execution('SELECT 1')
        if execution:
            log.info(f'保活成功')
    except Exception as e:
        log.info(f'数据库失去连接')