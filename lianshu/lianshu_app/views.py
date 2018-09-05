from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from lianshu_app.models import *

import json
import random
import time,datetime

@csrf_exempt
def push(request):

    if request.method != 'POST':
        return JsonResponse({ 'success': False, 'code': -1, 'msg': '只支持POST' }, status=405)

    raw = json.loads(request.body.decode('utf-8'))
    data = Push_data()
    data.data_id = raw['id']
    data.deveui = raw['deveui']
    data.timestamp = raw['timestamp']
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

    if raw['gtw_info']:
    	for r in raw['gtw_info']:
    		gtw = Gtw_info()
    		gtw.data = Push_data.objects.filter(data_id=raw['id'],deveui = raw['deveui'],timestamp = raw['timestamp']).first()
    		gtw.gtw_id = r['gtw_id']
    		gtw.rssi = r['rssi']
    		gtw.snr = r['snr']
    		gtw.save()

    if raw['ExtraProperty']:
    	for e in raw['ExtraProperty']:
    		extra = ExtraProperty()
    		extra.data = Push_data.objects.filter(data_id=raw['id'],deveui = raw['deveui'],timestamp = raw['timestamp']).first()
    		extra.save()

    return JsonResponse({ 'success': True })

@csrf_exempt
def station(request):
    ctx = {}
    station_id = request.GET.get('station_id')
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
    
    ctx['station_id'] = int(station_id)
    ctx['is_alive'] = alives[random.randint(0,1)]
    ctx['trunk_num'] = random.randint(0,5)
    ctx['capacity'] = random.randint(1,99)
    ctx['operation_num'] = random.randint(0,20)
    ctx['update_time'] = timeStamp1
    ctx['online_time'] = time2Stamp2

    return  JsonResponse(ctx,safe=False)











