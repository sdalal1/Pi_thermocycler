import time
import board
import digitalio
import adafruit_max31855
import RPi.GPIO as gpio
import LCD1602
import json
import PCF8591 as ADC
from multiprocessing import Process

ADC.setup(0x48)

DO = 4
CSO = 5
CLK = 6
# thermocouple Pins
CS1 = 18
CS2 = 27
CS3 = 22
#Oven and Fan Pins
heater = 21
cooler = 17
#LCD initialization
LCD1602.init(0x27, 1)

cycles = 0			# counter for cycles run
Thigh = 0			# max target temp
Tlow = 0			# min target temp
threshold = 0		# ramping temp
sampleTime = 1	# seconds
rampTime = 1		# minutes
soakTime = 1		# minutes
loopsRamp = int(rampTime*20/sampleTime)
loopsSoak = int(loopsRamp*soakTime/rampTime)
p = Process(target=Tlow, args=('temp',))

temp=0


gpio.setmode(gpio.BCM)
gpio.setup(heater,gpio.OUT)
gpio.setup(cooler,gpio.OUT)

#Read temperature from T1 and T3, didnt need it for this project but can be initiated for multiple Ovens at the same time
#cs1 = digitalio.DigitalInOut(board.D18)
#T1= adafruit_max31855.MAX31855(spi, cs1)
#TC1 = T1.temperature

#cs3 = digitalio.DigitalInOut(board.D22)
#T3= adafruit_max31855.MAX31855(spi, cs3)
#TC3 = T3.temperature

#Function to control the heating and cooling cycles
def segment(inc):
		global threshold, Thigh, Tlow, TC2, temp
		# positive increments operate heater
		if inc >= 0:
				if threshold > Thigh:
						threshold = Thigh
				if temp < threshold:
						gpio.output(heater,1)
						print("Heater ON")
				elif temp >= threshold:
						gpio.output(heater,0)
						print("Heater OFF")
		# negative increments operate cooler
		elif inc < 0:
				if threshold < Tlow:
						threshold = Tlow
				if temp < threshold:
						gpio.output(cooler,0)
						print("Cooler OFF")
				elif temp >= threshold:
						gpio.output(cooler,1)
						print("Cooler ON")
		# each loop increments		
		threshold += inc
		print("temp " + str(temp))
		print("Threshold"+str(threshold))

try:
		threshold = Tlow #initializing threshold as Tlow which will get significantly higher after the end of first cycle
		while True:
			spi = board.SPI()
			cs2 = digitalio.DigitalInOut(board.D27)
			T2= adafruit_max31855.MAX31855(spi, cs2)
			TC2 = T2.temperature #reading temperature from the Oven
			temp=TC2
			output1 = 'T_oven = ' + str(TC2)
			output2 = 'T_H=' + str(Thigh) + ' T_L=' + str(Tlow)
			LCD1602.write(0, 0, output1) #output to LCD screen
			LCD1602.write(1, 1, output2)
			with open('cycler.txt','r') as f: #open json txt file to initiate T_high and T_low from the browser
					data = json.load(f)
					Thigh = int(data['Thigh'])
					Tlow = int(data['Tlow'])
			Tinc = (Thigh-Tlow)/loopsRamp
			thermistor = ADC.read(4)-273 #reading ADC temperature in celsius for the internal components. If the internal temp is higher than 70, it shuts off the system. 
			if thermistor > 70:
					gpio.output(heater,0)
					gpio.output(cooler,0)
					print('Control Unit temperature too high, heater and cooler shut down')
					break
			for x in range(0,loopsRamp):
					segment(Tinc)
					time.sleep(sampleTime)
					print('heat')
			for x in range(0,loopsSoak):
					segment(0)
					time.sleep(sampleTime)
					print('hot soak')
			gpio.output(heater,0) # force off on exit
			for x in range(0,loopsRamp):
					segment(-Tinc)
					time.sleep(sampleTime)
					print('cool')
			gpio.output(cooler,0) # force off on exit
			for x in range(0,loopsSoak):
					segment(0)
					time.sleep(sampleTime)
					print('cool soak')

except KeyboardInterrupt:
		gpio.cleanup()

