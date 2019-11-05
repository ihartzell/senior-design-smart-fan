import RPi.GPIO as GPIO
import os
import json
import requests
from gpiozero import MotionSensor
from threading import Thread
from datetime import datetime 

class FanController:
    PINS = {
        'low': 17,
        'medium': 15,
        'high': 14
    }
    
    def __init__(self):
        self.is_on = False
        self.last_speed = ''
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
    
        GPIO.setup(self.PINS.values(), GPIO.OUT)
        GPIO.output(self.PINS.values(), GPIO.HIGH)
        
    def on(self, speed='low'):
        self.off()
        self.is_on = True
        self.last_speed = speed
    
        GPIO.output(self.PINS[speed], GPIO.LOW)
        
    def off(self):
        if self.is_on:
            GPIO.output(self.PINS.values(), GPIO.HIGH)
        
class TempController:
    DEVICE_FILE = '/sys/bus/w1/devices/28-00000a9df21a/w1_slave'
    
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
        f = open(self.DEVICE_FILE, 'r')
        lines = f.readlines()
        f.close()
        
        return lines
    
class MotionController:
    PIN = 27
    
    def __init__(self):
        self.sensor = MotionSensor(self.PIN)
        self.last_motion = datetime.now() 
        
        Thread(target=self.record_motion).start()
        
    def record_motion(self):
        while True:
            self.sensor.wait_for_motion()
            self.last_motion = datetime.now() 
    
class ApiController:
    def __init__(self):
        self.url_base = 'http://tp-api.zsluder.com/api'
        self.headers = {
            'Content-Type': 'application/json'
        }
        
    def save_last_temp(self, temp):
        response = requests.post(self.url_base + '/temperature', headers=self.headers)        

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
        
    def get_temp_ranges(self):
        response = requests.get(self.url_base + '/temperature/ranges', headers=self.headers)        

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None
    
def main():
    fan_controller.off()
    fan_controller.on('medium')
    
    last_time = datetime.now()

    while True:
        # Motion detection
        time_elapsed = (datetime.now() - motion_controller.last_motion).seconds
        
        print('No motion in {} sec'.format(time_elapsed))
        
        if int(time_elapsed) >= 15:
            fan_controller.off()
        else:
            fan_controller.on(fan_controller.last_speed)
            
        # Temperature detection
        temp = temp_controller.read()
        time_elapsed = (datetime.now() - last_time).seconds
        
        if int(time_elapsed) >= 5:
           api_controller.save_last_temp(temp)
           last_time = datetime.now()
        
        '''if temp >= 24:
            fan_controller.on('high')
        elif temp >= 23 and temp < 24:
            fan_controller.on('medium')
        else:
            fan_controller.on('low')'''

if __name__ == '__main__':
    fan_controller = FanController()
    temp_controller = TempController()
    api_controller = ApiController()
    motion_controller = MotionController()
    
    try: 
        main()
    except KeyboardInterrupt:
        fan_controller.off()
        
