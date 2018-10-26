from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from lianshu_app.models import *

import json
import random
import requests
import time,datetime


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


@csrf_exempt
def push(request):
    #被动接收的数据接口
    if request.method != 'POST':
        return JsonResponse({ 'success': False, 'code': -1, 'msg': '只支持POST' }, status=405)

    raw = json.loads(request.body.decode('utf-8'))
    data = Push_data()
    data.data_id = raw['id']
    data.deveui = raw['deveui']
    data.timestamp = timechange(raw['timestamp'])
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
    data.save()


    if 'gtw_info' in raw.keys() and raw['gtw_info']:
    	for r in raw['gtw_info']:
    		gtw = Gtw_info()
    		gtw.data = Push_data.objects.filter(data_id=raw['id'],deveui = raw['deveui'],timestamp = raw['timestamp']).first()
    		gtw.gtw_id = r['gtw_id']
    		gtw.rssi = r['rssi']
    		gtw.snr = r['snr']
    		gtw.save()

    if 'ExtraProperty' in raw.keys() and raw['ExtraProperty']:
    	for e in raw['ExtraProperty']:
    		extra = ExtraProperty()
    		extra.data = Push_data.objects.filter(data_id=raw['id'],deveui = raw['deveui'],timestamp = raw['timestamp']).first()
    		extra.save()

    return JsonResponse({ 'success': True })

@csrf_exempt
def station(request):
    #单个小压站状态数据请求
    ctx = {}
    station_id = request.GET.get('station')
    print(station_id)

    #模拟数据
    alives = [True,False]
    now = datetime.datetime.now()
    nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
    nowArray = time.strptime(nowstr, "%Y-%m-%d %H:%M:%S")
    timeStamp1 = int(time.mktime(nowArray))

    time2 = now + datetime.timedelta(days=-1)
    time2str = time2.strftime("%Y-%m-%d %H:%M:%S")
    time2Array = time.strptime(time2str,"%Y-%m-%d %H:%M:%S")
    time2Stamp2 = int(time.mktime(time2Array))
    
    ctx['station_id'] = int(float(station_id))    #小压站ID
    ctx['is_alive'] = alives[random.randint(0,1)] #设备是否在线 
    ctx['trunk_num'] = random.randint(0,5)        #今天第几箱垃圾
    ctx['spillover'] = random.randint(1,99)       #(当前箱垃圾的满溢度百分比) int (大于0小于100)
    ctx['operation_num'] = random.randint(0,20)   #(垃圾翻斗动作了几次) int
    ctx['update_time'] = timeStamp1               #(上次收到数据的时间) int （unix 时间戳）
    ctx['online_time'] = time2Stamp2              #(设备上线时间) int （unix 时间戳）

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
    #每15分钟推送一次数据到指定url接口上
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












