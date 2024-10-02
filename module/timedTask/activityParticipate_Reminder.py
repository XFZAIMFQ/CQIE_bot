from datetime import timedelta

from module.go_cqhttp import friend_sendMessage


def activityParticipate_Reminder(database, date, switch=True):
    new_time = date.strftime('%Y-%m-%d %H:%M:00')
    next_time = (date + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:00')
    SQL = (f"select ID,HDMC,applicants from activity_tab "
           f"where {'HDKSSJ' if switch else 'HDJSSJ'} <= %s and {'HDKSSJ' if switch else 'HDJSSJ'} > %s and applicants is not null ;")
    data = (next_time, new_time)
    execution = database.execution(SQL, data)
    if not execution:
        return False
    for activity in execution:
        ID = activity[0]
        HDMC = activity[1]
        applicants = activity[2]
        user_IDs = applicants.split(',')[:-1]
        message = (f"10分钟后有一个活动{'开始' if switch else '结束'}\n"
                   f"活动名称:{HDMC}\n"
                   f"活动ID:{ID}")
        for user_ID in user_IDs:
            friend_sendMessage(user_ID, message)
