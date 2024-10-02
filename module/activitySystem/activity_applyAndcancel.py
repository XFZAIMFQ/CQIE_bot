# 活动申请
import requests

from module.activitySystem import automaticallyFetchActivity_Cookie, get_activityDetails_Query
from module.database.CQIE_bot_database import database
from module.go_cqhttp import friend_sendMessage
from module.tool.outputLog import log


def apply_activity(qq_ID, message, auto=False):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法申请活动')
        return None
    # 判断是否为自动签到
    if auto:
        ID = message
    else:
        messages = message.split(" ")
        if len(messages) != 2 or messages[1] == "":
            friend_sendMessage(qq_ID, '申请活动失败,指令错误请重试\n正确指令:申请活动 [活动ID] 使用空格隔开')
            return None
        ID = messages[1]

    cookie = automaticallyFetchActivity_Cookie(qq_ID, database)
    if not cookie:
        friend_sendMessage(qq_ID, '活动申请失败,原因:cookie获取不成功')
        return None
    query = get_activityDetails_Query(cookie, ID)
    if not query:
        log.info(f'用户 <{qq_ID}> apply_activity 获取活动数据失败')
        return None
    loads_data, xh, hdsxbj = query
    url = 'http://xs.cqie.edu.cn/xg/' + hdsxbj + 'zyz' + '/insertSQ'
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'cookie': cookie}
    data = {'hdid': ID}
    response = requests.post(url, headers=headers, data=data)
    applicationResults = response.json()
    if not applicationResults.get('flag'):
        friend_sendMessage(qq_ID, f"{'自动' if auto else ''}申请失败\n"
                                  f"原因:{applicationResults.get('msg')}")
    else:
        friend_sendMessage(qq_ID, f"{'自动' if auto else ''}申请成功\n"
                                  f"活动ID:{ID}")
        SQL = "UPDATE activity_tab SET applicants = CONCAT(IFNULL(applicants, ''), %s) WHERE ID = %s;"
        data = (f"{qq_ID},", ID)
        execution = database.execution(SQL, data)
        if execution:
            log.info(f'用户 <{qq_ID}> 添加活动 <{ID}> 提醒成功 ')
        else:
            log.info(f'用户 <{qq_ID}> 添加活动 <{ID}> 提醒失败 ')


# 活动取消
def activity_cancel(qq_ID, message):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法取消申请活动')
        return None
    messages = message.split(" ")
    if len(messages) != 2 or messages[1] == "":
        friend_sendMessage(qq_ID, '取消申请活动失败,指令错误请重试\n正确指令:取消申请活动 [活动ID] 使用空格隔开')
        return None
    ID = messages[1]

    cookie = automaticallyFetchActivity_Cookie(qq_ID, database)
    if not cookie:
        print(f'用户 <{qq_ID}> cancel_activity 获取cookie 失败')
        return None
    query = get_activityDetails_Query(cookie, ID)
    if not query:
        print(f'用户 <{qq_ID}> cancel_activity 获取活动数据失败')
    loads_data, xh, hdsxbj = query

    # 请求 URL
    url = 'http://xs.cqie.edu.cn/xg/allhdzyz/cancel'
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 'cookie': cookie}
    # 请求参数
    data = {
        'hdid': ID,
        'xh': xh,
        'hdlx': hdsxbj
    }
    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=data)
    cancelResult = response.json()
    if cancelResult.get('success'):
        # 活动取消成功
        friend_sendMessage(qq_ID, cancelResult.get('msg'))
        # 删除数据库中申请的活动提醒
        SQL = "select applicants from activity_tab where ID = %s;"
        data = (ID,)
        execution = database.execution(SQL, data)
        # 查询到数据且数据不为空时
        if execution and execution[0][0] is not None:
            user_IDs = execution[0][0].split(',')[:-1]
            if qq_ID in user_IDs:
                user_IDs.remove(qq_ID)
            SQL = "update activity_tab set applicants = %s where ID = %s;"
            data = ((','.join(user_IDs) + ',') if len(user_IDs) != 0 else '', ID)
            database_execution = database.execution(SQL, data)
            if database_execution:
                log.info(f'用户 <{qq_ID}> 取消活动提醒成功')
            else:
                log.info(f'用户 <{qq_ID}> 取消活动提醒失败')
    else:
        friend_sendMessage(qq_ID, cancelResult.get('msg'))
