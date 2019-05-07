import network
from machine import Pin,PWM
from time import sleep
import json
from umqtt.simpel import MQTTClient
import ucollections
import uasyncio as asyncio


#all public vars
Wifi_SSID = ''
Wifi_Pass = ''
Devices = {}
Devices_Data = {}
Mqtt_User = ''
MQTT_Client = None
Alarm = False
ArmingMode = False
Motion = []
Motion_Detectors = None

#this function initialise all public vars from the configuration file
def init_all():
	#declare so u can modify the glob vars
	global Wifi_SSID, Wifi_Pass, Devices, Devices_Data, Mqtt_User, Mqtt_Pass, MQTT_Client, Motion_Detectors,Motion
	#get config file
	with open("config_web/Configuration.json",'r') as f:
		conf = f.read
	config = json.loads(conf)
	#Networks
	Wifi_SSID = config["Used_Net"]['SSID']
	Wifi_Pass = config["used_Net"]["Password"]
	#Devices
	Devices = config["Devices"]
	#Devices_Data is init here so it ease the job of writing data same structure on the config file
	Devices_Data = config["Devices"]
	#in Grab_DATA_Devices we don't need these three Devices
	Devices_Data.pop("Light")
	Devices_Data.pop("RGB")
	Devices_Data.pop("MSense")
	#Declaring interupts for the motion detecters
	for i in Devices["MSense"]:
		pir = Pin(i, Pin.IN)
		pir.irq(trigger:Pin.IRQ_RISING, handler=handle_interrupt)
		Motion_Detectors.append(pir)
	#init motion alarm
	Motion[0] = False
	Motion[1] = "INIT"
	#Declaring as a deque (FIFO) with max lenght of 1000 with interval of 30 sec so about 8 hours of data
	for i in Devices_Data["DHT"]:
		i = ucollections.deque([], 1000)
	for i in Devices_Data["GSenese"]:
		i = ucollections.deque([], 1000)
	#Mqtt: Get username because we gonna need it after for publishing topics
	Mqtt_User = config["Mqtt_User"]
	#Mqtt: client with :clientid , Server ip/domain, username ,password
	MQTT_Client = MQTTClient(config["API_KEY"], config["Mqtt_Server"], user = config["Mqtt_User"], password = config["Mqtt_Pass"])


#subscribe callback function
def sub_cb(topic, msg):
	print(topic, msg)
	if topic == b'Alarm' and msg == b'OFF':
		Alarm = False
	if topic == b'ArmingMode':
		if msg == b'ON':
			ArmingMode = True
			Arming_Mode()
		if msg == b'OFF':
			ArmingMode = False

#in case of errors 
def restart_and_reconnect():
	import machine
	print('Failed to connect to MQTT broker. Reconnecting...')
	time.sleep(10)
	machine.reset()


#connect and set the callback function
def connect():
	global MQTT_Client, Mqtt_User
	MQTT_Client.set_callback(sub_cb)
	try:
		MQTT_Client.connect()
		#Mqtt: Subscribing to all needed topics
		MQTT_Client.subscribe("/"+Mqtt_User+"/ArmingMode")
		MQTT_Client.subscribe("/"+Mqtt_User+"/Alarm")
	except OSError as e:
		restart_and_reconnect()
#update all data on startup od the esp it send the list of devices to structure it in the db
def Update_Device():
	global MQTT_Client, Mqtt_User, Devices
	Devices_to_send = Devices
	Devices_to_send.pop("ServoM")
	Devices_to_send.pop("Buzzer")
	try:
		MQTT_Client.publish(bytes("/"+Mqtt_User+"/UpdateDevices","UTF-8"),bytes(str(Devices_to_send),"UTF-8"))
		sleep(1)
	except OSError as e:
		restart_and_reconnect()

#this function measure the data for all devices (DHT, Gas sensor,Doors state) and then publishing them to the broker
async def Grab_DATA_Devices_Send():
	from dht import DHT11
	from hcsr04 import HCSR04
	from mq2 import mq2
	global Devices_Data, Mqtt_User, MQTT_Client
	while True:
		await asyncio.sleep(180)
		

		j = 0
		for i in Devices["DHT"]:
			DHT = DHT11(Pin(i, Pin.IN, Pin.PULL_UP))
			DHT.measure()
			Devices_Data["DHT"][j].append([DHT.temperature, DHT.humidity])
			j += 1



		j = 0
		for i in Devices["GSense"]:
			GS = MQ2(pinData = i, baseVoltage = 5)
			GS.calibrate()
			Devices_Data["GSense"][j].append([GS.readSmoke(), GS.readLPG(), GS.readMethane(), readHydrogen()])
			j += 1



		j = 0
		for i in Devices["Ultrason"]:
			US = HCSR04(trigger_pin=Devices["Ultrason"][0], echo_pin=Devices["Ultrason"][1])
			if US.distance_cm()>3.0:
				#Door id and the second value is bool either open or not
				Devices_Data["Ultrason"][j] = ["Door"+str(Devices["Ultrason"][0])+","+str(Devices["Ultrason"][1]),True]
			else:
				Devices_Data["Ultrason"][j] = ["Door"+str(Devices["Ultrason"][0])+","+str(Devices["Ultrason"][1]),True]
			j += 1


		try:
			MQTT_Client.publish(bytes("/"+Mqtt_User+"/Values","UTF-8"),bytes(str(Devices_Data),"UTF-8"))
		except OSError as e:
			restart_and_reconnect()

#func try to connect to the wifi specified in config file and return true if successfull and false in other cases
def Connect_Wifi():
	sta_if = network.WLAN(network.STA_IF)
	sta_if.active(True)
	try:
		sta_if.connect(Wifi_SSID, Wifi_Pass)
		print("Connecting...",end="")
		while not sta_if.isconnected():
			print(".",end="")
			sleep(0.5)
		return True
	except:
		return False


#This func checks the values of smoke and lpg to discover any gas leak and give an alert and it disables gas 
async def Fire_GasLeak_Detect():
	while True:
		await asyncio.sleep(1)
		for i in Devices_Data["GSense"]:
			#checking smoke (recheck the values online!!!)
			if i[0]>1000 or i[1]>1000:
				Alarm = True
				Fire_Gas_Alarm()


#raise a special alarm for gas and fire (it shut down the gas outlets with a servo)
def Fire_Gas_Alarm():
	global Devcies
	msg = "Alert:Fire or Gas leak!!"
	for i in Devices["ServoM"]:
		s = Pin(i)
		servo = PWM(s, freq=50)
		servo.duty(85)
	Alarm(msg)

#ALARM!!! the msg is sent by mqtt to notify and sms(sms is not implemented yet)
def Alarm(msg):
	global Alarm, MQTT_Client
	#publish msg
	MQTT_Client.publish(bytes("/"+Mqtt_User"/Alarm","UTF-8"),bytes(msg,"UTF-8"))
	#send msg
	while Alarm:
		#buzzer 


#handler function for the interrupt
def handle_interrupt(pir):
	global Motion
	Motion[0] = True
	Motion[1] = "MSense-"+int(str(pir)[4:-1])


def Arming_Mode():
	global Devices_Data, ArmingMode, Motion
	while ArmingMode:
		for i in Devices_Data["Ultrason"]:
			if i[1] :
				Alarm("Alert!!: "+i[0]+"is open.")
		if Motion[0] : 
			Alarm("Alert!!: Motion detected in "+Motion[1]+".")


def main():
	init_all()

	Connect_Wifi()

	connect()

	Update_Device()

	loop = asyncio.get_event_loop()

	loop.run_until_complete(asyncio.gather(Fire_GasLeak_Detect(), Grab_DATA_Devices_Send()))
 

if __name__ == '__main__':
	main()