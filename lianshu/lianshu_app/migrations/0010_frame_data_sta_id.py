# Generated by Django 2.0.5 on 2018-10-30 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lianshu_app', '0009_auto_20181029_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='frame_data',
            name='sta_id',
            field=models.CharField(default='', max_length=20, verbose_name='设备标识'),
        ),
    ]
