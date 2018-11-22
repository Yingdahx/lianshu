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
        # url = "http://101.89.135.132/compressionstation/spillover/add/" #prod
        url = "http://101.89.135.80/compressionstation/spillover/add/"  #test

        #推送时间段内的数据
        res = []
        stas = Frame_data.objects.filter(online_time__range=(last_tuple,now_tuple))
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
        print('-----post station num :'+str(len(res))+'-----')

        # logger.debug('-----post data-----')
        # logger.debug('-----post station:'+str(len(res)))
        try :
            response = requests.post(url, data=json.dumps(res), headers=headers).text
            print('-----post success-----'+response)
        except Exception as e:
            print('-----post failed-----')
            print('-----error-----')
            print(e)
            print('----------')

            # logger.error('-----post failed-----')
            # logger.error(e)
        