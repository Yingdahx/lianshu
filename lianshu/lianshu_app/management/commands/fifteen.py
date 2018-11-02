from django.core.management.base import BaseCommand, CommandError
from lianshu_app.models import *
import requests,hashlib
from django.db.models import Model
from django.utils.timezone import now, timedelta
import datetime
import time
import json
import logging


class Command(BaseCommand):
    help = '15minutes push-data'

    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        #日志记录器
        # logger = logging.getLogger('15')
        now = datetime.datetime.now() #datetime
        print('-----'+str(now)+'-----')
        print('-----post begin-----')
        # logger.info('-----'+str(now)+'-----')
        # logger.info('-----post begin-----')
        now_tuple = int(time.mktime(now.timetuple()))                 #datetime->时间戳
        last_tuple = now_tuple - 900                                  #15分钟前的时间戳   

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            }
        url = "http://101.89.135.132/compressionstation/spillover/add/"

        #推送时间段内的数据
        resp = {}
        resp['res']= res = []
        stas = Frame_data.objects.filter(online_time__range=(last_tuple,now_tuple)).values_list('sta_id').distinct()
        stas = list(stas)
        for sta in stas:
            datas = Frame_data.objects.filter(sta_id=sta[0],online_time__range=(last_tuple,now_tuple)).order_by('-online_time')
            i = 1
            pyload = {}
            pyload['sensors'] = sensors = []
            for _ in datas:
                if i:
                    pyload['station'] = _.sta_id
                    pyload['spillover'] = _.manyi
                    pyload['trunkNum'] = _.count
                    pyload['operationNum'] = _.action
                    pyload['refreshTime'] = _.get_time
                    pyload['onlineTime'] = _.online_time
                    i = 0
                sensor = {}
                sensor['type'] = '0' #暂时默认置0
                sensor['status'] = str(_.status)
                sensor['rawdata'] = _.data.dataFrame
                sensor['datatime'] = _.data.timestamp
                sensors.append(sensor)
            res.append(pyload)
        print('-----post data-----')
        print(resp)
        print('-----post station num :'+str(len(res))+'-----')

        # logger.debug('-----post data-----')
        # logger.debug('-----post station:'+str(len(res)))
        try :
            response = requests.post(url, data=json.dumps(resp), headers=headers).text
            print('-----post success-----'+response)
        except Exception as e:
            print('-----post failed-----')
            print('-----error-----')
            print(e)
            print('----------')

            # logger.error('-----post failed-----')
            # logger.error(e)
        