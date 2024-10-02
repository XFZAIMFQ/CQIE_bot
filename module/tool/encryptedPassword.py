import base64
import hashlib

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad


def DES_encryption(password, key=None):
    if key is None:
        key = b'abcd1234'  # 加密的key
    cipher = DES.new(key, DES.MODE_ECB)  # 使用key生成密匙
    pwd_bytes = password.encode('utf-8')  # 将密码编码转换
    encrypted_bytes = cipher.encrypt(pad(pwd_bytes, DES.block_size))  # 使用密匙对密码进行加密
    encrypted_pwd = base64.b64encode(encrypted_bytes).decode()  # 将加密后的密码进行base64编码
    return encrypted_pwd


def paymentSystem_encryption(password):
    new_password = hashlib.md5(password.encode()).hexdigest()
    if len(new_password) > 5:
        new_password = new_password[:5] + "a" + new_password[5:]

    if len(new_password) > 10:
        new_password = new_password[:10] + "b" + new_password[10:]

    new_password = new_password[:-2]

    return new_password
