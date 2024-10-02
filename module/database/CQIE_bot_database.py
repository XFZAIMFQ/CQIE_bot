import configparser
import os
from threading import Lock

import pymysql

from module.tool.outputLog import log


class cqie_bot_database:
    __conn = None
    __host = ""
    __user = ""
    __password = ""
    __database = ""

    def __init__(self, host, user, password, database):
        self.__host = host
        self.__user = user
        self.__password = password
        self.__database = database
        self.__lock = Lock()

    def connection(self):
        try:
            # 创建数据库连接
            self.__conn = pymysql.connect(
                host=self.__host,
                user=self.__user,
                password=self.__password,
                database=self.__database
            )
            if self.__conn.open:
                # print("数据库连接成功")
                log.info("数据库连接成功")
                # self.__conn = conn
                return self.__conn
        except pymysql.Error as e:
            # 如果连接失败，输出错误信息
            # print("数据库连接失败：", e)
            log.error(f"数据库连接失败 {e}")
            return False

    def execution(self, query, data=None, conn=None, manyLines=False):
        with self.__lock:
            try:
                if conn is None:
                    # 创建游标对象
                    cursor = self.__conn.cursor()
                else:
                    cursor = conn.cursor()

                if data is None:
                    cursor.execute(query)
                else:
                    if manyLines:
                        cursor.executemany(query, data)
                    else:
                        cursor.execute(query, data)

                # 提交事务
                if conn is None:
                    self.__conn.commit()
                else:
                    conn.commit()

                # 检查是否为查询语句
                if query.lower().startswith("select"):
                    # 获取查询结果
                    result = cursor.fetchall()
                    return result
                else:
                    # 非查询语句执行成功
                    return True
            except Exception as e:
                # 发生异常时回滚事务
                if conn is None:
                    self.__conn.rollback()
                else:
                    conn.rollback()
                # print("执行失败:", str(e))
                log.error(f"执行失败:{str(e)}")
                return False
            finally:
                # 游标对象在最后关闭
                cursor.close()

    def get_UserPassword(self, qq_ID):
        """ 获得用户学号密码 """
        query = "SELECT * FROM user_tab where QQ = %s ;"
        data = (qq_ID,)
        result = self.execution(query, data)
        if result:
            studentID = result[0][1]
            password = result[0][2]
            return studentID, password
        else:
            return False

    def closeDatabase(self, conn=None):
        if conn == None:
            self.__conn.close()
        else:
            conn.close()


def database_init():
    config_file = 'cqie_bot.ini'
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        # 创建 ConfigParser 对象
        config = configparser.ConfigParser()
        # 添加初始配置项和值
        config['database_deploy'] = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root_password',
            'database_name': 'cqie_bot'
        }
        # 保存配置到文件
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        print("配置文件已创建并初始配置已保存")
        print("请重新运行")
        quit(0)
    else:
        # 创建 ConfigParser 对象
        config = configparser.ConfigParser()
        config.read(config_file)
        host = config.get('database_deploy', 'host')
        user = config.get('database_deploy', 'user')
        password = config.get('database_deploy', 'password')
        database_name = config.get('database_deploy', 'database_name')
        database = cqie_bot_database(host, user, password, database_name)  # 新建数据库对象
        database.connection()  # 连接数据库
        return database


database = database_init()
