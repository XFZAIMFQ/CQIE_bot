import sched
import time

from datetime import datetime, timedelta

from module.electricityBillQuery import get_wanmeielectricityFees
from module.go_cqhttp import friend_sendMessage
from module.tool.outputLog import log

roomData = {
    "容园7号": 1,
    "容园6号": 2,
    "和园3号一单元": 3,
    "和园3号二单元": 4,
    "容园5号": 5,
    "容园1号": 6,
    "容园4号": 7,
    "双桥明仁楼": 8,
    "双桥明义楼": 9,
    "双桥明理楼": 10,
    "双桥明智楼": 11,
    "双桥明信楼": 12,
    "双桥教师宿舍": 13,
    "容园3号": 14,
    "容园2号": 15,
    "和园1号": 16,
    "和园2号": 17,
    "和园4号": 18,
    "和园5号": 19
}
roomData_t = {value: key for key, value in roomData.items()}


def electricCharge_Reminder(database):
    SQL = "select QQ, QSL, QSH " \
          "from user_tab natural join bedroom_tab " \
          "where electric_Reminder = 1 and QSL is not null and QSH is not null;"
    execution = database.execution(SQL)
    if execution:
        for data in execution:
            qq_ID = data[0]
            QSL = data[1]
            QSH = data[2]
            # 获得寝室剩余电费
            electricityBill = get_wanmeielectricityFees(QSL, QSH)
            log.info(f'检测用户 <{qq_ID}> | QSL <{roomData_t[int(QSL)]}> | QSH <{QSH}> | 剩余电费 <{electricityBill}>')
            # 判断电费是否小于10度
            if electricityBill == 0.0 or electricityBill < 10:
                message = f"您绑定的 {roomData_t[int(QSL)]} {QSH} 寝室\n电费剩余{electricityBill} ,已经不足10度请尽快充值电费"
                friend_sendMessage(qq_ID, message)
                continue
            # 发生错误则关闭当前用户的电费不足提醒功能
            if electricityBill != 0.0 and not electricityBill:
                update = "update user_tab set electric_Reminder = 0 where QQ = %s ;"
                data = (qq_ID,)
                execution = database.execution(update, data)
                if execution:
                    message = f"您绑定的 {roomData_t[int(QSL)]} {QSH} 寝室\n 存在错误已经为你关闭电费剩余提醒功能"
                    friend_sendMessage(qq_ID, message)
                else:
                    # print('用户:', qq_ID, '寝室绑定错误,关闭电费剩余提醒功能失败')
                    log.info(f'用户 <{qq_ID}> 寝室绑定错误,关闭电费剩余提醒功能失败')
            time.sleep(5)
        log.info(f'电费不足检测已经结束')


def schedule_tasks(database):
    s = sched.scheduler(time.time, time.sleep)

    # 定义任务函数
    def task():
        now = datetime.now()
        # 获取当前时间的小时和分钟
        current_hour = now.hour
        current_minute = now.minute

        # # 根据当前时间选择要执行的任务
        # for time_str, task_func in tasks.items():
        #     hour, minute = map(int, time_str.split(':'))
        #     if current_hour == hour and current_minute == minute:
        #         task_func(time_str, database)

        if current_minute == 0:
            electricCharge_Reminder(database)

        # 计算下一次任务的调度时间
        next_time = now + timedelta(hours=1)  # 加一个小时
        next_time = next_time.replace(second=0, microsecond=0)

        # 设置下一次任务的调度时间
        s.enterabs(next_time.timestamp(), 1, task)

    # 获取当前时间
    now = datetime.now()
    # 计算下一分钟的调度时间
    next_time = now + timedelta(hours=1)
    next_time = next_time.replace(second=0, microsecond=0)

    # 计算延迟时间
    delay = (next_time - now).total_seconds()

    # 设置第一次任务的调度时间
    s.enter(delay, 1, task)
    # 开始调度任务
    s.run()


def electricCharge_Reminder_start(database):
    schedule_tasks(database)
