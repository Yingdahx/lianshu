from django.db import models

class Push_data(models.Model):
	class Meta:
		verbose_name = verbose_name_plural = '接收数据(原数据)'

	#DecimalField类型max_digits-总位数，decimal_places-小数点后精确位数
	data_id = models.DecimalField(max_digits=20,decimal_places=1,verbose_name='ID')
	deveui = models.CharField(max_length=200,default='',verbose_name='设备的EUI')
	timestamp = models.CharField(max_length=200,default='',verbose_name='数据上报时间')
	devaddr = models.DecimalField(max_digits=20,decimal_places=1,verbose_name='设备物理地址')
	dataFrame = models.CharField(max_length=200,default='',verbose_name='设备业务原始数据(Base64编码)')
	fcnt = models.DecimalField(max_digits=5,decimal_places=1,verbose_name='fcnt')
	port = models.DecimalField(max_digits=5,decimal_places=1,verbose_name='port')
	rssi = models.DecimalField(max_digits=5,decimal_places=1,verbose_name='信号强度')
	snr = models.DecimalField(max_digits=5,decimal_places=1,verbose_name='信噪比')
	freq = models.DecimalField(max_digits=20,decimal_places=1,verbose_name='freq')
	devId = models.CharField(max_length=200,default='',verbose_name='devId')
	appId = models.CharField(max_length=200,default='',verbose_name = '应用编号')
	sf_used = models.DecimalField(max_digits=5,decimal_places=1,verbose_name = 'sf_used')
	dr_used = models.CharField(max_length=200,default='',verbose_name = 'dr_used')
	cr_used = models.CharField(max_length=200,default='',verbose_name = 'cr_used')
	device_redundancy = models.DecimalField(max_digits=5, decimal_places=1,verbose_name = 'device_redundancy')#冗余
	time_on_air_ms = models.DecimalField(max_digits=10, decimal_places=3,verbose_name = 'time_on_air_ms')
	decrypted = models.CharField(max_length=200,default='',verbose_name = '是否解密(decrypted)') #
	status = models.CharField(max_length=200,default='',verbose_name = 'status')
	address = models.CharField(max_length=200,default='',verbose_name = 'address')
	name = models.CharField(max_length=200,default='',null=True,verbose_name = 'name')
	longitude = models.DecimalField(max_digits=15,decimal_places=1,verbose_name = 'longitude')
	latitude = models.DecimalField(max_digits=15,decimal_places=1,verbose_name = 'latitude')
	alive = models.CharField(max_length=200,default='',verbose_name='是否在线')
	data_hex = models.CharField(max_length=200,default='',verbose_name='解码处理后的16字节list字符串')

	def __str__(self):
		return 'ID:' + str(self.data_id) + '     设备的EUI:' + self.deveui + '     数据上报时间' + self.timestamp 

class Gtw_info(models.Model):
	class Meta:
		verbose_name = verbose_name_plural = 'gtw_info'

	data = models.ForeignKey(Push_data,on_delete=models.CASCADE,verbose_name='绑定数据')
	gtw_id = models.CharField(max_length=200,default='',verbose_name = 'gtw_id')
	rssi = models.DecimalField(max_digits=5,decimal_places=1,verbose_name = 'rssi')
	snr = models.DecimalField(max_digits=5,decimal_places=1,verbose_name = 'snr')

	def __str__(self):
		return 'gtw_id:' + self.gtw_id + '     绑定数据:' + str(self.data)
 
class ExtraProperty(models.Model):
	class Meta:
		verbose_name = verbose_name_plural = 'ExtraProperty'

	data = models.ForeignKey(Push_data,on_delete=models.CASCADE,verbose_name='绑定数据')
	devId = models.CharField(max_length=50,default='',verbose_name='devId')
	extra_id = models.CharField(max_length=50,default='',verbose_name='extra_id')
	name = models.CharField(max_length=50,default='',verbose_name='name')
	value = models.CharField(max_length=50,default='',verbose_name='value')

	def __str__(self):
		return '绑定数据:' + self.data.devId + 'devId:' + self.devId +'extra_id:' + self.extra_id

class Frame_data(models.Model):
	class Meta:
		verbose_name = verbose_name_plural = 'base64解析数据'

	data = models.ForeignKey(Push_data,on_delete=models.CASCADE,verbose_name='绑定数据')
	decode_list = models.CharField(max_length=500,default='',verbose_name='解码字符串list')
	sta_id = models.CharField(max_length=20,default='',verbose_name='设备标识')
	count = models.IntegerField(default=0,verbose_name='今天第几箱垃圾(暂时默认为0)')
	manyi =  models.IntegerField(default=0,verbose_name='设备满溢参数')
	action = models.IntegerField(default=0,verbose_name='垃圾翻斗动作次数')
	status = models.IntegerField(default=0,verbose_name='是否在线')
	get_time = models.IntegerField(default=0,verbose_name='上次收到数据时间')
	online_time = models.IntegerField(default=0,verbose_name='设备上线时间')

	def __str__(self):
		return '小压站:' + str(self.data.data_id) +'设备标识'+self.sta_id+'解析字符串' + self.decode_list
			

class Station(models.Model):
	class Meta:
		verbose_name = verbose_name_plural = '小压站'

	station_id = models.CharField(max_length=200,default='',verbose_name = '小站标识ID')
	spillover = models.CharField(max_length=200,default='',verbose_name = '满溢度(百分比)')
	add_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
	update_time = models.DateTimeField(auto_now=True,verbose_name='修改时间')

	def __str__(self):
		return '小站ID：' + self.station_id + '      满溢度（百分比）' +  self.spillover

class Sensor(models.Model):
	class Meta:
		verbose_name = verbose_name_plural = '小压站下的传感器数据'

	station = models.ForeignKey(Station,on_delete=models.CASCADE,verbose_name='小压站')
	sensor_type = models.CharField(max_length=20,default='',verbose_name='传感器类型 目前为0~2')
	status = models.CharField(max_length=20,default='',verbose_name='传感器状态:0-正常 1-非正常')
	rawdata = models.CharField(max_length=50,default='',verbose_name='数据采集的原始数据')
	datatime = models.CharField(max_length=100,default='',verbose_name='数据采集时间')
	add_time = models.DateTimeField(auto_now_add=True,verbose_name='入库时间')
	update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')

	def __str__(self):
		return '传感器类型：' + self.sensor_type + '传感器状态：' + self.status + '数据采集时间:' + self.datatime + '入库时间:' + str(self.add_time)
 

			
			


