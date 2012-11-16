#! /usr/bin/python
class Accel :
	time_stamp=0
	gnd_truth=-1
	accel_x=0
	accel_y=0
	accel_z=0
	def __init__(self,x,y,z,time_stamp,gnd_truth) :
		self.accel_x=x
		self.accel_y=y
		self.accel_z=z
		self.time_stamp=time_stamp
		self.gnd_truth=gnd_truth
	def __str__(self) :
		return "Accel: "+str(self.time_stamp)+"\t"+str(self.gnd_truth)+"\t"+str(self.accel_x)+"\t"+str(self.accel_y)+"\t"+str(self.accel_z)

class WiFi :
	ap_list=[]
	rssi_list=[]
	time_stamp=0
	gnd_truth=-1 
	def __init__(self,aps,rssis,time_stamp,gnd_truth) :
		self.ap_list=aps
		self.rssi_list=rssis;
		assert(len(self.ap_list) == len(self.rssi_list))
		self.time_stamp=time_stamp
		self.gnd_truth=gnd_truth
	def __str__(self) :
		return "WiFi: "+str(self.time_stamp)+"\t"+str(self.gnd_truth)+"\t"+str(self.ap_list)+"\t"+str(self.rssi_list)

class GPS :
	lat=0
	lon=0
	time_stamp=0
	gnd_truth=-1
	def __init__(self,lat,lon,time_stamp,gnd_truth) :
		self.lat=lat
		self.lon=lon
		self.time_stamp=time_stamp
		self.gnd_truth=gnd_truth
	def __str__(self) :
		return "GPS: "+str(self.time_stamp)+"\t"+str(self.gnd_truth)+"\t"+str(self.lat)+"\t"+str(self.lon)

class GSM :
	cell_tower_list=[]
	rssi_list=[]
	time_stamp=0
	gnd_truth=-1
	def __init__(self,towers,rssis,time_stamp,gnd_truth) :
		self.cell_tower_list=towers
		self.rssi_list=rssis;
		assert(len(self.cell_tower_list) == len(self.rssi_list))
		self.time_stamp=time_stamp
		self.gnd_truth=gnd_truth
	def __str__(self) :
		return "GSM: "+str(self.time_stamp)+"\t"+str(self.gnd_truth)+"\t"+str(self.cell_tower_list)+"\t"+str(self.rssi_list)

class NwkLoc :
	lat=0
	lon=0
	time_stamp=0
	gnd_truth=-1
	def __init__(self,lat,lon,time_stamp,gnd_truth) :
		self.lat=lat
		self.lon=lon
		self.time_stamp=time_stamp
		self.gnd_truth=gnd_truth
	def __str__(self) :
		return "NwkLoc: "+str(self.time_stamp)+"\t"+str(self.gnd_truth)+"\t"+str(self.lat)+"\t"+str(self.lon)
