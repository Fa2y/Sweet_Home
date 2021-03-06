import network
from machine import Pin,PWM
from time import sleep
import json
from umqtt.simple import MQTTClient
import ucollections
import _thread
from RGB import RGBLed

#all public vars
Wifi_SSID = ''
Wifi_Pass = ''
Devices = {}
Devices_Data = {}
Mqtt_User = ''
MQTT_Client = None
MQTT_ClientID = ''
Alarm = False
ArmingMode = False
Motion = [None, None]
Motion_Detectors = None
Phonenumbers = []
msg={}

#this function initialise all public vars from the configuration file
def init_all():
        #declare so u can modify the glob vars
        global Wifi_SSID, Wifi_Pass, Devices, Devices_Data, Mqtt_User, Mqtt_Pass, MQTT_Client, Motion_Detectors,Motion
        #get config file
        with open("config_web/Configuration.json",'r') as f:
                conf = f.read()
        config = json.loads(conf)
        #Networks
        Wifi_SSID = config["Used_Net"]['SSID']
        Wifi_Pass = config["Used_Net"]["Password"]
        #Devices
        Devices = dict(config["Devices"][0])
        #Devices_Data is init here so it ease the job of writing data same structure on the config file
        Devices_Data = dict(config["Devices"][0])
        #in Grab_DATA_Devices_Send we don't need these three Devices
        Devices_Data.pop("Light")
        Devices_Data.pop("RGB")
        Devices_Data.pop("MSense")
        #Declaring interupts for the motion detecters
        for i in Devices["MSense"]:
                pir = Pin(i, Pin.IN)
                pir.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)
                Motion_Detectors.append(pir)
        #init motion alarm
        Motion[0] = False
        Motion[1] = "INIT"
        #Declaring as list
        Devices_Data["DHT"]=[]
        Devices_Data["GSense"]=[]

        #Mqtt: Get username because we gonna need it after for publishing topics
        Mqtt_User = config["Mqtt_User"]
        #Mqtt: client with :clientid , Server ip/domain, username ,password
        MQTT_ClientID = config["ClientID"]
        print(config["Mqtt_Server"]+"----"+config["ClientID"])
        MQTT_Client = MQTTClient(config["ClientID"], config["Mqtt_Server"], user = config["Mqtt_User"], password = config["Mqtt_Pass"])
        #init phonenumbers for send alarm msg
        Phonenumbers = config["Phonenumbers"]

#subscribe callback function
def sub_cb(topic, msg):
        global Alarm, ArmingMode, MQTT_Client, Mqtt_User
        print("Data published!!")
        print(topic, msg)
        if topic == bytes(Mqtt_User+'/Alarm','UTF-8') and msg == b'OFF':
                Alarm = False
        if topic == bytes(Mqtt_User+'/ArmingMode','UTF-8'):
                if msg == b'ON' and ArmingMode == False:
                        ArmingMode = True
                        print("Arms")
                        _thread.start_new_thread(Arming_Mode, [])
                if msg == b'OFF':
                        ArmingMode = False
        if topic == bytes(Mqtt_User+'/Light','UTF-8'):
                if msg.decode("utf-8").split('-')[-1] == 'ON':
                        light = Pin(int(msg.decode("utf-8").split('-')[1]) , Pin.OUT)
                        light.value(1)
                elif msg.decode("utf-8").split('-')[-1] == "OFF":
                        light = Pin(int(msg.decode("utf-8").split('-')[1]) , Pin.OUT)
                        light.value(0)
        if topic == bytes(Mqtt_User+'/RGB','UTF-8'):
                if msg.decode("UTF-8").split('-')[-1] == 'ON':
                        rgb = RGBLed()
                

#in case of errors
def restart_and_reconnect():
        import machine
        print('Failed to connect to MQTT broker. Reconnecting...')
        sleep(10)
        machine.reset()


#connect and set the callback function
def connect():
        global MQTT_Client, Mqtt_User
        MQTT_Client.set_callback(sub_cb)
        try:
                MQTT_Client.connect()
                #Mqtt: Subscribing to all needed topics
                MQTT_Client.subscribe(Mqtt_User+"/ArmingMode")
                MQTT_Client.subscribe(Mqtt_User+"/Alarm")
        except OSError as e:
                print(e)
                restart_and_reconnect()
#update all data on startup od the esp it send the list of devices to structure it in the db
def Update_Device():
        global MQTT_Client, Mqtt_User, Devices
        Devices_to_send = Devices
        Devices_to_send.pop("ServoM")
        Devices_to_send.pop("Buzzer")
        try:
                MQTT_Client.publish(bytes(Mqtt_User+"/UpdateDevices","UTF-8"),bytes("{'data':"+str(Devices_to_send)+",'clientid':"+MQTT_ClientID+"}","UTF-8"))
                sleep(1)
        except OSError as e:
                restart_and_reconnect()

#this function measure the data for all devices (DHT, Gas sensor,Doors state) and then publishing them to the broker
def Grab_DATA_Devices_Send():
        from dht import DHT11
        from hcsr04 import HCSR04
        import MQ2
        global Devices_Data, Mqtt_User, MQTT_Client
        while True:
                sleep(5)

                #dht:[pin,[],[]]
                for i in Devices["DHT"]:
                        DHT = DHT11(Pin(i, Pin.IN, Pin.PULL_UP))
                        DHT.measure()
                        Devices_Data["DHT"].append([i,DHT.temperature, DHT.humidity])




                # for i in Devices["GSense"]:
                #         GS = MQ2(pinData = i, baseVoltage = 5)
                #         GS.calibrate()
                #         Devices_Data["GSense"].append([i,GS.readSmoke(), GS.readLPG(), GS.readMethane(), readHydrogen()])
                #         #checking smoke (recheck the values online!!!)
                #         if Devices_Data["GSense"][j][0]>500 or Devices_Data["GSense"][j][1]>500:
                #                 Alarm = True
                #                 Fire_Gas_Alarm()




                j = 0
                for i in Devices["Ultrason"]:
                        US = HCSR04(trigger_pin=i[0], echo_pin=i[1])
                        if US.distance_cm()>3.0:
                                #Door id and the second value is bool either open or not
                                Devices_Data["Ultrason"][j] = [i[0],{"value":True}]
                        else:
                                Devices_Data["Ultrason"][j] = [i[0],{"value":False}]
                        j += 1


                try:
                        MQTT_Client.publish(bytes(Mqtt_User+"/Values","UTF-8"),bytes("{'data':"+str(Devices_Data)+",'clientid':"+MQTT_ClientID+"}","UTF-8"))
                except OSError as e:
                        restart_and_reconnect()

#func try to connect to the wifi specified in config file and return true if successfull and false in other cases
def Connect_Wifi():
        global Wifi_SSID, Wifi_Pass
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


#raise a special alarm for gas and fire (it shut down the gas outlets with a servo)
def Fire_Gas_Alarm():
        global Devcies
        msg["data"] = "gaz"
        for i in Devices["ServoM"]:
                s = Pin(i)
                servo = PWM(s, freq=50)
                servo.duty(85)
        Alarm(msg)

#ALARM!!! the msg is sent by mqtt to notify and sms(sms is not implemented yet)
def Alarm(msg):
        from sms import Sms
        sms = Sms()
        global Alarm, MQTT_Client, MQTT_ClientID
        msg["alarm"] = True
        #publish msg
        MQTT_Client.publish(bytes(Mqtt_User+"/Alarm","UTF-8"),bytes("{'data':'"+msg+",'clientid':"+MQTT_ClientID+"}","UTF-8"))
        for i in Phonenumbers:
                sms.send_msg(i,"SweetHome ALARM!!: \n alarm of type"+msg["data"])       
        button = Pin(26, Pin.IN)
        while Alarm and not(button.value()):
                sleep(1)
                beeper = PWM(Pin(14, Pin.OUT), freq=440, duty=512)
                time.sleep(0.3)
                beeper.deinit()
                time.sleep(0.3)



#handler function for the interrupt
def handle_interrupt(pir):
        global Motion
        Motion[0] = True
        Motion[1] = "MSense-"+int(str(pir)[4:-1])


def Arming_Mode():
        global Devices_Data, ArmingMode, Motion, MQTT_Client
        print("ArmingMode Activated!!")
        while ArmingMode:
                sleep(1)
                for i in Devices_Data["Ultrason"]:     
                        if i[1] :
                                Alarm("Alert!!: "+str(i[0])+"is open.")
                if Motion[0] :
                        Alarm("Alert!!: Motion detected in "+Motion[1]+".")
def While_checking():
        global MQTT_Client
        print("Checking for msg...",end="")
        while True:             
                sleep(1)
                MQTT_Client.check_msg()




init_all()

Connect_Wifi()

connect()

Update_Device()

print("Starting thread!")

_thread.start_new_thread(While_checking, [])

Grab_DATA_Devices_Send()

# if __name__ == '__main__':
#       main()