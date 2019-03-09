from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from lianshu_app.models import *
from django.db.models import Count,Sum

import json
import random
import requests
import time,datetime
import base64
import logging
import struct
from pprint import pprint
#格林威治时间转换
def timechange(timestr):
    #'2018-10-26T06:25:04.845Z'
    #2019-03-03T05:59:43.755Z
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
    reslist = [ _[2:] for _ in strlist ]    #'0x'去掉头
    return reslist


@csrf_exempt
def push(request):
    #需求1 : 被动接收数据接口
    if request.method != 'POST':
        return JsonResponse({ 'success': False, 'code': -1, 'msg': '只支持POST' }, status=405)

    raw = json.loads(request.body.decode('utf-8'))
    print('开始保存原数据！')
    yuanshishuju(raw)
    print('保存原数据成功！')

    # json_root = settings.MEDIA_ROOT  + '%d.json' % time.time()  #json保存路径
    # with open(json_root, 'w') as f:
    #   f.write(json.dumps(raw))
    print('推送数据：',raw,sep='\n')
    #格林威治时间转为北京时区时间字串
    timestr = timechange(raw['timestamp'])

    data = Push_data.objects.filter(deveui=raw['deveui']).first()
    if not data:
        data = Push_data()
    data.data_id = raw['id']
    data.deveui = raw['deveui']
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
    try:
        data.save()
    except Exception as e:
        print('-----！！！存储出错！！！-----',e)
    print('原数据更新入库完成')
    
    #base64解码解析数据
    fram_list = base64_decode(raw['dataFrame'])
    print('解码后的字节码：',fram_list,sep='\n')

    #开始调用满溢度计算公式
    print('开始调用满溢度计算公式')
    try:
        get_manyi_value = get_manyi(raw['deveui'])
    except Exception as e:
        print('满溢度计算出错')

    print('满溢度计算完成')

    frame = Frame_data.objects.filter(machine_id=raw['deveui']).first()
    if not frame:
        frame = Frame_data()
    frame.data =  data
    frame.decode_list = str(fram_list)
    frame.count = raw['fcnt']                       #第几箱垃圾  暂用FCNT字段
    frame.manyi = get_manyi_value                #第2位 满溢度 
    frame.action = int('0x'+fram_list[5],16)     #第5位 翻斗次数 转回十进制
    #拼接 生成datetime
    # f_date = datetime.datetime(year=int(fram_list[18]+fram_list[19]),month=int(fram_list[20]),day=int(fram_list[21]),
    #     hour=int(fram_list[22]),minute=int(fram_list[23]),second=int(fram_list[24]))
    # #转成时间戳 float -> int
    # d_unix = time.mktime(f_date.timetuple())
    
    #str -> datetime -> float -> int 
    timestr = datetime.datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S')    
    on_date = time.mktime(timestr.timetuple())
    frame.get_time = str(int(on_date))
    frame.online_time = str(int(on_date))
    frame.sta_id = str(int('0x'+fram_list[0],16)) + str(int('0x'+fram_list[1],16)) #16进制转10进制->str存储
    frame.machine_id = raw['deveui']
    frame.status = int(fram_list[13])
    frame.save()
    print('转码后入库的信息:','满溢度',frame.manyi,'翻斗次数',int('0x'+fram_list[5],16),
        '设备标识',fram_list[0] +  fram_list[1],'状态',int(fram_list[13]),'base64解析入库完成',sep='\n')

    if 'gtw_info' in raw.keys() and raw['gtw_info']:
        print('gtw_info数据',raw['gtw_info'],sep='\n')
        for r in raw['gtw_info']:
            gtw = Gtw_info.objects.filter(data=data,gtw_id=r['gtw_id'],rssi=r['rssi'],snr=r['snr']).first()
            if not gtw:
                gtw = Gtw_info()
            gtw.data = data
            gtw.gtw_id = r['gtw_id']
            gtw.rssi = r['rssi']
            gtw.snr = r['snr']
            gtw.save()

    if 'ExtraProperty' in raw.keys() and raw['ExtraProperty']:
        print('ExtraProperty数据',raw['ExtraProperty'],sep='\n')
        for e in raw['ExtraProperty']:
            extra = ExtraProperty.objects.filter(data=data,devId=e['devId'],extra_id=e['id'],name=e['name'],value=e['value']).first()
            if not extra:
                extra = ExtraProperty()
            extra.data = data
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
    
    frame = Frame_data.objects.filter(machine_id=station_id).order_by('-online_time').first()
    if frame:
        ctx['code'] = 1
        ctx['data'] = res = {}
        res['station'] = int(frame.machine_id)    #小压站ID
        res['is_alive'] = frame.data.alive == str(True)  #设备是否在线 
        res['trunk_num'] = frame.count                   #今天第几箱垃圾                     
        res['spillover'] = frame.manyi                   #(当前箱垃圾的满溢度百分比) int (大于0小于100)   [2]
        res['operation_num'] =  frame.action             #(垃圾翻斗动作了几次) int                     [5]
        res['update_time'] = frame.get_time              #(上次收到数据的时间) int （unix 时间戳）       [18] [24]
        res['online_time'] = frame.online_time           #(设备上线时间) int （unix 时间戳） 
    else:
        ctx['code'] = 0
        ctx['message'] = '暂无该压站数据'

    return  JsonResponse(ctx,safe=False)


@csrf_exempt
def test(request):
    #需求3：15分钟推送定时任务测试
    #请求头
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        }
    #请求地址
    # url = "http://101.89.135.132/compressionstation/spillover/add/" #prod
    url = "http://101.89.135.80/compressionstation/spillover/add/"  #test

    #当前时间
    now = datetime.datetime.now() #datetime
    print('-----begin-----')
    print(now)
    #当前时间时间戳-15分钟前时间戳
    now_tuple = int(time.mktime(now.timetuple()))                 #datetime->时间戳
    last_tuple = now_tuple - 900                                    
    # last_date = time.localtime(last_tuple)                      #时间戳->datetime
    # last_str = time.strftime("%Y-%m-%d %H:%M:%S", last_date)    #datetime->字符串
    # nowstr = now.strftime("%Y-%m-%d %H:%M:%S")                  #datetime->字符串
    # 比对 nowstr 及 last_str 即可
    res = []
    stas = Frame_data.objects.filter(online_time__range=(last_tuple,now_tuple))
    print(stas)
    for sta in stas:
        pyload = {}
        pyload['station'] = sta.machine_id
        pyload['spillover'] = sta.manyi
        pyload['trunkNum'] = sta.count
        pyload['operationNum'] = sta.action
        pyload['refreshTime'] = sta.get_time
        pyload['onlineTime'] = sta.online_time
        #type字段暂时默认0
        pyload['sensors'] = [{'type':0,'status':str(sta.status),'rawdata':sta.data.dataFrame,'datatime':sta.data.timestamp}]
        res.append(pyload)
    print('-----post data-----')
    # print(json.dumps(pyload))
    # response = requests.post(url, data=json.dumps(pyload), headers=headers).text
    # print('------post response-----')
    # print(response)
    return JsonResponse(res,safe=False)

# post data :
# {  
#     "station": "xxx", 站标识（小站垃圾压缩设备无线监控系统提供相关小站检测数据上传到应用方数据系统）
#     "spillover": "80", 满溢度，百分比
#     "sensors": [       传感器列表
#         { 
#             "type": "0", 传感器类别（取值0~2，目前确定为3个传感器）
#             "status": "0", 正常，"1",非正常
#             "rawdata": "001", 数据采集的原始数据
#             "datatime": "2018-04-18 13: 01: 01" 数据采集的时间
#         }, 
#         { 
#             "type": "1", 传感器类别（取值0~2，目前确定为3个传感器）
#             "status": "0", 正常，"1",非正常
#             "rawdata": "002", 数据采集的原始数据
#             "datatime": "2018-04-18 13: 01: 01" 数据采集的时间
#         }, 
#         { 
#             "type": "2", 传感器类别（取值0~2，目前确定为3个传感器）
#             "status": "0", 正常，"1",非正常
#             "rawdata": "003", 数据采集的原始数据
#             "datatime": "2018-04-18 13: 01: 01" 数据采集的时间
#         }, 
#     ]  
# }

@csrf_exempt
def log_test(request):
    Push_data.objects.all().delete()
    Frame_data.objects.all().delete()
    # # logger = logging.getLogger("15") # django为loggers中定义的名称

    # try:
    #     a = []
    #     b = a[1]
    # except Exception as e:
    #     # logger.error(e) #此处捕获异常到15.log中去 
    #     print('-----Exception-----',e,'-------------------',sep='\n')
    #     #DEBUG，INFO，WARNING，ERROR，CRITICAL

    # #此处故意报错 15.log中并无该报错项记录，配置的test.log中有该行的报错记录
    # # return HttpRequest('test end') 
    return HttpResponse('test')


def yuanshishuju(raw):
    try:
        Bao_Wei.objects.create(bw_name='小压站', bw_input_txt=raw)
        
    except Exception as e:
        print(e)
        pass
    try:
        timestr = timechange(raw['timestamp'])
        Yaun_Push_data.objects.create(
            data_id = raw['id'],
            deveui = raw['deveui'],
            timestamp = timestr,
            devaddr = raw['devaddr'],
            dataFrame = raw['dataFrame'],
            fcnt = raw['fcnt'],
            port = raw['port'],
            rssi = raw['rssi'],
            snr = raw['snr'],
            freq = raw['freq'],
            devId = raw['devId'],
            appId = raw['appId'],
            sf_used = raw['sf_used'],
            dr_used = raw['dr_used'],
            cr_used = raw['cr_used'],
            device_redundancy = raw['device_redundancy'],
            time_on_air_ms = raw['time_on_air_ms'],
            decrypted = raw['decrypted'],
            status = raw['status'],
            address = raw['address'],
            name = raw['name'],
            longitude = raw['longitude'],
            latitude = raw['latitude'],
            alive = raw['live']
            )
    except Exception as e:
        Error.objects.create(error_id=raw['id'], error_address='保存原数据报错', error_bw=raw)
        print('Yaun_Push_data.create')
        pass
        

    try:
        #base64解码解析数据
        data = Yaun_Push_data.objects.filter(data_id=raw['id']).order_by('-create_time').first()
        if data:
            fram_list = base64_decode(raw['dataFrame'])
            # f_date = datetime.datetime(year=int(fram_list[18]+fram_list[19]),month=int(fram_list[20]),day=int(fram_list[21]),hour=int(fram_list[22]),minute=int(fram_list[23]),second=int(fram_list[24]))
            # d_unix = time.mktime(f_date.timetuple())
            timestr = datetime.datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S')    
            on_date = time.mktime(timestr.timetuple())
            Yaun_Frame_data.objects.create(
                data=data,
                decode_list=str(fram_list),
                count = raw['fcnt'],
                manyi = fram_list[2],
                action = int('0x'+fram_list[5],16),
                get_time = str(int(on_date)),
                online_time = str(int(on_date)),
                sta_id = str(int('0x'+fram_list[0],16)) + str(int('0x'+fram_list[1],16)),
                machine_id = raw['deveui'],
                status = int(fram_list[13])
                )
    except Exception as e:
        Error.objects.create(error_id=raw['id'], error_address='base64转码报错报错', error_bw=raw)
        print('Yaun_Frame_data.create')
        pass
        



hex_to_byte = lambda _: bytes.fromhex(_)
byte_to_hex = lambda _: ''.join([ "%02X" % x for x in _])
hex_to_json = lambda payload, *args: dict(zip([arg[0] for arg in args], [byte_to_hex(_) if not isinstance(_, int) else _ for _ in struct.unpack('>'+''.join([arg[1] for arg in args]), hex_to_byte(payload.replace(' ', '')))]))


#满溢度
def adjust(payload, *args):

    def parse(payload):
        return hex_to_json(payload.replace(' ', ''),
            ('LJ', '2s'),
            ('S', 'b'),
            ('N1', 'xh'),
            ('Lock', 'xh'),
            ('N2', 'xh'),
            ('Power', '2s'),
            ('V', 'h'),
            ('A', 'h'),
            ('t', '7s'),
            ('END', 'b')
        )
    p = parse(payload)

    c1 = (p['N1'] == 0)
    c2 = (p['N2'] == 0)
    c3 = (p['Lock'] == 0)

    for arg in args:
        p_check = parse(arg)

        c1 &= (p_check['N1'] == 0)
        c2 &= (p_check['N2'] == 0)
        c3 &= (p_check['Lock'] == 0)

    s = p['S']

    if c1 and not c2:
        s += min(p['N2'], 50) * adjust.P1

    elif c2 and not c1:
        s += min(p['N1'], 60) * adjust.P2

    elif c3 and p['N1'] > 60 and p['N2'] > 50:
        s -= min(p['N1'], 60) * adjust.P1
        s -= min(p['N2'], 50) * adjust.P2
        s += 60 * adjust.P1 + 50 * adjust.P2

    if s > 100:
        s = 100-16.18*(100.0/s)

    return s


def get_manyi(deveui):
    manyi_list = []

    frame = Yaun_Frame_data.objects.filter(machine_id=deveui).order_by('-data__create_time')[0:3]
    for x in frame:
        if x.decode_list:
            get_new_manyi = get_manyi_list(x.decode_list)
            if get_new_manyi:
                manyi_list.append(get_new_manyi)

    adjust.P1 = 0.7
    adjust.P2 = 0.15
    manyidu = 0
    # manyi_list =['4c 4a 54 01 00 9c 02 00 5c 03 00 00 10 00 56 95 1f b9 20 19 03 06 12 20 32 33', 
    # '4c 4a 54 01 00 9c 02 00 5c 03 00 00 10 00 56 95 1f b9 20 19 03 06 12 20 32 33',
    # '4c 4a 54 01 00 9c 02 00 5c 03 00 00 10 00 56 95 1f b9 20 19 03 06 12 20 32 33']
    if len(manyi_list) == 0:
        manyidu = 0
    elif len(manyi_list) == 1:
        manyidu = adjust(manyi_list[0])
    elif len(manyi_list) == 2:
        manyidu = adjust(manyi_list[0], manyi_list[1])
    elif len(manyi_list) == 3:
        manyidu = adjust(manyi_list[0], manyi_list[1], manyi_list[2])

    print(manyidu)
    return manyidu

import ast

#转成2进制
def  get_manyi_list(fram_list):
    list_list = ast.literal_eval(fram_list)
    manyi_list = ''
    for x in list_list:
        if len(x) == 1:
            x = '0' + x
        manyi_list = manyi_list +' '+ x

    return manyi_list







