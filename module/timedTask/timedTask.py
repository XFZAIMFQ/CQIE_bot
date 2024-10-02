import sched
import threading
import time
from datetime import datetime, timedelta

from module.timedTask.activityParticipate_Reminder import activityParticipate_Reminder
from module.timedTask.activity_Reminder import activity_Reminder
from module.timedTask.course_Reminder import course_Reminder
from module.timedTask.databaseKeepalive import databaseKeepalive
from module.timedTask.electricCharge_Reminder import electricCharge_Reminder
from module.tool.outputLog import log


def schedule_tasks(tasks, database):
    s = sched.scheduler(time.time, time.sleep)

    # 定义任务函数
    def timedTask():
        now = datetime.now()
        # 获取当前时间的小时和分钟
        current_hour = now.hour
        current_minute = now.minute

        # 根据当前时间选择要执行的任务
        for time_str, task_func in tasks.items():
            hour, minute = map(int, time_str.split(':'))
            if current_hour == hour and current_minute == minute:
                log.info(f'上课提醒检测')
                task_func_thread = threading.Thread(target=task_func, args=(time_str, database))
                task_func_thread.start()
                log.info(f'已启动上课提醒检测线程')

        if current_minute == 0 and current_hour >= 8:
            # 电费不足检测 每1小时检测一次 0-8点不检测
            log.info(f'电费不足检测')
            electricCharge_Reminder_thread = threading.Thread(target=electricCharge_Reminder, args=(database,))
            electricCharge_Reminder_thread.start()
            log.info(f'已启动电费不足检测线程')

        if current_minute % 15 == 0 and current_hour >= 8:
            # 活动检测 每15分钟检测一次 0-8点不检测
            log.info(f'活动订阅检测')
            activity_Reminder_thread = threading.Thread(target=activity_Reminder, args=(database,))
            activity_Reminder_thread.start()
            log.info(f'已启动活动订阅检测线程')

        if current_minute % 10 == 0 and current_hour >= 8:
            # 活动参加提醒 每10分钟检测一次 0-8点不检测
            log.info(f'活动参加提醒')
            activityParticipate_Reminder_start_thread = threading.Thread(target=activityParticipate_Reminder,
                                                                         args=(database, now, True))
            activityParticipate_Reminder_start_thread.start()
            activityParticipate_Reminder_end_thread = threading.Thread(target=activityParticipate_Reminder,
                                                                       args=(database, now, False))
            activityParticipate_Reminder_end_thread.start()
            log.info(f'已启动活动参加提醒检测线程')

        if current_minute % 30 == 0:
            """ 数据库保活连接 """
            log.info(f'数据库保活')
            databaseKeepalive_thread = threading.Thread(target=databaseKeepalive, args=(database,))
            databaseKeepalive_thread.start()
            log.info(f'已启动活动订阅检测线程')

        # 计算下一次任务的调度时间
        next_time = now + timedelta(minutes=1)
        next_time = next_time.replace(second=0, microsecond=0)

        # 设置下一次任务的调度时间
        s.enterabs(next_time.timestamp(), 1, timedTask)

    # 获取当前时间
    now = datetime.now()
    # 计算下一分钟的调度时间
    next_time = now + timedelta(minutes=1)
    next_time = next_time.replace(second=0, microsecond=0)

    # 计算延迟时间
    delay = (next_time - now).total_seconds()

    # 设置第一次任务的调度时间
    s.enter(delay, 1, timedTask)
    # 开始调度任务
    s.run()


def timedTask_Start(database):
    tasks = {
        '8:00': course_Reminder,
        '10:09': course_Reminder,
        '13:30': course_Reminder,
        '15:39': course_Reminder,
        '18:30': course_Reminder,
        '20:39': course_Reminder
    }
    schedule_tasks(tasks, database)
