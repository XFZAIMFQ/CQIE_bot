import json
import threading
import time

import paho.mqtt.client as mqtt

from module.go_cqhttp import friend_sendMessage
from module.tool import log

connectionParameters = {"clientId": "k0b73dtB4Hf.Cqie_bot|securemode=2,signmethod=hmacsha256,timestamp=1697035237293|",
                        "username": "Cqie_bot&k0b73dtB4Hf",
                        "mqttHostUrl": "iot-06z00g57nytw674.mqtt.iothub.aliyuncs.com",
                        "passwd": "d4497829a3048ef2c65df2990089a2945cc4032ca97713fdd8337f2fcc9f3768", "port": 1883}

client = mqtt.Client()
temperature = None
humidity = None


def on_connect(client, userdata, flags, rc):
    rc_status = ["连接成功", "协议版本错误", "无效的客户端标识", "服务器无法使用", "用户密码错误", "无授权"]
    log.info(f"Mqtt {rc_status[rc]}")
    # print("connect：", "Mqtt"+rc_status[rc])


def test(to_mqtt):
    to_mqtt.publish('/k0b73dtB4Hf/Cqie_bot/user/TX', 'on LED1', qos=0)  # 发布消息
    time.sleep(1)
    to_mqtt.publish('/k0b73dtB4Hf/Cqie_bot/user/TX', 'off LED1', qos=0)  # 发布消息
    time.sleep(1)
    to_mqtt.publish('/k0b73dtB4Hf/Cqie_bot/user/TX', 'on LED1', qos=0)  # 发布消息
    time.sleep(1)
    to_mqtt.publish('/k0b73dtB4Hf/Cqie_bot/user/TX', 'off LED1', qos=0)  # 发布消息


def connectToMQTT(connectionParameters):
    global client
    client = mqtt.Client(client_id=connectionParameters.get('clientId'))
    client.on_connect = on_connect  # 注册返回连接状态的回调函数
    client.on_message = on_message  # 定义接收消息回调函数
    client.username_pw_set(connectionParameters.get('username'), connectionParameters.get('passwd'))
    # client.will_set("test/die", "我死了", 0)  # 设置遗嘱消息
    client.connect(connectionParameters.get('mqttHostUrl'), connectionParameters.get('port'),
                   keepalive=600)  # 连接服务器
    # client.loop_forever()
    # client.loop_start()
    return client


def on_message(client, userdata, msg):
    log.info(f"接收到主题：{str(msg.topic)}")
    log.info(f"消息：{str(msg.payload, 'utf-8')}")
    message = str(msg.payload, 'utf-8')
    date = json.loads(message)
    if 'temperature' in message:
        friend_sendMessage("3057466296",
                           f'已获取到温湿度信息\n温度: {date.get("temperature")}℃ 湿度: {date.get("humidity")}%')
    elif 'message' in message:
        friend_sendMessage("3057466296", date.get('message'))


def startMQTT():
    global client
    client = connectToMQTT(connectionParameters)
    client.subscribe('/k0b73dtB4Hf/Cqie_bot/user/RX', qos=0)  # 订阅主题test/#
    # client.unsubscribe('/k0b73dtB4Hf/Cqie_bot/user/TX')  # 取消订阅
    client.loop_forever()
    # client.loop_start()


def closeMQTT():
    client.disconnect()


def sendCommand(instruction):
    client.publish('/k0b73dtB4Hf/Cqie_bot/user/TX', instruction, qos=0)

# if __name__ == '__main__':
#     threading.Thread(target=startMQTT).start()
#     time.sleep(2)
