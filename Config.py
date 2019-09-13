from microWebSrv import MicroWebSrv
# import network
import json



def availble_pins():
	all_pins = [2,4,5,12,14,15,16,17,18,19,21,22,23,25,32,33,34,35,36,39] #last 4 are input only
	availble_pins = []
	with open("config_web/Configuration.json","r") as f:
		conf = f.read()
	config = json.loads(conf)
	for i in config["Devices"][0]:
		for j in config["Devices"][0][i]:
			if type(j) == list:
				for k in j:
					all_pins.remove(k)
			if j in all_pins:
				all_pins.remove(j)
	for i in all_pins:
		availble_pins.append(str(i))

	return availble_pins

def Used_Pin():
	Used = []
	with open("config_web/Configuration.json","r") as f:
		conf = f.read()
	config = json.loads(conf)
	for i in config["Devices"][0]:
		Used.append(i+":")
		Used.extend(config["Devices"][0][i])
	return Used

	

print("Configuring.....")
# ----------------------------------------------------------------------------
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/pins', 'GET')
def _httpHandlerPinGET(httpClient, httpResponse) :
	print("WebServer:Pin GET ")
	content1 = str(availble_pins()).replace("'",'"')


	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = content1	 )

	print("Webserver:Availble pins Sent!")




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/wifis', 'POST')
def _httpHandlerWifiPost(httpClient, httpResponse) :
	print("WebServer:wifis POST")

	Data  = httpClient.ReadRequestContent()

	wifi = json.loads(Data)


	with open("config_web/Configuration.json",'r') as f:
		conf = f.read()

	config = json.loads(conf)

	config["Wifis"].append(wifi)
	with open("config_web/Configuration.json", 'w') as f :
		json.dump(config , f)
	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = "Success:New Wifi Added" )
	print("WebServer:Data Writen")




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

@MicroWebSrv.route('/AddDevice', 'POST')
def _httpHandlerDevicePost(httpClient, httpResponse) :
	print("WebServer:Add Device POST")

	Data = httpClient.ReadRequestContent()

	Devices = json.loads(Data.decode("UTF-8"))

	with open("config_web/Configuration.json", 'r') as f:
		conf = f.read()
	config = json.loads(conf)

	try:
		if Devices["Device_type"]== "Ultrason":
			config["Devices"][0][Devices["Device_type"]].append([int(Devices["device_pin"]), int(Devices["device_pin_echo"])])
		elif Devices["Device_type"]== "RGB":
			config["Devices"][0][Devices["Device_type"]].append(Devices["device_pins"])
		else:
			config["Devices"][0][Devices["Device_type"]].append(int(Devices["device_pin"]))
		content = "style='color:#74FF00'>Success:Device Added!"
	except:
		content = "style='color:#FF0000'>Error:Fill the Data"
		
	with open("config_web/Configuration.json","w") as f:
		json.dump(config, f)
	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = content )
	print("Webserver: Data Written")




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/wifis', 'GET')
def _httpHandlerWifisGET(httpClient, httpResponse) :
	print("WebServer:Wifis GET")
	Wifis = []
	with open("config_web/Configuration.json", "r") as f:
		conf = f.read()
	config = json.loads(conf)
	for i in config["Wifis"]:
		Wifis.append(i["SSID"])
	content = str(Wifis).replace("'",'"')
	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = content )
	print("WebServer:Wifis SENT!")




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/Used_Net','POST')
def _httpHandlerUsed_NetPOST(httpClient, httpResponse):
	print("WebServer:Choosing Network...")
	Data = httpClient.ReadRequestContent()

	with open("config_web/Configuration.json","r") as f:
		conf = f.read()
	config = json.loads(conf)

	j = 0
	for i in config["Wifis"]:
		if i["SSID"] == Data.decode("UTF-8"):

			break
		else:
			j += 1

	config["Used_Net"] = config["Wifis"][j]

	with open("config_web/Configuration.json","w") as f:
		json.dump(config, f)
	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = "Success:Network Changed!" )
	print("Network Written!")


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/mqtt','POST')
def _httpHandlerUsed_mqttPost(httpClient, httpResponse):
	print("WebServer:mqtt settings submitted")
	
	Data = httpClient.ReadRequestContent()
	Mqtt = json.loads(Data.decode("UTF-8"))
	with open("config_web/Configuration.json", "r") as f:
		conf = f.read()
	config = json.loads(conf)

	if Mqtt["mqtt_User"] != "":
		config["Mqtt_User"] = Mqtt["mqtt_User"]
	
	if Mqtt["mqtt_Pass"] != "":
		config["Mqtt_Pass"] = Mqtt["mqtt_Pass"]

	if Mqtt["mqtt_server"] != "":
		config["Mqtt_Server"] = Mqtt["mqtt_server"]

	with open("config_web/Configuration.json", 'w') as f:
		json.dump(config, f)

	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = "Success:Mqtt Settings submitted" )
	print("Webserver:Mqtt settings saved")


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/phone','POST')
def _httpHandlerUsed_mqttPost(httpClient, httpResponse):
	print("WebServer:phone number adding...")
	
	Data = httpClient.ReadRequestContent()
	phone = Data.decode("UTF-8")
	with open("config_web/Configuration.json", "r") as f:
		conf = f.read()
	config = json.loads(conf)

	config["Phonenumbers"].append(phone)

	with open("config_web/Configuration.json", 'w') as f:
		json.dump(config, f)

	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = "Success:Phone number Added" )
	print("WebServer:Phone number Added")


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/Del_Wifi', 'POST')
def _httpHandlerDelWifiPOST(httpClient, httpResponse):
	print("WebServer: Deleting Wifi")
	Data = httpClient.ReadRequestContent()
	with open("config_web/Configuration.json", "r") as f:
		conf = f.read()
	config = json.loads(conf)
	j = 0
	for i in config["Wifis"]:
		if i["SSID"] == Data.decode("UTF-8"):

			break
		else:
			j += 1

	del config["Wifis"][j]

	with open("config_web/Configuration.json","w") as f:
		json.dump(config,f)
	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = "Success:Network Deleted!!" )
	print("Webserver: Network Deleted")




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/DelDevice', 'POST')
def _httpHandlerDelWifiPOST(httpClient, httpResponse):
	print("WebServer: Deleting Device")
	Data = httpClient.ReadRequestContent()
	print(Data)
	Devices = json.loads(Data.decode("UTF-8"))

	with open("config_web/Configuration.json", "r") as f:
		conf = f.read()
	print("problem??")
	config = json.loads(conf)
	if Devices["Device_type"]=="Ultrason":
		config["Devices"][0][Devices["Device_type"]].remove([int(Devices["device_pin"]), int(Devices["device_pin_echo"])])
	elif Devices["Device_type"] == "RGB":
		print("Right device")
		config["Devices"][0][Devices["Device_type"]].remove([int(Devices["R"]), int(Devices["G"]),int(Devices["B"])])
	else:
		config["Devices"][0][Devices["Device_type"]].remove(int(Devices["device_pin"]))



	with open("config_web/Configuration.json","w") as f:
		json.dump(config,f)
	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = "Success:Device Deleted!" )
	print("Webserver: Device Deleted")




#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route("/Delpins","GET")
def _httpHandlerUsedPinGET(httpClient, httpResponse):
	print("WebServer: UsedPins GET")
	content = str(Used_Pin()).replace("'",'"')

	httpResponse.WriteResponseOk( headers		 = None,
						  contentType	 = "application/json",
						  contentCharset = "UTF-8",
						  content 		 = content )
	print("WebServer: Used Pins Sent!!")

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route("/phone","GET")
def _httpHandlerUsedPinGET(httpClient, httpResponse):
	print("WebServer: phone number GET")
	
	with open("config_web/Configuration.json", "r") as f:
		conf = f.read()

	config = json.loads(conf)
	content = str(config["Phonenumbers"]).replace("'",'"')

	httpResponse.WriteResponseOk( headers		 = None,
						  contentType	 = "application/json",
						  contentCharset = "UTF-8",
						  content 		 = content )
	print("WebServer: phone number Sent!!")
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/reset', 'POST')
def _httpHandlerRESTPOST(httpClient, httpResponse):
	print("WebServer: reset device!!")
	import machine
	
	httpResponse.WriteResponseOk( headers		 = None,
						  contentType	 = "application/json",
						  contentCharset = "UTF-8",
						  content 		 = "Success!!")
	machine.reset()

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@MicroWebSrv.route('/Del_phone', 'POST')
def _httpHandlerDelPhonePOST(httpClient, httpResponse):
	print("WebServer: Deleting phone number...")
	Data = httpClient.ReadRequestContent()
	with open("config_web/Configuration.json", "r") as f:
		conf = f.read()
	config = json.loads(conf)
	j = 0
	for i in config["Phonenumbers"]:
		if i == Data.decode("UTF-8"):
			break
		else:
			j += 1

	del config["Phonenumbers"][j]

	with open("config_web/Configuration.json","w") as f:
		json.dump(config,f)
	httpResponse.WriteResponseOk( headers		 = None,
							  contentType	 = "application/json",
							  contentCharset = "UTF-8",
							  content 		 = "Success:phone number Deleted!!" )
	print("Webserver: phone number Deleted")


# ----------------------------------------------------------------------------

# print("Config:Starting up the ap")
# ap_if = network.WLAN(network.AP_IF)
# ap_if.active(True)
# ap_if.config(essid = 'ESP32', password = 'microESP32', authmode = 3)
# ap_if.ifconfig(('1.1.1.1', '255.255.255.0', '1.0.0.0', '8.8.8.8'))
# print("Config:AP Started")

print("Config:Starting Web Server")
srv = MicroWebSrv(webPath='config_web/')
srv.MaxWebSocketRecvLen     = 256
srv.WebSocketThreaded		= False
srv.Start()

# ----------------------------------------------------------------------------
