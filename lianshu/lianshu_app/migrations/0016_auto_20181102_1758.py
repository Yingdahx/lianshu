# Generated by Django 2.0.5 on 2018-11-02 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lianshu_app', '0015_auto_20181102_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frame_data',
            name='count',
            field=models.IntegerField(default=0, verbose_name='今天第几箱垃圾(暂用fcnt字段)'),
        ),
    ]
