from machine import Pin
import ujson
from time import sleep


def config_mod():
	import Config

def wait_for_config():
    button = Pin(27, Pin.IN)
    LED = Pin(2, Pin.OUT) 
    for i in range(4):
        print('interation'+str(i))
        if button.value():
            config_mod()
            break
        LED.value(1)
        sleep(0.5)
        LED.value(0)
        sleep(0.5)

wait_for_config()


import Sweet


