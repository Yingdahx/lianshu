# Generated by Django 2.0.5 on 2018-11-21 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lianshu_app', '0017_auto_20181121_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='push_data',
            name='device_redundancy',
            field=models.DecimalField(decimal_places=1, max_digits=10, verbose_name='device_redundancy'),
        ),
        migrations.AlterField(
            model_name='push_data',
            name='fcnt',
            field=models.DecimalField(decimal_places=1, max_digits=10, verbose_name='fcnt'),
        ),
        migrations.AlterField(
            model_name='push_data',
            name='port',
            field=models.DecimalField(decimal_places=1, max_digits=10, verbose_name='port'),
        ),
        migrations.AlterField(
            model_name='push_data',
            name='rssi',
            field=models.DecimalField(decimal_places=1, max_digits=10, verbose_name='信号强度'),
        ),
        migrations.AlterField(
            model_name='push_data',
            name='sf_used',
            field=models.DecimalField(decimal_places=1, max_digits=10, verbose_name='sf_used'),
        ),
        migrations.AlterField(
            model_name='push_data',
            name='snr',
            field=models.DecimalField(decimal_places=1, max_digits=19, verbose_name='信噪比'),
        ),
    ]
