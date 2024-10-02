import base64
import re

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from module.tool.outputLog import log


# 解析课程时间地点 并将课程写入数据库
def analysisOfClassTimeAndPlace(timeAndLocation_str, QQ, courseName, teacherName, database):
    timeAndLocation_str = timeAndLocation_str.replace("\n", "")
    split = timeAndLocation_str.split('周')
    number = len(split) - 1
    datas = []
    weeks = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '日': 7, '[': 0}
    for i in range(number):
        if i == 0:
            classTime_location = split[i] + '周' + split[i + 1].split(',')[0]
        else:
            # classTime_location = split[i].split(',')[-1] + '周' + split[i + 1].split(',')[0]
            classTime_location = ",".join(split[i].split(",")[1:]) + '周' + split[i + 1].split(',')[0]
        # print(classTime_location)
        schoolWeek = []  # 上课周数
        if ',' in classTime_location:  # 处理带 ',' 的上课周数
            location_splits = classTime_location.split(',')
            location_splits[-1] = location_splits[-1].split('周')[0]
            for location_split in location_splits:
                if '-' in location_split:
                    start, end = location_split.split('-')
                    schoolWeek.extend(range(int(start), int(end) + 1))
                else:
                    schoolWeek.append(int(location_split))
        else:  # 处理不带 ',' 的上课周数
            week = classTime_location.split('周')[0]
            if '-' not in week:  # 仅有一周
                schoolWeek.append(int(week))
            else:
                start, end = week.split('-')
                start = int(start)
                end = int(end)
                if '单' in classTime_location:  # 范围内是单周
                    if start % 2 == 0:
                        start += 1
                    schoolWeek.extend(range(start, end + 1, 2))
                elif '双' in classTime_location:
                    if start % 2 == 1:
                        start += 1
                    schoolWeek.extend(range(start, end + 1, 2))
                else:
                    schoolWeek.extend(range(start, end + 1))
        classTime_locations = classTime_location.split(' ')
        schoolday = weeks[classTime_locations[1][0]]  # 上课日
        numberoflessons = classTime_locations[1].split('[')[1].split(']')[0]  # 上课节数
        classLocations = '空'
        numberOfPeopleInClass = '无'
        if len(classTime_locations) == 3 and classTime_locations[2] != '':
            classLocations = classTime_locations[2].split('(')[0]
            numberOfPeopleInClass = classTime_locations[2].split('(')[1].split(')')[0]
        # print(f"上课周: {schoolWeek} 上课日:星期{schoolday} 上课节数:{numberoflessons} 上课地点:{classLocations} 上课人数:{numberOfPeopleInClass}")
        week_nums = "," + ",".join(map(str, schoolWeek)) + ","  # 上课周数
        data = (
            QQ, courseName, teacherName, week_nums, schoolday, classLocations, numberoflessons, numberOfPeopleInClass)
        datas.append(data)
    insert = "insert into course_tab (QQ,courseName, teacherName, week_nums, day_of_week, location, class_nums,numberOfPeopleInClass) " \
             "values (%s,%s,%s,%s,%s,%s,%s,%s);"
    execution = database.execution(insert, datas, manyLines=True)
    if execution:
        # print(datas, '插入成功')
        log.info(f'{datas} 插入成功')
    else:
        # print(datas, '插入失败')
        log.info(f'{datas} 插入失败')


# 获取 userCode 学年 学期
def get_currentSemester(cookie):
    url = "http://jw.cqie.edu.cn/jw/common/showYearTerm.action"
    headers = {
        "Accept": "text/plain, */*; q=0.01",
        "Cookie": cookie,
        "X-Requested-With": "XMLHttpRequest"
    }
    response = requests.post(url, headers=headers, allow_redirects=False)

    if response.status_code == 302:
        # 请求失败
        # print("get_currentSemester 请求失败，状态码: ", response.status_code)
        log.info(f"get_currentSemester 请求失败，状态码 {response.status_code}")
        return False
    if response.headers['Content-Type'].split(';')[0] == 'text/html':
        # print("get_currentSemester 请求失败, Content-Type: text/html  Cookie已过期")
        log.info("get_currentSemester 请求失败, Content-Type: text/html  Cookie已过期")
        return False
    # 请求成功，你可以根据需要处理响应结果
    # print(response.text)
    semester = response.json()
    if semester:
        userCode = semester['userCode']
        xn = semester['xn']
        xq = semester['xqM']
        return userCode, xn, xq
    else:
        # print('get_currentSemester 响应内容非json')
        log.info('get_currentSemester 响应内容非json')
        return False

# 设置或更新课程
def set_curriculum(qq_ID, cookie, database):
    semester = get_currentSemester(cookie)
    if semester:
        zh = semester[0][:2] + f'{int(semester[0][2]) + 1}' + semester[0][3:]
        queryParameters = f'xn={semester[1]}&xq={semester[2]}&zh={zh}'
    else:
        return False

    encoded_bytes = base64.b64encode(queryParameters.encode("utf-8"))
    encoded_string = encoded_bytes.decode("utf-8")

    url = "http://jw.cqie.edu.cn/wsxk/xkjg.ckdgxsxdkchj_data10319.jsp"
    headers = {"Cookie": cookie,
               "Referer": "http://jw.cqie.edu.cn//student/xkjg.wdkb.jsp?menucode=S20301"}
    params = {"params": encoded_string}
    # print(encoded_string)

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 302:
        # print("get_curriculum 请求失败，状态码: ", response.status_code)
        log.info(f"get_curriculum 请求失败，状态码 {response.status_code}")
        return False

    soup = BeautifulSoup(response.text, "html.parser")
    find_all = soup.find_all('tr')[1:]
    # start = time.perf_counter()

    for finds in find_all:
        informations = finds.find_all("td")
        courseName = informations[1].text.strip().split(']')[1]
        teacherName = informations[5].text.strip().split(']')[1]
        classTimeAndPlace = informations[8].text.strip()
        analysisOfClassTimeAndPlace(classTimeAndPlace, qq_ID, courseName, teacherName, database)

    return True
    # end = time.perf_counter()
    # runTime = end - start
    # print("运行时间：", runTime)


# 获得当前教学周
def get_currentWeek(cookie):
    url = 'http://jw.cqie.edu.cn/frame14/DeskStu.v14.jsp'
    headers = {
        'Cookie': cookie
    }
    response = requests.get(url, headers=headers, allow_redirects=False)

    pattern = r'var dqjxz = (.*?);'
    match = re.search(pattern, response.text)
    if match:
        week = match[0].split('"')[1].split('"')[0]
        return int(week)
    else:
        # print('未知原因,获取当前教学周失败')
        log.info('未知原因,获取当前教学周失败')
        return False

# 设置开学时间
def set_commencementTime(qq_ID, database):
    from module.educationSystem import automaticAcquisition_educationSystem_Cookie
    cookie = automaticAcquisition_educationSystem_Cookie(qq_ID, database)
    if cookie:
        week = get_currentWeek(cookie)

        specified_date = datetime.now()
        # 计算向前推的天数
        delta_days = (week - 1) * 7
        # 计算指定日期的上一周的日期
        previous_week_date = specified_date - timedelta(days=delta_days)
        # 找到指定日期所在周的星期一日期
        monday_date = previous_week_date - timedelta(days=previous_week_date.weekday())
        # query = "SELECT * FROM user_tab WHERE QQ = %s;"
        # data = (qq_ID)
        # execution = database.execution(query, data)
        # if not execution:
        #     SQL = "insert into user_tab (commencement_Time,QQ) values (%s,%s);"
        # else:
        #     SQL = "UPDATE user_tab SET commencement_Time = %s WHERE QQ = %s ;"
        SQL = "UPDATE user_tab SET commencement_Time = %s WHERE QQ = %s ;"

        data = (monday_date, qq_ID)
        execution = database.execution(SQL, data)
        if execution:
            # print('用户: ', qq_ID, ' 数据库更新更新开学日期成功')
            log.info(f'用户 {qq_ID} 数据库更新更新开学日期成功')
            return monday_date
        else:
            # print('用户: ', qq_ID, ' 数据库更新更新开学日期失败')
            log.info(f'用户 {qq_ID} 数据库更新更新开学日期失败')
            return False


# 将时间转化成 教学周
def get_teachingWeek(days):
    week_day = days % 7 if days % 7 != 0 else 7  # 当前的星期
    now_week = int(days / 7) + 1 if days % 7 != 0 else int(days / 7)  # 现在的教学周
    return now_week, week_day


# def init():
#     from CQIE_bot_database import cqie_bot_database
#     database = cqie_bot_database("localhost", "root", "admin", "schoolactivities")  # 新建数据库对象
#     database.connection()  # 连接数据库
#     return database


