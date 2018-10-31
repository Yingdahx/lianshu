from django.test import TestCase

# Create your tests here.
import base64


a = 'TEqCAQAAAgAAAwAAEABDYoAAIBgQKRVWRDMAAAAAAACQAAAAAAAAAA=='
b = base64.b64decode(a.encode('utf-8')) #base64解码 16进制bytes
# b'LJ\x82\x01\x00\x00\x02\x00\x00\x03\x00\x00\x10\x00Cb\x80\x00 \x18\x10)\x15VD3\x00\x00\x00\x00\x00\x00\x90\x00\x00\x00\x00\x00\x00\x00'

c = [ int(hex(x),16) for x in b ]   #16进制字节码 转 字符串 放list内
# ['0x4c', '0x4a', '0x82', '0x1', '0x0', '0x0', '0x2', '0x0', '0x0', '0x3', '0x0', '0x0', '0x10', '0x0', '0x43', '0x4b', '0x66', '0x67', '0x20', '0x18', '0x10', '0x29', '0x17', '0x17', '0x33', '0x33', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x90', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0', '0x0']

d = [   _[2:]    for _ in c ]    #去掉头
# [
# 	'4c', '4a',     (设备标识）
# 	'82',           （满溢）
# 	'1', '0', '0',  1.0端口  状态正常 翻斗 计数 8 次
# 	'2', '0', '0',  1.1端口  状态正常 箱锁 计数 7 次 
# 	'3', '0', '0',  1.1端口  状态正常 推杆 计数 6 次
# 	'10', '0',      电源模块  状态正常
# 	'43', '4b',     当次推杆的电压值
# 	'66', '67',     当次推杆的电流峰值
# 	'20', '18', '10', '29', '17', '17', '33', 当前时间
# 	'33',           结束符 
# 	'0', '0', '0', '0', '0', '0', '90', '0', '0', '0', '0', '0', '0', '0'
# ]

# now_date = datetime.datetime(year=2018,month=10,
# 	day=30,hour=10,
# 	minute=10,second=20)