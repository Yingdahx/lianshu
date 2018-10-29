from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from lianshu_app.models import *

import json
import random
import requests
import time,datetime
import base64


#格林威治时间转换
def timechange(timestr):
    #'2018-10-26T06:25:04.845Z'
    try:
        timestr = timestr.split('.')[0]
    except:
        print(timestr+'传入的格林威治时间字符串没有.字符分割')
        pass
    #str -> time -> list
    timetuple = time.strptime(timestr,'%Y-%m-%dT%H:%M:%S')
    timelist = list(timetuple)
    #时区与北京市区相差8小时 list -> time -> str
    timelist[3] = timelist[3] + 8
    new_str = time.strftime('%Y-%m-%d %H:%M:%S',tuple(timelist))
    return new_str

def base64_decode(base64_str):
    enstr = base64.b64decode(base64_str.encode('utf-8'))  #base64解码 16进制bytes
    strlist = [ hex(x) for x in enstr ] 
    reslist = [   _[2:]    for _ in strlist ]    #去掉头
    return reslist


@csrf_exempt
def push(request):
    #需求1 : 被动接收数据接口
    if request.method != 'POST':
        return JsonResponse({ 'success': False, 'code': -1, 'msg': '只支持POST' }, status=405)

    raw = json.loads(request.body.decode('utf-8'))

    # json_root = settings.MEDIA_ROOT  + '%d.json' % time.time()  #json保存路径
    # with open(json_root, 'w') as f:
    #   f.write(json.dumps(raw))
    print('推送数据：',raw)

    data = Push_data()
    data.data_id = raw['id']
    data.deveui = raw['deveui']
    #格林威治时间转为北京时区时间字串
    timestr = timechange(raw['timestamp'])
    data.timestamp = timestr
    data.devaddr = raw['devaddr']
    data.dataFrame = raw['dataFrame']
    data.fcnt = raw['fcnt']
    data.port = raw['port']
    data.rssi = raw['rssi']
    data.snr = raw['snr']
    data.freq = raw['freq']
    data.devId = raw['devId']
    data.appId = raw['appId']
    data.sf_used = raw['sf_used']
    data.dr_used = raw['dr_used']
    data.cr_used = raw['cr_used']
    data.device_redundancy = raw['device_redundancy']
    data.time_on_air_ms = raw['time_on_air_ms']
    data.decrypted = raw['decrypted']
    data.status = raw['status']
    data.address = raw['address']
    data.name = raw['name']
    data.longitude = raw['longitude']
    data.latitude = raw['latitude']
    data.alive = raw['live']
    data.save()
    print('原数据入库完成')

    #base64解码解析数据
    fram_list = base64_decode(raw['dataFrame'])
    frame = Frame_data()
    frame.data =  Push_data.objects.filter(data_id=raw['id'],deveui = raw['deveui'],timestamp = timestr).first()
    frame.decode_list = str(fram_list)
    frame.count = 0   #第几箱垃圾  暂无解析字段
    frame.manyi = int(fram_list[2])      #第2位 满溢度
    frame.action = int(fram_list[5])     #第5位 翻斗次数
    #拼接 生成datetime
    f_date = datetime.datetime(year=int(fram_list[18]+fram_list[19]),month=int(fram_list[20]),day=int(fram_list[21]),
        hour=int(fram_list[22]),minute=int(fram_list[23]),second=int(fram_list[24]))
    #转成时间戳 float->int
    d_unix = time.mktime(f_date.timetuple())
    frame.get_time = int(d_unix)   
    #str -> datetime -> float -> int 
    timestr = datetime.datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S')    
    on_date = time.mktime(timestr.timetuple())
    frame.online_time = int(on_date)
    frame.save()
    print('base64解析入库完成')


    if 'gtw_info' in raw.keys() and raw['gtw_info']:
        for r in raw['gtw_info']:
            gtw = Gtw_info()
            gtw.data = Push_data.objects.filter(data_id=raw['id'],deveui = raw['deveui'],timestamp = timestr).first()
            gtw.gtw_id = r['gtw_id']
            gtw.rssi = r['rssi']
            gtw.snr = r['snr']
            gtw.save()

    if 'ExtraProperty' in raw.keys() and raw['ExtraProperty']:
        for e in raw['ExtraProperty']:
            extra = ExtraProperty()
            p_data = Push_data.objects.filter(data_id=raw['id'],deveui = raw['deveui'],timestamp = timestr).first()
            extra.data = p_data
            extra.devId = e['devId']
            extra.extra_id = e['id']
            extra.name = e['name']
            extra.value = e['value']
            extra.save()

    return JsonResponse({ 'success': True })

@csrf_exempt
def station(request):
    #需求2:单个小压站状态数据查询请求
    ctx = {}
    station_id = request.GET.get('station')
    print(station_id)
    station_id = float(station_id)
    
    frame = Frame_data.objects.filter(data__data_id=station_id).order_by('-online_time').first()
    ctx['station_id'] = frame.data.data_id        #小压站ID
    ctx['is_alive'] = frame.data.alive            #设备是否在线 
    ctx['trunk_num'] = frame.count                #今天第几箱垃圾                     
    ctx['spillover'] = frame.manyi                #(当前箱垃圾的满溢度百分比) int (大于0小于100)   [2]
    ctx['operation_num'] =  frame.action          #(垃圾翻斗动作了几次) int                     [5]
    ctx['update_time'] = frame.get_time           #(上次收到数据的时间) int （unix 时间戳）       [18] [24]
    ctx['online_time'] = frame.online_time        #(设备上线时间) int （unix 时间戳）            

    return  JsonResponse(ctx,safe=False)


@csrf_exempt
def push_station(request):
    #接收test推送的数据接口
    if request.method != 'POST':
        return JsonResponse({ 'success': False, 'code': -1, 'msg': '只支持POST' }, status=405)

    raw = json.loads(request.body.decode('utf-8'))
    action = Station.objects.get_or_create(station_id=raw['station'],spillover=raw['spillover'])
    station =  Station.objects.filter(station_id=raw['station'],spillover=raw['spillover']).first()
    sensors = raw['sensors']
    for sensor in sensors:
        new = Sensor()
        new.station = station
        new.sensor_type = sensor['type']
        new.status = sensor['status']
        new.rawdata = sensor['rawdata']
        new.datatime = sensor['datatime']
        new.save()
    return JsonResponse({ 'success': True })

@csrf_exempt
def test(request):
    #需求3：定时任务测试 每15分钟推送一次数据到指定url接口上
    now = datetime.datetime.now()
    print('-----begin-----')
    print(now)
    nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        }
    url = "http://101.89.135.132/compressionstation/spillover/add/"

    pyload = {}
    pyload['station'] = 'test'
    pyload['spillover'] = '80'
    pyload['sensors'] = sensors = []
    while len(sensors) < 3:
        sensor = {}
        sensor['type'] = len(sensors)
        sensor['status'] = '0'
        sensor['rawdata'] = '00' + str(len(sensors)+1)
        sensor['datatime'] = nowstr
        sensors.append(sensor)
    print('-----post data-----')
    print(json.dumps(pyload))
    response = requests.post(url, data=json.dumps(pyload), headers=headers).text
    print('------post response-----')
    print(response)
    return JsonResponse({ 'msg': 'success' })

# post data :
# {  
#   "station": "xxx", 站标识（小站垃圾压缩设备无线监控系统提供相关小站检测数据上传到应用方数据系统）
#   "spillover": "80", 满溢度，百分比
#   "sensors": [{ 传感器列表
#     "type": "0", 传感器类别（取值0~2，目前确定为3个传感器）
#     "status": "0", 正常，"1",非正常
#     "rawdata": "001", 数据采集的原始数据
#     "datatime": "2018-04-18 13: 01: 01" 数据采集的时间
#   }, { 
#     "type": "1", 传感器类别（取值0~2，目前确定为3个传感器）
#     "status": "0", 正常，"1",非正常
#     "rawdata": "002", 数据采集的原始数据
#     "datatime": "2018-04-18 13: 01: 01" 数据采集的时间
#   }, 
#  { 
#     "type": "2", 传感器类别（取值0~2，目前确定为3个传感器）
#     "status": "0", 正常，"1",非正常
#     "rawdata": "003", 数据采集的原始数据
#     "datatime": "2018-04-18 13: 01: 01" 数据采集的时间
#   }, 
# ]  
# }












