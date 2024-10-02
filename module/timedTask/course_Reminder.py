import sched
import time
from datetime import datetime, timedelta

from module.educationSystem import get_teachingWeek
from module.go_cqhttp import friend_sendMessage


def course_Reminder(reminderTime, database):
    dates = {"8:00": "'1-_'", "10:09": "'3-_'", "13:30": "'5-_'", "15:39": "'7-_'", "18:30": "'9-__'", "20:39": "'11-__'"}
    SQL = "select QQ,commencement_Time from user_tab  where course_Reminder = 1;"
    execution = database.execution(SQL)
    if execution:
        for user_data in execution:
            qq_ID = user_data[0]  # 用户QQ
            date = user_data[1]  # 上课时间
            days = (datetime.now().date() - date).days + 1
            week_nums, day_of_week = get_teachingWeek(days)
            SQL = "select courseName,teacherName,class_nums,location,numberOfPeopleInClass " \
                  "from course_tab " \
                  f"where week_nums like %s and day_of_week = %s and class_nums like {dates[reminderTime]} and QQ = %s"
            data = (f'%,{week_nums},%', f'{day_of_week}', f'{qq_ID}')
            execution = database.execution(SQL, data)
            if execution:
                classTime = {'8:00': 30, '10:09': 20, '13:30': 30, '15:39': 20, '18:30': 30, '20:39': 10}
                friend_sendMessage(qq_ID, f"提醒:{classTime[reminderTime]}分钟后你有一门课程")

                from cqie_bot import sendInquirySchedule
                sendInquirySchedule(qq_ID, execution)


def schedule_tasks(tasks, database):
    s = sched.scheduler(time.time, time.sleep)

    # 定义任务函数
    def task():
        now = datetime.now()
        # 获取当前时间的小时和分钟
        current_hour = now.hour
        current_minute = now.minute

        # 根据当前时间选择要执行的任务
        # 取出 tasks 中的执行任务时间与任务
        for time_str, task_func in tasks.items():
            # 取出执行任务的时间的 hour 与 minute
            hour, minute = map(int, time_str.split(':'))
            # 判断时间是否相同 相同就执行任务
            if current_hour == hour and current_minute == minute:
                task_func(time_str, database)

        # 计算下一次任务的调度时间
        next_time = now + timedelta(minutes=1)
        next_time = next_time.replace(second=0, microsecond=0)

        # 设置下一次任务的调度时间
        s.enterabs(next_time.timestamp(), 1, task)

    # 获取当前时间
    now = datetime.now()
    # 计算下一分钟的调度时间
    next_time = now + timedelta(minutes=1)
    next_time = next_time.replace(second=0, microsecond=0)

    # 计算延迟时间
    delay = (next_time - now).total_seconds()

    # 设置第一次任务的调度时间
    s.enter(delay, 1, task)
    # 开始调度任务
    s.run()


def course_Reminder_start(database):
    tasks = {
        '8:00': course_Reminder,
        '10:10': course_Reminder,
        '13:40': course_Reminder,
        '15:40': course_Reminder,
        '18:40': course_Reminder,
        '20:40': course_Reminder
    }
    schedule_tasks(tasks, database)
