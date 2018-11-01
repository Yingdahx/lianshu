from django.contrib import admin

# Register your models here.


from .models import *
from django import forms  
from django.contrib.auth.admin import UserAdmin  
admin.site.site_title = admin.site.site_header = '联数'

class Push_dataAdmin(admin.ModelAdmin):
    list_display = ('data_id','deveui','timestamp','devaddr','dataFrame','fcnt','port','rssi','snr','freq','devId',
    	'appId','sf_used','dr_used','cr_used','device_redundancy','time_on_air_ms','decrypted','status','address',
    	'name','longitude','latitude')

class Frame_dataAdmin(admin.ModelAdmin):
    list_display = ('data','decode_list','sta_id','status','count','manyi','action','get_time','online_time')

class ExtraPropertyAdmin(admin.ModelAdmin):
    list_display = ('data','devId','extra_id','name','value')

admin.site.register(Push_data,Push_dataAdmin)
admin.site.register(Gtw_info)
admin.site.register(ExtraProperty,ExtraPropertyAdmin)
admin.site.register(Station)
admin.site.register(Sensor)
admin.site.register(Frame_data,Frame_dataAdmin)

