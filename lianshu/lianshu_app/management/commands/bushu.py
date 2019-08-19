from django.core.management.base import BaseCommand, CommandError
from lianshu_app.models import *
import requests,hashlib
from django.db.models import Model
from django.utils.timezone import now, timedelta
import datetime
import time
import json
import logging
from lianshu_app import views as v

class Command(BaseCommand):
    help = '15minutes push-data'

    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        now = datetime.datetime.now() #datetime
        print('-----'+str(now)+'-----')
        print('-----post begin-----')
        # logger.info('-----'+str(now)+'-----')
        # logger.info('-----post begin-----')
        # now_tuple = int(time.mktime(now.timetuple()))                 #datetime->时间戳
        # last_tuple = now_tuple - 900                                  #15分钟前的时间戳   

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            }
        # url = "http://101.89.135.132/compressionstation/spillover/add/" #prod
        url = "http://data.chi4rec.com.cn/compressionstation/spillover/add/"  #test

        #推送时间段内的数据
        res = []
        get_bao_list = Bao_Wei.objects.filter(create_time__range=('2019-08-15 00:00','2019-08-19 00:00')).order_by('create_time')
        for x in get_bao_list:
            pyload = {}
            if x.bw_input_txt:
                if x.bw_input_txt:
                    raw = eval(x.bw_input_txt)
                    xianyazhan_status = Xiaoyazhan.objects.filter(data_id=int(raw['deveui'])).first()
                    if xianyazhan_status:
                        pyload['status'] = xianyazhan_status.status
                    else:
                        pyload['status'] = '维护表，不存在该小压站信息'

                    #开始调用满溢度计算公式
                    try:
                        get_manyi_value = v.get_manyi(raw['deveui'])#计算满溢度
                        
                    except Exception as e:
                        print('-----失败了-----')
                        get_manyi_value = 0

                    try:
                        fandou = int('0x'+fram_list[5],16)#翻斗数
                        get_manyi_value = v.find_manyidu_value(raw['deveui'],get_manyi_value,fandou)
                    except Exception as e:
                        get_manyi_value = 0
                    

                    fram_list = v.base64_decode(raw['dataFrame'])
                    pyload['station'] = int(raw['deveui'])
                    pyload['spillover'] = get_manyi_value
                    pyload['trunkNum'] = raw['fcnt']
                    pyload['operationNum'] = int('0x'+fram_list[5],16)
                    pyload['refreshTime'] = time.mktime(x.create_time.timetuple())
                    pyload['onlineTime'] = time.mktime(x.create_time.timetuple())
                    pyload['sensors'] = [{'type':0,'status':str('1'),'rawdata':raw['dataFrame'],'datatime':x.create_time.strftime('%Y-%m-%d %H:%M:%S')}]
                    res.append(pyload)
            try :
                response = requests.post(url, data=json.dumps(res), headers=headers).text
                if 'Success' in response:
                    pass
                else:
                    Error.objects.create(error_id=now, error_address='推送不成功', error_bw=response)
                print('-----post success-----'+response)
            except Exception as e:
                print('-----post failed-----')
                print(e)
                print('----------')
                Error.objects.create(error_id=now, error_address='推送数据失败', error_bw=response)
            print('==============>>>'+ str(x.create_time))
            Error.objects.create(error_id=now, error_address='补数据', error_bw=x.create_time)

