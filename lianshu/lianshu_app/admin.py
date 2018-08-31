from django.contrib import admin

# Register your models here.


from .models import *
from django import forms  
from django.contrib.auth.admin import UserAdmin  
admin.site.site_title = admin.site.site_header = '联数'

admin.site.register(Push_data)
admin.site.register(Gtw_info)
admin.site.register(ExtraProperty)
