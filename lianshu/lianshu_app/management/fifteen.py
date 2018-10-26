from django.core.management.base import BaseCommand, CommandError
from lianshu_app.models import *
import requests,hashlib
from django.db.models import Model
from django.utils.timezone import now, timedelta
import datetime
import time


class Command(BaseCommand):
    help = '15minutes run'

    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
    	now = datetime.datetime.now()
    	print(now,'-----begin')
        nowstr = now.strftime("%Y-%m-%d %H:%M:%S")
	    headers = {
	        "Content-Type": "application/json; charset=UTF-8",
	        }
	    url = ""

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
	    print('post data-----',pyload)
	    response = requests.post(url, data=json.dumps(pyload), headers=headers).text
	    print('post response-----',response)