# Generated by Django 2.0.5 on 2018-10-29 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lianshu_app', '0008_auto_20181029_1854'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='frame_data',
            options={'verbose_name': 'base64解析数据', 'verbose_name_plural': 'base64解析数据'},
        ),
        migrations.AlterModelOptions(
            name='push_data',
            options={'verbose_name': '接收数据(原数据)', 'verbose_name_plural': '接收数据(原数据)'},
        ),
        migrations.AlterField(
            model_name='frame_data',
            name='count',
            field=models.IntegerField(default=0, verbose_name='今天第几箱垃圾(暂时默认为0)'),
        ),
    ]
