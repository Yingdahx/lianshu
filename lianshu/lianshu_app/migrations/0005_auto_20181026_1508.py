# Generated by Django 2.0.5 on 2018-10-26 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lianshu_app', '0004_auto_20180905_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push_data',
            name='decrypted',
            field=models.CharField(default='', max_length=200, verbose_name='是否解密(decrypted)'),
        ),
        migrations.AlterField(
            model_name='push_data',
            name='status',
            field=models.CharField(default='', max_length=200, verbose_name='是否在线(status)'),
        ),
    ]
