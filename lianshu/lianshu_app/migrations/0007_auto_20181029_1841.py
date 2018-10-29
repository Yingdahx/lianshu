# Generated by Django 2.0.5 on 2018-10-29 10:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lianshu_app', '0006_auto_20181029_1506'),
    ]

    operations = [
        migrations.CreateModel(
            name='Frame_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decode_list', models.CharField(default='', max_length=200, verbose_name='解码字符串list')),
                ('count', models.IntegerField(default=0, verbose_name='今天第几箱垃圾')),
                ('manyi', models.IntegerField(default=0, verbose_name='设备满溢参数')),
                ('action', models.IntegerField(default=0, verbose_name='垃圾翻斗动作次数')),
                ('get_time', models.IntegerField(default=0, verbose_name='上次收到数据时间')),
                ('online_time', models.IntegerField(default=0, verbose_name='设备上线时间')),
            ],
            options={
                'verbose_name': '接受数据对应的解码数据',
                'verbose_name_plural': '接受数据对应的解码数据',
            },
        ),
        migrations.AddField(
            model_name='push_data',
            name='alive',
            field=models.CharField(default='', max_length=200, verbose_name='是否在线'),
        ),
        migrations.AddField(
            model_name='push_data',
            name='data_hex',
            field=models.CharField(default='', max_length=200, verbose_name='解码处理后的16字节list字符串'),
        ),
        migrations.AlterField(
            model_name='push_data',
            name='status',
            field=models.CharField(default='', max_length=200, verbose_name='status'),
        ),
        migrations.AddField(
            model_name='frame_data',
            name='data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lianshu_app.Push_data', verbose_name='绑定数据'),
        ),
    ]
