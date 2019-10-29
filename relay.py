import RPi.GPIO as GPIO
import os
import time

class FanController:
    PINS = {
        'low': 17,
        'medium': 15,
        'high': 14
    }
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
    
        GPIO.setup(self.PINS.values(), GPIO.OUT)
        GPIO.output(self.PINS.values(), GPIO.HIGH)
        
    def on(self, speed):
        self.off()
        
        GPIO.output(self.PINS[speed], GPIO.LOW)
        
    def off(self):
        GPIO.output(self.PINS.values(), GPIO.HIGH)
        
class TempController:
    base_dir = '/sys/bus/w1/devices/'
    device_id = '28-00000a9df21a'
    device_file = base_dir + device_id + '/w1_slave'
    
    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        
    def read(self):
        lines = self.read_temp_raw()
    
        while lines[0].strip()[-3:] != 'YES':
            lines = self.read_temp_raw()
            
        equals_pos = lines[1].find('t=')
        
        if equals_pos != -1:
            temp_string = lines[1][(equals_pos + 2):]
            temp_c = float(temp_string) / 1000.0
            
            return temp_c
        
        
    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        
        return lines
 
if __name__ == '__main__':
    fan_controller = FanController()
    temp_controller = TempController()
    
    fan_controller.off()
        
    while True:
        temp = temp_controller.read()
        print(temp)
        
        if temp >= 24:
            fan_controller.on('high')
        elif temp >= 23 and temp < 24:
            fan_controller.on('medium')
        else:
            fan_controller.on('low')
