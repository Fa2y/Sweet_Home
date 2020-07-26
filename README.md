# Sweet_Home
This is a part of multidisciplinary project "Home automation" this is the hardware side I used an esp32 and micropython.
## Features
- Webserver hosted on esp32 (used to configure the hardware).
- Fully costumize you can add as many devices as you want (or as the esp's gpio can handle :p) based on a configuration file.
- Interaction with many devices (MQ2, hcsr04, motion sensor, DHT, Ultrason, Buzzer).
- Sending full report of sensores data to the server using mqtt.
- Receiving commands from the server to interact with devices (RGB light, simple led).
- Alarm on intrusion or fire and sending sms using IFTTT .
