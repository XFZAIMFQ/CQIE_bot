import sched
import time

from datetime import datetime, timedelta

from module.activitySystem import automaticallyFetchActivity_Cookie, get_activityQuery_Get, get_activityQuery_Query, \
    get_activityDetails_Query
from module.activitySystem.activity_applyAndcancel import apply_activity
from module.go_cqhttp import friend_sendMessage
from module.tool.outputLog import log


def activity_Reminder(database):
    """ 活动提醒 """
    cookie = automaticallyFetchActivity_Cookie('3057466296', database)
    if not cookie:
        log.info('activity_Reminder 获取Cookie失败')
        return False
    get_activity = get_activityQuery_Get(cookie, 1)
    if not get_activity:
        log.info('activity_Reminder 获取活动失败')
        return False
    # 获取最大页数
    maxPage = get_activity['page']['maxPage']
    if maxPage == 0:
        log.info('activity_Reminder 目前没有活动')
        return False
    log.info('已检测到活动')
    ID_list_news = []
    for i in range(1, maxPage + 1):
        # 进行活动查询 获取不同页的各项活动
        query_activity = get_activityQuery_Query(cookie, 1, i)
        if not query_activity:
            log.info('activity_Reminder 活动获取异常')
            return False
        # 取出活动json数据中的data
        activity_datas = query_activity['data']
        for activity_data in activity_datas:
            log.info(f"活动ID <{activity_data}>")
            ID_list_news.append(activity_data['ID'])
        time.sleep(5)

    # 旧的活动
    ID_list_olds = []
    # SQL = "SELECT ID FROM activity_tab WHERE NOW() < SQJSSJ"
    # SQL = "SELECT ID FROM activity_tab WHERE NOW() < SQJSSJ"
    # SQL = "SELECT ID FROM activity_tab  WHERE NOW() < SQJSSJ and Reminders_num <= 3;"
    SQL = "SELECT ID FROM activity_tab ;"
    execution = database.execution(SQL)
    if execution:
        for i in execution:
            ID_list_olds.append(i[0])
        for ID_list_new in ID_list_news:
            if ID_list_new not in ID_list_olds:
                activity_Reminder_send(database, cookie, ID_list_new)
    else:
        for ID_list_new in ID_list_news:
            activity_Reminder_send(database, cookie, ID_list_new)


def activity_Reminder_send(database, cookie, activity_ID):
    activityDetails_datas = get_activityDetails_Query(cookie, activity_ID)
    if not activityDetails_datas:
        # print('activity_Reminder 获取活动详情失败')
        log.info('activity_Reminder 获取活动详情失败')
        return False
    activity_type = {'301': "A", '302': "B", '303': "C", '304': "D", "399": "创造性劳动", "397": "服务性劳动",
                     "398": "生产性劳动", "400": "劳动培训", "403": "岗位劳动实践", "404": "义务劳动",
                     "401": "劳模讲座", "402": "劳动技能培训", "405": "种植劳动实践", "406": "专业生产性劳动实践",
                     "407": "其它", "396": "日常生活劳动"}
    activityDetails_data = activityDetails_datas[0]
    ID = activityDetails_data['ID']  # 活动ID
    HDMC = activityDetails_data['HDMC']  # 活动名称
    HDSX = activityDetails_data['HDSX']  # 活动属性
    HDXF = activityDetails_data['HDXF']  # 活动学分
    SQKSSJ = activityDetails_data['SQKSSJ']  # 申请开始时间
    SQJSSJ = activityDetails_data['SQJSSJ']  # 申请结束时间
    HDKSSJ = activityDetails_data['HDKSSJ']  # 活动开始时间
    HDJSSJ = activityDetails_data['HDJSSJ']  # 活动结束时间
    FQZDH = activityDetails_data['FQZDH']  # 发起者电话
    FQDW = activityDetails_data['FQDW']  # 发起单位
    MXDXMC = activityDetails_data['MXDXMC']  # 参加学院
    MXNJMC = activityDetails_data['MXNJMC']  # 参与年级
    HDDD = activityDetails_data['HDDD']  # 活动地点

    SQL = f"SELECT QQ, college, grade, automatic_Application,activity_Reminder_type " \
          f"FROM user_tab " \
          f"WHERE activity_Reminder = 1 and activity_Reminder_type like '%{activity_type[HDSX]}%' ;"
    execution = database.execution(SQL)
    if not execution:
        return False
    for user in execution:
        if user[1] not in MXDXMC or user[2] not in MXNJMC:
            continue
        qq_ID = user[0]
        message = f"有一个你订阅的{activity_type[HDSX]}类活动 \n" \
                  f"活动名称:{HDMC} 活动积分:{HDXF}分 \n" \
                  f"活动ID:{ID} \n" \
                  f"如需参与活动请发送下列文字"
        friend_sendMessage(qq_ID, message)
        friend_sendMessage(qq_ID, f"申请活动 {ID}")
        # 活动自动申请
        if user[3] == 1:
            # 线上活动
            if user[4] == '线上' and (any(string in HDDD for string in ['学习通', '直播间', '直播课程码']) or any(
                    string in HDMC for string in ['直播讲座', '时政导学', '心理健康教育', '线上'])):
                apply_activity(qq_ID, ID, True)
            elif user[4] == '不限':
                # 申请活动
                apply_activity(qq_ID, ID, True)

    insert = "insert into activity_tab (ID, HDMC, HDSX, HDXF, SQKSSJ, SQJSSJ, HDKSSJ, HDJSSJ, MXDXMC, MXNJMC," \
             " FQZDH, FQDW) " \
             "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    data = (ID, HDMC, HDSX, HDXF, SQKSSJ, SQJSSJ, HDKSSJ, HDJSSJ, ','.join(MXDXMC), ','.join(MXNJMC), FQZDH, FQDW)
    execution = database.execution(insert, data)
    if execution:
        log.info(f'activity_Reminder 活动:{HDMC} 保存数据库成功')
    else:
        log.info(f'activity_Reminder 活动:{HDMC} 保存数据库错误')


def schedule_tasks(database):
    s = sched.scheduler(time.time, time.sleep)

    # 定义任务函数
    def task():
        now = datetime.now()
        # 获取当前时间的小时和分钟
        current_hour = now.hour
        current_minute = now.minute

        if current_minute % 15 == 0:
            activity_Reminder(database)

        # 计算下一次任务的调度时间
        next_time = now + timedelta(minutes=15)
        next_time = next_time.replace(second=0, microsecond=0)

        # 设置下一次任务的调度时间
        s.enterabs(next_time.timestamp(), 1, task)

    # 获取当前时间
    now = datetime.now()
    # 计算下一分钟的调度时间
    next_time = now + timedelta(minutes=15)
    next_time = next_time.replace(second=0, microsecond=0)

    # 计算延迟时间
    delay = (next_time - now).total_seconds()

    # 设置第一次任务的调度时间
    s.enter(delay, 1, task)
    # 开始调度任务
    s.run()


def activity_Reminder_start(database):
    activity_Reminder(database)
