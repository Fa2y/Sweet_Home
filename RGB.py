import machine

PIN_R = 12
PIN_G = 13
PIN_B = 14


class RGBLed:
    def __init__(self, pin_g, pin_r, pin_b):
        self.pin_r = machine.PWM(machine.Pin(pin_r))
        self.pin_g = machine.PWM(machine.Pin(pin_g))
        self.pin_b = machine.PWM(machine.Pin(pin_b))
        self.set(0, 0, 0)
   
    def set_hex(value):
        r,g,b=self.hex_to_rgb(value)
        self.set(r,g,b)
   
    def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    def set(self, r, g, b):
        self.r = int(r)
        self.g = int(g)
        self.b = int(b)
        self.duty()

    def duty(self):
        self.pin_r.duty(self.duty_translate(self.r))
        self.pin_g.duty(self.duty_translate(self.g))
        self.pin_b.duty(self.duty_translate(self.b))

    def duty_translate(self, n):
        """translate values from 0-255 to 0-1023"""
        return int((float(n) / 255) * 1023)


