from django.core.management.base import BaseCommand, CommandError
from lianshu_app.models import *
import requests,hashlib
from django.db.models import Model
from django.utils.timezone import now, timedelta
import datetime
import time
import json


class Command(BaseCommand):
    help = '15minutes push-data'

    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        now = datetime.datetime.now() #datetime
        print('-----post begin-----')
        print('-----post time:',now,'-----')
        now_tuple = int(time.mktime(now.timetuple()))                 #datetime->时间戳
        last_tuple = now_tuple - 900                                  #15分钟前的时间戳   

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            }
        url = "http://101.89.135.132/compressionstation/spillover/add/"

        #推送时间段内的数据
        resp = {}
        resp['res']= res = []
        stas = Frame_data.objects.filter(online_time__range=(last_tuple,now_tuple)).values_list('sta_id','manyi').distinct()
        stas = list(stas)
        for sta in stas:
            pyload = {}
            pyload['station'] = sta[0]
            pyload['spillover'] = sta[1]
            pyload['sensors'] = sensors = []
            datas = Frame_data.objects.filter(sta_id=sta[0],online_time__range=(last_tuple,now_tuple)).order_by('-online_time')
            for _ in datas:
                sensor = {}
                sensor['type'] = 0 #暂时默认置0
                sensor['status'] = _.status
                sensor['rawdata'] = _.data.dataFrame
                sensor['datatime'] = _.data.timestamp
                sensors.append(sensor)
            res.append(pyload)

        print('-----post data-----')
        print('-----post station:',len(res))
        try :
            response = requests.post(url, data=json.dumps(resp), headers=headers).text
            print('-----post success-----',response)
        except:
            response = requests.post(url, data=json.dumps(resp), headers=headers)
            print('-----post failed-----',response)
        