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
import random
import ast
from django.db.models import Q
#格林威治时间转换
def timechange(timestr):
    try:
        timestr = timestr.split('.')[0]
    except:
        print(timestr+'传入的格林威治时间字符串没有.字符分割')
        pass
    #str -> time -> list
    timetuple = time.strptime(timestr,'%Y-%m-%dT%H:%M:%S')
    timelist = list(timetuple)
    #时区与北京市区相差8小时 list -> time -> str
    # timelist[3] = timelist[3] + 8
    new_str = time.strftime('%Y-%m-%d %H:%M:%S',tuple(timelist))
    new_time = datetime.datetime.strptime(new_str, '%Y-%m-%d %H:%M:%S')
    print(new_time,'=======>>>>')
    time_jia = new_time + datetime.timedelta(hours=8)
    print(time_jia)
    new_str1 = str(time_jia)
    print(new_str1)
    return new_str1

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

    print('推送数据：',raw,sep='\n')
    #格林威治时间转为北京时区时间字串
    # timestr = timechange(raw['timestamp'])
    timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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
    data.appId = raw['appId']
    data.sf_used = raw['sf_used']
    data.dr_used = raw['dr_used']
    data.cr_used = raw['cr_used']
    data.device_redundancy = raw['device_redundancy']
    data.time_on_air_ms = raw['time_on_air_ms']
    data.decrypted = raw['decrypted']
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
    get_manyi_value = 0
    try:
        get_manyi_value = int(fram_list[2])
        # get_manyi_value = get_manyi(raw['deveui'])#计算满溢度
        # get_manyi_value = raw['deveui']
    except Exception as e:
        print('满溢度计算出错')
        frame_data_manyi = Frame_data.objects.filter(machine_id=raw['deveui']).first()
        get_manyi_value = frame_data_manyi.manyi if frame_data_manyi else 0

    print('满溢度计算完成', str(get_manyi_value))

    print('判断满溢度是否变化')
    # try:
    #     fandou = int('0x'+fram_list[5],16)#翻斗数
    #     # get_manyi_value = find_manyidu_value(raw['deveui'],get_manyi_value,fandou)
    # except Exception as e:
    #     get_manyi_value = 0
    #     print(e)
    print('判断结束')

    get_manyidu = Manyi.objects.filter(machine_id=raw['deveui']).order_by('-create_time').first()
    if get_manyidu:
        get_manyidu.zuizhong_manyidu = get_manyi_value
        get_manyidu.save()

    frame = Frame_data.objects.filter(machine_id=raw['deveui']).first()
    if not frame:
        frame = Frame_data()
    frame.data =  data
    frame.decode_list = str(fram_list)
    frame.count = raw['fcnt']                       #第几箱垃圾  暂用FCNT字段
    frame.manyi = int(get_manyi_value)                #第2位 满溢度 
    frame.action = int('0x'+fram_list[5],16)     #第5位 翻斗次数 转回十进制
    #拼接 生成datetime
    timestr = datetime.datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S')    
    on_date = time.mktime(timestr.timetuple())
    frame.get_time = str(int(on_date))
    frame.online_time = str(int(on_date))
    frame.sta_id = str(int('0x'+fram_list[0],16)) + str(int('0x'+fram_list[1],16)) #16进制转10进制->str存储
    frame.machine_id = raw['deveui']
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
            extra = ExtraProperty.objects.filter(data=data,extra_id=e['id'],name=e['name'],value=e['value']).first()
            if not extra:
                extra = ExtraProperty()
            extra.data = data
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

        try:
            xianyazhan_status = Xiaoyazhan.objects.filter(data_id=station_id).first()
            if xianyazhan_status:
                res['status'] = xianyazhan_status.status
            else:
                res['status'] = '维护表，不存在该小压站信息'
        except Exception as e:
            res['status'] = '维护表，不存在该小压站信息'
            pass

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
    # url = "http://101.89.135.80/compressionstation/spillover/add/"  #test
    url = "http://data.chi4rec.com.cn/compressionstation/spillover/add/"

    #当前时间
    now = datetime.datetime.now() #datetime
    print('-----begin-----')
    print(now)
    #当前时间时间戳-15分钟前时间戳
    now_tuple = int(time.mktime(now.timetuple()))                 #datetime->时间戳
    last_tuple = now_tuple - 900                                    

    res = []
    stas = Frame_data.objects.filter(online_time__range=(last_tuple,now_tuple))
    print(stas)
    for sta in stas:
        pyload = {}

        xianyazhan_status = Xiaoyazhan.objects.filter(data_id=sta.machine_id).first()
        if xianyazhan_status:
            pyload['status'] = xianyazhan_status.status
        else:
            pyload['status'] = '维护表，不存在该小压站信息'
        
        pyload['station'] = sta.machine_id
        pyload['spillover'] = sta.manyi
        pyload['trunkNum'] = sta.count
        pyload['operationNum'] = sta.action
        pyload['refreshTime'] = sta.get_time
        pyload['onlineTime'] = sta.online_time
        #type字段暂时默认0
        pyload['sensors'] = [{'type':0,'status':str(sta.status),'rawdata':sta.data.dataFrame,'datatime':sta.data.timestamp}]
        res.append(pyload)

        Push_history.objects.create(data_id=sta.machine_id, manyi=sta.manyi, time_update=now, bw=res)

    print('-----post data-----')

    return JsonResponse(res,safe=False)


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
        manyi = fram_list[2]
    except Exception as e:
        print(e)
        frame_data_manyi = Frame_data.objects.filter(machine_id=raw['deveui']).first()
        get_manyi_value = frame_data_manyi.manyi if frame_data_manyi else 0

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
            appId = raw['appId'],
            sf_used = raw['sf_used'],
            dr_used = raw['dr_used'],
            cr_used = raw['cr_used'],
            device_redundancy = raw['device_redundancy'],
            time_on_air_ms = raw['time_on_air_ms'],
            decrypted = raw['decrypted'],
            alive = raw['live']
            )
    except Exception as e:
        Error.objects.create(error_id=raw['id'], error_address='保存原数据报错', error_bw=raw)
        print('Yaun_Push_data.create')
        pass
    
    xiaozhan_status_list = Xiaoyazhan.objects.filter(data_id=raw['deveui']).first()
    if xiaozhan_status_list:
        print(xiaozhan_status_list.time_update)
        xiaozhan_status_list.time_update = datetime.datetime.now()
        xiaozhan_status_list.save()
        print(xiaozhan_status_list.time_update)
    else:
        Xiaoyazhan.objects.create(data_id=raw['deveui'])


    try:
        #base64解码解析数据
        data = Yaun_Push_data.objects.filter(data_id=raw['id']).order_by('-create_time').first()
        if data:
            fram_list = base64_decode(raw['dataFrame'])
            timestr = datetime.datetime.strptime(timestr,'%Y-%m-%d %H:%M:%S')    
            on_date = time.mktime(timestr.timetuple())
            Yaun_Frame_data.objects.create(
                data=data,
                decode_list=str(fram_list),
                count = raw['fcnt'],
                manyi = manyi,
                action = int('0x'+fram_list[5],16),
                get_time = str(int(on_date)),
                online_time = str(int(on_date)),
                sta_id = str(int('0x'+fram_list[0],16)) + str(int('0x'+fram_list[1],16)),
                machine_id = raw['deveui']
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

    Manyi.objects.create(machine_id=deveui, manyidu=manyidu, manyidu_list=manyi_list)
    return manyidu


#转成2进制
def  get_manyi_list(fram_list):
    list_list = ast.literal_eval(fram_list)
    manyi_list = ''
    for x in list_list:
        if len(x) == 1:
            x = '0' + x
        manyi_list = manyi_list +' '+ x

    return manyi_list



def find_manyidu_value(deveui,manyidu,fandou):
    #查询小压站表
    get_xiao_mianyidu = XiaoyazhanMainYidu.objects.filter(data_id=deveui).first()
    
    #有数据
    if get_xiao_mianyidu:

        if int(manyidu) == 0 and int(fandou)>0:
            if(fandou<=40):
                manyidu = random.randint(10,fandou*2)
            elif(fandou<80):
                manyidu = random.randint(10,fandou)
            else:
                manyidu = random.randint(10,80)

            get_xiao_mianyidu.update_time = datetime.datetime.now()
            get_xiao_mianyidu.manyi = manyidu
            get_xiao_mianyidu.save()
            return manyidu

        get_date_time = datetime.datetime.now() + datetime.timedelta(hours=-10)
        last_manyi = get_xiao_mianyidu.manyi_last.split(',')

        #获取上次应为随机生成满溢度的时间
        #在10小时以内，上次值和刚刚计算的值是一样的时候
        flag = False
        if get_xiao_mianyidu.last_time_update:
            last_time_update = datetime.datetime.strptime(get_xiao_mianyidu.last_time_update,'%Y-%m-%d %H:%M:%S')
            if get_date_time < last_time_update:
                flag = True

        flag1 = False
        if get_xiao_mianyidu.last_time_update:
            last_time_update = datetime.datetime.strptime(get_xiao_mianyidu.last_time_update,'%Y-%m-%d %H:%M:%S')
            if get_date_time > last_time_update:
                flag1 = True

        #当满溢度不等于时
        if flag and  len(last_manyi) == 2 and str(last_manyi[0]) == str(manyidu):
            manyidu = get_xiao_mianyidu.manyi

        elif str(manyidu) != str(get_xiao_mianyidu.manyi):
            #大于10小时，上次值相等时
            if flag1 and len(last_manyi) == 2 and str(last_manyi[0]) == str(manyidu):
                get_xiao_mianyidu.time_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')#修改时间
                get_xiao_mianyidu.last_time_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')#10小时值不变修改的时间
                if manyidu and manyidu >= 50:
                    manyidu = random.randint(0,49)
                else:
                    manyidu = random.randint(50,100)

                get_xiao_mianyidu.manyi_last = str(last_manyi[0]) + ',' + str(manyidu)#覆盖替换时的值
                get_xiao_mianyidu.manyi = manyidu

            else:
                get_xiao_mianyidu.time_update = datetime.datetime.now()
                get_xiao_mianyidu.manyi_last = str(get_xiao_mianyidu.manyi) + ',' + str(manyidu)#覆盖替换时的值
                get_xiao_mianyidu.manyi = manyidu

        else:
            time_update = datetime.datetime.strptime(get_xiao_mianyidu.time_update.split('.')[0],'%Y-%m-%d %H:%M:%S')
            if time_update < get_date_time:
                get_xiao_mianyidu.time_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')#修改时间
                get_xiao_mianyidu.last_time_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')#10小时值不变修改的时间

                if manyidu and manyidu >= 50:
                    manyidu = random.randint(0,49)
                else:
                    manyidu = random.randint(50,100)

                get_xiao_mianyidu.manyi_last = str(get_xiao_mianyidu.manyi) + ',' + str(manyidu)#覆盖替换时的值
                get_xiao_mianyidu.manyi = manyidu

        get_xiao_mianyidu.save()
    else:
        XiaoyazhanMainYidu.objects.create(
            data_id=deveui,
            manyi=manyidu,
            time_update=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            )
    return manyidu

    
from django.core.paginator import Paginator

@csrf_exempt
def get_xiaoyazhan(request):
    pagesize = int(request.POST.get('pagesize','10'))
    page = int(request.POST.get('page','1'))

    xiaoyazhan_list = Xiaoyazhan.objects.all()
    if request.method == 'POST':
        action = request.POST.get('action','')
        if action == 'search':
            name = request.POST.get('name','')
            xiaoyazhan_list = xiaoyazhan_list.filter(Q(data_id__icontains=name)|Q(name__icontains=name))
        elif action == 'update':
            id = request.POST.get('id','')
            xiaoyazhan_name = request.POST.get('xiaoyazhan_name','')
            address = request.POST.get('address','')
            status = request.POST.get('status','')
            get_update = xiaoyazhan_list.filter(id=id).first()
            if get_update:
                if xiaoyazhan_name:
                    get_update.name = xiaoyazhan_name
                if address:
                    get_update.address = address
                if status:
                    get_update.status = status
                get_update.save()


    paginator = Paginator(xiaoyazhan_list, pagesize) 
    try:
        xiaoyazhan_list = paginator.page(page)
    except EmptyPage:
        xiaoyazhan_list = paginator.page(paginator.num_pages)

    return render(request,'xiaoyazhan.html',locals())
