import datetime
import json
import re
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from module.activitySystem import automaticallyFetchActivity_Cookie, get_Activity_Cookie, get_activityQuery_Get, \
    get_activityDetails_Query, get_activityQuery_Query, apply_activity, activity_cancel
from module.database import database
from module.educationSystem import automaticAcquisition_educationSystem_Cookie, set_curriculum, get_teachingWeek, \
    set_commencementTime
from module.electricityBillQuery import get_ADormAutomatically, get_wanmeielectricityFees
from module.go_cqhttp import friend_sendImage, friend_sendMessage
from module.smartCampusSystem import get_basicInformation, get_smartCampus_Cookie
from module.timedTask import roomData_t, roomData
from module.timedTask import timedTask_Start
from module.tool import log
from module.tool.Mqtt import client, startMQTT, closeMQTT, sendCommand


# 创建自定义的请求处理器类
class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        if json.loads(post_data)['post_type'] != "meta_event":
            # print(f"Received POST data: {post_data}")
            str_post_data = str(post_data).replace('\n', '')
            log.info(f"Received POST data: {str_post_data} ")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"POST received successfully")
            # 解析消息
            messageParser(post_data)
        # 回复客户端请求
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"POST received successfully")

    def log_message(self, format, *args):
        pass


def messageParser(message):
    message = replace_multiple_spaces(message)
    loads_message = json.loads(message)
    if loads_message.get('message_type') == 'private':
        user_id = loads_message['user_id']
        message = loads_message['message']
        threading.Thread(target=executeCommand, args=(user_id, message)).start()


# 执行命令
def executeCommand(user_id, message):
    match message.split(" ")[0]:
        case ("查询电费"):
            queryElectricityBill(user_id, message)
        case ("开启电费不足提醒"):
            set_electric_Reminder(user_id, True)
        case ("关闭电费不足提醒"):
            set_electric_Reminder(user_id, False)
        case ("开启电费用量订阅"):
            set_electricCharge_Reminder(user_id, True)
        case ("关闭电费用量订阅"):
            set_electricCharge_Reminder(user_id, False)
        case ("绑定寝室"):
            bindTheDormitory(user_id, message)
        case ("解绑寝室"):
            untieTheBedroom(user_id)
        case ("查询参加过的活动"):
            participatedInTheEvent(user_id)
        case ("绑定智慧校园平台"):
            bindingCampusPlatform(user_id, message)
        case ("解绑智慧校园平台"):
            untieTheCampusPlatform(user_id)
        case ("更新课表"):
            updateClassSchedule(user_id)
        case ("查询课表"):
            checkSchedule(user_id, message)
        case ("更新教学周"):
            updateOrGetTeachingWeek(user_id, update=True)
        case ("查询综测成绩"):
            queryComprehensiveTestResults(user_id, message)
        case ("申请活动"):
            apply_activity(user_id, message)
        case ("取消活动"):
            activity_cancel(user_id, message)
        case ('开启自动申请活动'):
            set_automaticApplicationForActivities(user_id, True)
        case ('关闭自动申请活动'):
            set_automaticApplicationForActivities(user_id, False)
        case ('设置自动申请活动类型'):
            set_automaticApplicationForActivities_type(user_id, message)
        case ('导入活动提醒'):
            importEventReminders(user_id, message)
        case ("获取活动签到码"):
            # get_activitySignInCode(user_id, message)
            pass
        case ("开启活动提醒"):
            set_activity_Reminder(user_id, True)
        case ("关闭活动提醒"):
            set_activity_Reminder(user_id, False)
        case ("设置活动提醒类型"):
            set_activity_Reminder_type(user_id, message)
        case ("开启上课提醒"):
            set_course_Reminder(user_id, True)
        case ("关闭上课提醒"):
            set_course_Reminder(user_id, False)
        case ("开启免打扰模式"):
            pass
        case ("关闭免打扰模式"):
            pass
        case ("查询成绩"):
            pass
        case ("添加日历提醒"):
            pass
        case ("统计综测成绩"):
            # messageProcessing = threading.Thread(target=statisticsComprehensiveTestResults, args=(user_id, message))
            # messageProcessing.start()
            statisticsComprehensiveTestResults(user_id, message)
            pass
        case ("查询已开启功能"):
            queryFunctionstatus(user_id)
        case ("群发消息"):
            # messageProcessing = threading.Thread(target=groupMessage, args=(user_id, message))
            # messageProcessing.start()
            groupMessage(user_id, message)
        case ("手动执行"):
            manualExecution(user_id, message)
        case ("重启服务"):
            pass
        case ("帮助"):
            CQIE_bot_help(user_id)
            pass
        case ("测试设备"):
            testEquipment(message)
            pass


# 替换多个空格
def replace_multiple_spaces(message):
    pattern = r"\s+"
    replaced_message = re.sub(pattern, " ", message)
    return replaced_message


# 查询电费
def queryElectricityBill(qq_ID, message):
    messages = message.split(" ")
    if len(messages) == 1:
        query = "SELECT * FROM bedroom_tab where QQ = %s ;"
        data = (qq_ID,)
        result = database.execution(query, data)
        if result:
            buildid = int(result[0][1])
            roomid = int(result[0][2])
            searchResult = get_wanmeielectricityFees(build=buildid, room=roomid)
            # print(electricityBill)
            if searchResult == 0.0 or searchResult:
                message = f"已经为您查询到电费了哦\n寝室楼:{roomData_t[buildid]} 寝室号:{roomid}\n电费剩余:{searchResult} 度"
                friend_sendMessage(qq_ID, message)
            else:
                message = f"很抱歉没有查询到{roomid}寝室的电费"
                friend_sendMessage(qq_ID, message)
        else:
            query = "SELECT * FROM user_tab where QQ = %s ;"
            data = (qq_ID,)
            result = database.execution(query, data)
            if result:
                message = f"似乎你没有手动绑定寝室\n正在自动帮您查询中"
                friend_sendMessage(qq_ID, message)
                studentID = result[0][1]
                password = result[0][2]
                automatically = get_ADormAutomatically(username=studentID, password=password)
                if automatically:
                    buildid = roomData[automatically[0]]  # 获得寝室楼
                    roomid = int(automatically[1])  # 获得寝室号
                    searchResult = get_wanmeielectricityFees(build=buildid, room=roomid)
                    if searchResult == 0.0 or searchResult:
                        message = f"已经为您查询到电费了哦\n寝室楼:{roomData_t[buildid]} 寝室号:{roomid}\n电费剩余:{searchResult} 度"
                        friend_sendMessage(qq_ID, message)
                        bindTheDormitory(qq_ID, f"绑定寝室 {roomData_t[buildid]} {roomid}")
                        message = f"已自动帮您绑定寝室 {automatically[0]} {automatically[1]}\n如需解绑,请发送指令 解绑寝室"
                        friend_sendMessage(qq_ID, message)
                        return None
                    else:
                        message = f"自动查询失败请手动绑定"
                        friend_sendMessage(qq_ID, message)
                else:
                    message = f"暂时无法自动获取到你的寝室,请尝试手动绑定。"
                    friend_sendMessage(qq_ID, message)
                    return None
            else:
                message = f"很抱歉好像没有记录你的寝室信息哦\n发送绑定寝室即可开始绑定\n" \
                          f"例:'绑定寝室 和园1号 101'使用空格隔开\n或绑定解绑智慧校园平台自动查询"
                friend_sendMessage(qq_ID, message)
            time.sleep(1)
    elif len(messages) == 3:
        if messages[1] not in roomData:
            friend_sendMessage(qq_ID, f"楼栋输入错误, 没有{messages[1]}楼")
            return None
        buildid = int(roomData[messages[1]])
        roomid = int(messages[2])
        electricityBill = get_wanmeielectricityFees(build=buildid, room=roomid)
        if electricityBill == 0.0 or electricityBill:
            message = f"已经为您查询到电费了哦\n寝室楼:{roomData_t[buildid]} 寝室号:{roomid}\n电费剩余:{electricityBill} 度"
            friend_sendMessage(qq_ID, message)
        else:
            message = f"很抱歉没有查询到{roomid}寝室的电费\n请检查参数是否正确"
            friend_sendMessage(qq_ID, message)
    else:
        message = f"很抱歉你的指令输入错误"
        friend_sendMessage(qq_ID, message)


# 设置电费不足提醒是否开启
def set_electric_Reminder(qq_ID, switch):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法进行设置电费不足提醒')
        return None
    if switch:
        SQL = "UPDATE user_tab SET electric_Reminder = 1 where QQ = %s"

    else:
        SQL = "UPDATE user_tab SET electric_Reminder = 0 where QQ = %s"

    data = (qq_ID,)
    execution = database.execution(SQL, data)
    if execution:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}电费不足提醒')
        return None
    else:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}电费不足提醒设置失败')


# 设置电费用量订阅是否开启
def set_electricCharge_Reminder(qq_ID, switch):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法进行设置电费用量订阅')
        return None
    if switch:
        SQL = "UPDATE user_tab SET electricCharge_Reminder = 1 where QQ = %s"
    else:
        SQL = "UPDATE user_tab SET electricCharge_Reminder = 0 where QQ = %s"

    data = (qq_ID,)
    execution = database.execution(SQL, data)
    if execution:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}电费用量订阅')
        return None
    else:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}电费用量订阅设置失败')


# 绑定寝室
def bindTheDormitory(qq_ID, message):
    query = "SELECT * FROM bedroom_tab where QQ = %s ;"
    result = database.execution(query, (qq_ID,))
    if result:
        friend_sendMessage(qq_ID, "已经绑定过喽")
        return None
    messages = message.split(" ")
    if len(messages) != 3:
        friend_sendMessage(qq_ID, "绑定格式错误请重试")
        return None
    if messages[1] not in roomData:
        friend_sendMessage(qq_ID, f"楼栋输入错误, 没有 {messages[1]} ")
        return None
    buildid = roomData[messages[1]]
    roomid = messages[2]

    electricityBill = get_wanmeielectricityFees(build=int(buildid), room=int(roomid))
    if electricityBill == 0.0 or electricityBill:
        insert = "INSERT INTO bedroom_tab (QQ,QSL,QSH) VALUES (%s,%s,%s)"
        execution = database.execution(insert, (qq_ID, str(buildid), roomid))
        if execution:
            friend_sendMessage(qq_ID, f"成功绑定 {messages[1]} {messages[2]}")
    else:
        friend_sendMessage(qq_ID, f"绑定失败请检查数据是否合法\n目前已知寝室楼:容园7号")


# 解绑寝室
def untieTheBedroom(qq_ID):
    """解绑寝室"""
    query = "SELECT * FROM bedroom_tab where QQ = %s ;"
    result = database.execution(query, (qq_ID,))
    if result:
        delete = " DELETE FROM bedroom_tab WHERE QQ = %s "
        execution = database.execution(delete, (qq_ID,))
        if execution:
            friend_sendMessage(qq_ID, f"解绑成功")
        else:
            friend_sendMessage(qq_ID, f"解绑失败")
    else:
        friend_sendMessage(qq_ID, f"未绑定无需解绑")


# 查询参加过的活动
def participatedInTheEvent(qq_ID):
    query = "SELECT activity_Cookie from user_cookie_tab where QQ = %s ;"
    data = (qq_ID,)
    result = database.execution(query, data)
    if result:
        activity_Cookie = result[0]


# 绑定智慧校园平台
def bindingCampusPlatform(qq_ID, message):
    query = "SELECT * from user_tab where QQ = %s ;"
    data = (qq_ID,)
    result = database.execution(query, data)
    if result:
        friend_sendMessage(qq_ID, "你已经绑定过了无须再次绑定")
        return None
    else:
        messages = message.split(' ')
        studentId = messages[1]
        password = messages[2]
        activity_cookie = get_Activity_Cookie(studentId, password)
        if not activity_cookie:
            friend_sendMessage(qq_ID, "你的绑定的信息存在错误,请重试!")
            return None
        cookie = get_smartCampus_Cookie(studentId, password)
        informations = get_basicInformation(cookie)
        DWMC = informations.get('DWMC')
        SZNJ = informations.get('SZNJ')
        insert = "insert into user_tab (QQ, studentID, password,college,grade) values (%s,%s,%s,%s,%s);"
        data = (qq_ID, studentId, password, DWMC, SZNJ + '级')
        execution = database.execution(insert, data)
        if execution:
            friend_sendMessage(qq_ID, f"{informations.get('XM')}同学 绑定成功!")
        else:
            friend_sendMessage(qq_ID, "绑定失败!")


# 解绑智慧校园平台
def untieTheCampusPlatform(qq_ID):
    query = "SELECT * from user_tab where QQ = %s ;"
    data = (qq_ID,)
    result = database.execution(query, data)
    if result:
        delete = "DELETE FROM user_tab WHERE QQ = %s"
        execution = database.execution(delete, data)
        if execution:
            friend_sendMessage(qq_ID, "解绑智慧校园平台成功!")
        else:
            friend_sendMessage(qq_ID, "解绑智慧校园平台失败!")
    else:
        friend_sendMessage(qq_ID, "未绑定智慧校园平台,无需解绑。")


# 发送私聊信息


# 更新课表
def updateClassSchedule(qq_ID):
    sql = "DELETE FROM course_tab WHERE QQ = %s ;"
    data = (qq_ID,)
    execution = database.execution(sql, data)
    if execution:
        # print('用户: ', qq_ID, ' 旧课表清楚成功')
        log.info(f'用户 <{qq_ID}> 旧课表清楚成功')
    else:
        # print('用户: ', qq_ID, ' 旧课表清楚失败')
        log.info(f'用户 <{qq_ID}> 旧课表清楚失败')
        return None

    cookie = automaticAcquisition_educationSystem_Cookie(qq_ID, database)
    if cookie:
        curriculum = set_curriculum(qq_ID, cookie, database)
        if curriculum:
            # print('用户: ', qq_ID, '更新课表成功')
            log.info(f'用户 <{qq_ID}> 更新课表成功')
            friend_sendMessage(qq_ID, "更新课表成功 ")
        else:
            # print('用户: ', qq_ID, '课表更新失败 get_curriculum执行失败')
            log.info(f'用户 <{qq_ID}> 课表更新失败 get_curriculum执行失败')
    else:
        friend_sendMessage(qq_ID, "课表更新失败 自动获取cookie失败")
        # print('用户: ', qq_ID, '更新课表失败 自动获取cookie失败')
        log.info(f'用户 <{qq_ID}> 更新课表失败 自动获取cookie失败')
    week = updateOrGetTeachingWeek(qq_ID, update=True)


# 查课表
def checkSchedule(qq_ID, message):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法查询课表')
        return None
    # 获取最新教学周
    commencementTime = updateOrGetTeachingWeek(qq_ID)
    if not commencementTime:
        # print('用户: ', qq_ID, ' 获取教学周失败')
        log.info(f'用户 <{qq_ID}> 获取教学周失败')
        return None
    days = (datetime.now().date() - commencementTime).days + 1
    SQL = "SELECT courseName,teacherName,class_nums,location,numberOfPeopleInClass " \
          "FROM course_tab " \
          "WHERE qq = %s and week_nums like %s and day_of_week = %s ORDER BY class_nums ASC;"
    messages = message.split(' ')
    # 指令参数不能大于3个
    if len(messages) >= 3:
        friend_sendMessage(qq_ID, '指令错误,请重试')
        return False
    # 指令带时间
    elif len(messages) == 2:
        date = messages[1]
        if date in ['明天', '后天', '往后天']:
            chart = {'明天': 1, '后天': 2, '往后天': 3}
            week_nums, day_of_week = get_teachingWeek(days + chart[date])
            data = (qq_ID, f'%,{week_nums},%', day_of_week)
        elif date in ['周一', '周二', '周三', '周四', '周五', '周六', '周日']:
            chart = {'周一': 1, '周二': 2, '周三': 3, '周四': 4, '周五': 5, '周六': 6, '周日': 7}
            week_nums, day_of_week = get_teachingWeek(days)
            data = (qq_ID, f'%,{week_nums},%', chart[date])
        else:
            friend_sendMessage(qq_ID, '时间参数错误,请重试')
            return None
    # 指令不带时间
    else:
        # now = datetime.now()
        # # 获取当前时间的小时和分钟
        # current_hour = now.hour
        # current_minute = now.minute
        # week_nums, day_of_week = get_teachingWeek(days)
        # data = (qq_ID, f'%,{week_nums},%', day_of_week)
        # execution = database.execution(SQL, data)
        # if execution:
        #

        week_nums, day_of_week = get_teachingWeek(days + 1)
        data = (qq_ID, f'%,{week_nums},%', day_of_week)

    # SQL += "and week_nums like %s and day_of_week = %s ORDER BY class_nums ASC;"
    execution = database.execution(SQL, data)
    if execution:
        friend_sendMessage(qq_ID, f"已经查询到了{date if len(messages) == 2 else '明天'} 的课表")
        sendInquirySchedule(qq_ID, execution)
    else:
        friend_sendMessage(qq_ID, f"{date if len(messages) == 2 else '明天'} 没有课程哦")


def sendInquirySchedule(qq_ID, result):
    for i in range(len(result)):
        courseName = result[i][0]
        teacherName = result[i][1]
        class_nums = result[i][2]
        location = result[i][3]
        numberOfPeopleInClass = result[i][4]
        capital = {'1': '第一教学楼', '2': '第二教学楼', '3': '第三教学楼', '4': '第四教学楼', '5': '第五教学楼',
                   '6': '第六教学楼',
                   '7': '第七教学楼', '8': '第八教学楼', '空': '无', '足': '足球场'}
        message = f"上课节数: {class_nums}   课程名: {courseName} \n" \
                  f"教师名: {teacherName}   上课人数: {numberOfPeopleInClass}\n" \
                  f"上课地点: {capital[location[0]]} 上课教室: {location}"
        friend_sendMessage(qq_ID, message)


# 更新或获取教学周
def updateOrGetTeachingWeek(qq_ID, update=False):
    if update:
        set_commencementTime(qq_ID, database)
        return None

    SQL = "SELECT commencement_time FROM user_tab where QQ = %s and commencement_time is not null;"
    data = (qq_ID)
    execution = database.execution(SQL, data)
    if not execution:
        # print('用户: ', qq_ID, ' 未设置教学周')
        log.info(f'用户 <{qq_ID}> 未设置教学周')
        friend_sendMessage(qq_ID, '未设置当前教学周')
        friend_sendMessage(qq_ID, '尝试自动设置教学周中')
        # print('用户: ', qq_ID, '尝试自动设置开学周')
        log.info(f'用户 <{qq_ID}> 尝试自动设置开学周')
        result = set_commencementTime(qq_ID, database)
        if result:
            friend_sendMessage(qq_ID, '自动设置教学周成功')
            # print('用户: ', qq_ID, '自动设置开学周成功')
            log.info(f'用户 <{qq_ID}> 自动设置开学周成功')
            return result
        else:
            friend_sendMessage(qq_ID, '自动设置教学周失败')
            return False
    else:
        # print('用户: ', qq_ID, ' 已设置开学周')
        log.info(f'用户 <{qq_ID}> 已设置开学周')
        return execution[0][0]


# 查询综测成绩
def queryComprehensiveTestResults(qq_ID, message):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法查询综测成绩')
        return None
    Activity_Cookie = automaticallyFetchActivity_Cookie(qq_ID, database)
    if not Activity_Cookie:
        print('用户: ', qq_ID, 'Activity_Cookie 获取失败')
        return None
    comprehensiveTestResults = get_activityQuery_Get(Activity_Cookie, 4)  # 获取综测成绩
    if not comprehensiveTestResults:
        print('用户: ', qq_ID, '获取综测成绩失败')
        friend_sendMessage(qq_ID, '获取综测成绩失败')
        return None
    comprehensiveTestResults = comprehensiveTestResults['data']
    messages = message.split(' ')
    if len(messages) >= 3:
        print('用户: ', qq_ID, '指令不正确')
        return None
    if len(messages) == 2:
        date = messages[1]  # 时间
        numberOfSemesters = len(comprehensiveTestResults)  # 学期数
        dates = {'大一上': 1, '大一下': 2, '大二上': 3, '大二下': 4, '大三上': 5, '大三下': 6, '大四上': 7, '大四下': 8}
        dates_t = {value: key for key, value in dates.items()}
        if date in dates:
            if dates[messages[1]] > numberOfSemesters:
                friend_sendMessage(qq_ID, f"综测成绩目前最大仅能查询到 {dates_t[numberOfSemesters]} 学期")
                return None
            timeTable = {'大一上': -2, '大一下': -1, '大二上': -4, '大二下': -3, '大三上': -6, '大三下': -5,
                         '大四上': -8, '大四下': -7}
            comprehensiveTestScoreData = comprehensiveTestResults[timeTable[messages[1]]]
            name = comprehensiveTestScoreData['XM']
            A_integral = comprehensiveTestScoreData['ALJF']
            B_integral = comprehensiveTestScoreData['BLJF']
            C_integral = comprehensiveTestScoreData['CLJF']
            D_integral = comprehensiveTestScoreData['DLJF']
            comprehensivePoints = comprehensiveTestScoreData['ZHCJ']
            schoolYear = comprehensiveTestScoreData['XN']
            semester = comprehensiveTestScoreData['XQ']
            message = f"{name} 同学 \n" \
                      f"你在{schoolYear}学年 第{semester}学期的综测成绩如下\n" \
                      f"A类积分: {A_integral} 分  B类积分: {B_integral} 分\n" \
                      f"C类积分: {C_integral} 分  D类积分: {D_integral} 分\n" \
                      f"综测成绩: {comprehensivePoints} 分"
            friend_sendMessage(qq_ID, message)


# 设置上课提醒是否开启
def set_course_Reminder(qq_ID, switch):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法进行设置上课提醒')
        return None
    if switch:
        SQL = "UPDATE user_tab SET course_Reminder = 1 where QQ = %s"

    else:
        SQL = "UPDATE user_tab SET course_Reminder = 0 where QQ = %s"

    data = (qq_ID)
    execution = database.execution(SQL, data)
    if execution:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}上课提醒')
        return None
    else:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}上课提醒设置失败')


def set_activity_Reminder(qq_ID, switch):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法进行设置活动提醒')
        return None
    if switch:
        SQL = "UPDATE user_tab SET activity_Reminder = 1 where QQ = %s"

    else:
        SQL = "UPDATE user_tab SET activity_Reminder = 0 where QQ = %s"

    data = (qq_ID,)
    execution = database.execution(SQL, data)
    if execution:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}活动提醒')
        return None
    else:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}活动提醒设置失败')


# 设置活动提醒类型
def set_activity_Reminder_type(qq_ID, message):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法进行设置活动提醒类型')
        return None
    messages = message.split(' ')
    if len(messages) != 2 or messages[1] == "":
        friend_sendMessage(qq_ID, '设置活动提醒类型失败,指令错误请重试')
        friend_sendMessage(qq_ID, '正确指令:设置活动提醒类型 [活动类型(ABCD)] 使用空格隔开\n')
        friend_sendMessage(qq_ID, '例:设置活动类型 AD')
        return None
    pattern = r"^(?!.*(.).*\1)[ABCDabcd]+$"
    match = re.match(pattern, messages[1])
    if not match:
        friend_sendMessage(qq_ID, '设置活动提醒类型失败,指令错误请重试')
        friend_sendMessage(qq_ID, '活动类型仅能为 ABCD (大小写不限,但不能重复)')

    SQL = "UPDATE user_tab SET activity_Reminder_type = %s WHERE QQ = %s ;"
    data = (messages[1].upper(), qq_ID)
    execution = database.execution(SQL, data)
    if not execution:
        friend_sendMessage(qq_ID, "数据库执行错误,设置活动提醒类型失败")
        return None
    else:
        friend_sendMessage(qq_ID, "设置活动提醒类型成功")
        return None


# 统计综测成绩
def statisticsComprehensiveTestResults(qq_ID, message):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法统计综测成绩')
        return None
    messages = message.split(' ')
    if len(messages) != 3 or messages[1] == "" or (not bool(re.match(r'^\d{4}-\d{4}$', messages[1]))):
        friend_sendMessage(qq_ID,
                           '指令错误!!!\n正确指令:统计综测成绩 [学年] [学期]\n例:统计综测成绩 2022-2023 第一学期')
        return None
    if messages[2] in ['第1学期', '第一学期', '上期', '上', '1']:
        messages[2] = '01'
    elif messages[2] in ['第2学期', '第二学期', '下期', '下', '2']:
        messages[2] = '02'
    else:
        friend_sendMessage(qq_ID, '学期指定错误')
        return None
    activity_cookie = automaticallyFetchActivity_Cookie(qq_ID, database)
    offlineActivity_data = get_activityQuery_Get(activity_cookie, 3)
    if not offlineActivity_data:
        friend_sendMessage(qq_ID, '线下活动首页数据获取失败请稍后重试')
        return None
    maxPage = offlineActivity_data['page']['maxPage']
    maxRowCount = offlineActivity_data['page']['maxRowCount']
    rowsPerPage = offlineActivity_data['page']['rowsPerPage']
    print(f'用户 {qq_ID} 共有 {maxPage}页 {maxRowCount}条数据,预计需要{2 * maxPage}秒')
    A_integral = 0
    B_integral = 0
    C_integral = 0
    D_integral = 0
    for index in range(1, maxPage + 1):
        activity_datas = get_activityQuery_Query(activity_cookie, 3, index)
        if not activity_datas:
            friend_sendMessage(qq_ID, '线下活动数据获取失败请稍后重试')
            return None
        for activity_data in activity_datas['data']:
            # print(activity_data)
            if activity_data['HDXN'].replace(' ', '') == messages[1] and activity_data['HDXQ'] == messages[2]:
                if activity_data['HDLB'] == '301':
                    A_integral += int(activity_data['HDXS'])
                elif activity_data['HDLB'] == '302':
                    B_integral += int(activity_data['HDXS'])
                elif activity_data['HDLB'] == '303':
                    C_integral += int(activity_data['HDXS'])
                elif activity_data['HDLB'] == '304':
                    D_integral += int(activity_data['HDXS'])
        # print(A_integral,B_integral,C_integral,D_integral)
        # return None
    comprehensiveTest_score = A_integral * 0.35 + B_integral * 0.3 + C_integral * 0.2 + D_integral * 0.15
    msg = (f"{messages[1]}学年 {('第一学期' if messages[2] == '01' else '第二学期')}\n"
           f"综测成绩为{comprehensiveTest_score}分\n"
           f"A类:{A_integral}分 B类:{B_integral}分\n"
           f"C类:{C_integral}分 D类:{D_integral}分")
    friend_sendMessage(qq_ID, msg)


# 群发消息
def groupMessage(qq_ID, message):
    sql = "select role from user_tab where QQ = %s;"
    execution = database.execution(sql, qq_ID)
    if execution:
        if execution[0][0] != '管理员':
            friend_sendMessage(qq_ID, "权限不足")
            return None
        messages = message.split(' ')
        if len(messages) != 2:
            friend_sendMessage(qq_ID, "指令错误")
            return None

        sql = 'select QQ from user_tab;'
        qq_IDs = database.execution(sql)
        for QQ in qq_IDs:
            if QQ[0] != qq_ID:
                friend_sendMessage(QQ[0], messages[1])
        friend_sendMessage(qq_ID, '群发消息完成')


# 查询已开启功能
def queryFunctionstatus(qq_ID):
    sql = (
        "select activity_reminder, activity_reminder_type, course_reminder, electric_reminder, electriccharge_reminder,"
        "automatic_Application,automatic_Application_type "
        "from user_tab "
        "where QQ = %s ;")
    data = (qq_ID,)
    execution = database.execution(sql, data)
    if execution:
        message = (f"上课提醒: {'开启' if execution[0][2] == 1 else '关闭'} \n"
                   f"活动提醒: {'开启' if execution[0][0] == 1 else '关闭'} \n"
                   f"活动提醒类型: {execution[0][1]}\n"
                   f"电费不足提醒: {'开启' if execution[0][3] == 1 else '关闭'} \n"
                   f"电费订阅提醒: {'开启' if execution[0][4] == 1 else '关闭'} \n"
                   f"自动申请活动: {'开启' if execution[0][5] == 1 else '关闭'} \n"
                   f"自动申请类型: {execution[0][6]}")
        friend_sendMessage(qq_ID, message)
    else:
        message = "未查询到你开启的任何功能"
        friend_sendMessage(qq_ID, message)


# 获取活动签到码
def get_activitySignInCode(qq_ID, message):
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法获取签退二维码')
        return
    # 消息参数分割
    messages = message.split(' ')
    if len(messages) != 2:
        friend_sendMessage(qq_ID, '发送的指令有误,参数数量错误')
        return None
    # 获取活动cookie
    cookie = automaticallyFetchActivity_Cookie(qq_ID, database)
    # 查询活动获取详细活动详情
    activityDetails_data = get_activityDetails_Query(cookie, messages[1])
    if activityDetails_data:
        # 获取签退码
        signBackCode_url = activityDetails_data[0].get('QTHDEWM')
        if signBackCode_url is None:
            friend_sendMessage(qq_ID, '获取活动签到码异常')
            return None
        friend_sendImage(qq_ID, signBackCode_url)
    else:
        friend_sendMessage(qq_ID, '获取活动签到码异常,请检查活动id是否正确')
        return None


# 添加日历
def addCalendarReminder(qq_ID, message):
    """ 添加日历 """
    pass


def set_automaticApplicationForActivities(qq_ID, switch=False):
    """ 自动申请活动 """
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法自动申请活动')
        return None
    if switch:
        SQL = "UPDATE user_tab SET automatic_Application = 1 where QQ = %s"

    else:
        SQL = "UPDATE user_tab SET automatic_Application = 0 where QQ = %s"

    data = (qq_ID,)
    execution = database.execution(SQL, data)
    if execution:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}自动申请活动')
        return None
    else:
        friend_sendMessage(qq_ID, f'已{"开启" if switch else "关闭"}自动申请活动')


def set_automaticApplicationForActivities_type(qq_ID, message):
    """设置自动申请活动类型"""
    user = database.get_UserPassword(qq_ID)
    if not user:
        friend_sendMessage(qq_ID, '未绑定智慧校园平台,无法设置自动活动申请类型')
        return
    messages = message.split(' ')
    # 检测参数是否合法
    if len(messages) > 2 or messages[1] not in ['线上', '不限']:
        friend_sendMessage(qq_ID, '参数错误:仅能设置为线上或不限')
        return None

    SQL = f"update user_tab set automatic_Application_type = %s where QQ = %s;"
    data = (messages[1], qq_ID)
    execution = database.execution(SQL, data)
    if execution:
        friend_sendMessage(qq_ID, '设置自动申请活动类型成功')
        return None
    else:
        friend_sendMessage(qq_ID, '设置自动申请活动类型失败')


def importEventReminders(qq_ID, message):
    pass


def manualExecution(qq_ID, message):
    """ 手动执行 """
    sql = "select role from user_tab where QQ = %s;"
    execution = database.execution(sql, qq_ID)
    if execution:
        if execution[0][0] != '管理员':
            friend_sendMessage(qq_ID, "权限不足")
            return None
        if len(message.split(' ')) < 3:
            friend_sendMessage(qq_ID, "指令错误")
            return None
        messages = message.split(' ', 3)

        sql = 'select QQ from user_tab;'
        qq_IDs = database.execution(sql)
        for QQ in qq_IDs:
            if QQ[0] == messages[1]:
                executeCommand(messages[1], messages[2])
                friend_sendMessage(qq_ID, '执行成功')
                return None
        friend_sendMessage(qq_ID, '错误,当前用户不存在')


def sendStartupMessage():
    sql = "select QQ from user_tab where role = '管理员' ;"
    execution = database.execution(sql)
    if execution:
        friend_sendMessage(execution[0][0], 'cqie_bot 已启动')
    else:
        log.info('用户列表无管理员,发送消息失败')


# 帮助
def CQIE_bot_help(qq_ID):
    message = "欢迎使用 CQIE_robot\n" \
              "目前支持的功能如下:" \
              "①查询电费: 查询电费 [寝室楼] [寝室号] \n" \
              "②查询课表: 查询课表 [时间] \n" \
              "③查询综测成绩: 查询综测成绩 [学期] "
    friend_sendMessage(qq_ID, message)


def testEquipment(message):
    messages = message.split(' ', 2)
    if messages[1] == '启动mqtt':
        threading.Thread(target=startMQTT).start()
        friend_sendMessage('3057466296', 'MQTT已启动')
    elif messages[1] == '关闭mqtt':
        closeMQTT()
        friend_sendMessage('3057466296', 'MQTT已关闭')
    elif messages[1] == '指令':
        sendCommand(messages[2])
    pass


def start_CQIE_bot():
    # 消息接收与处理线程
    messageProcessing = threading.Thread(target=messageProcessingThread)
    messageProcessing.start()
    # 定时任务线程
    timingTask = threading.Thread(target=timingTaskThread)
    timingTask.start()
    # 发送启动消息
    sendStartupMessage()


# 消息处理线程
def messageProcessingThread():
    # 定义服务器地址和端口
    server_address = ('', 5701)
    # 创建HTTP服务器实例，并设置请求处理器
    httpd = HTTPServer(server_address, MyRequestHandler)
    # 启动服务器
    log.info("Listening for POST requests on port 5701...")
    httpd.serve_forever()


# 定时任务线程
def timingTaskThread():
    timedTask_Start(database)


# 启动机器人
if __name__ == '__main__':
    start_CQIE_bot()
