#!/usr/bin/python37all
import cgi
import json
import cgitb
import digitalio
import adafruit_max31855
import board
import RPi.GPIO as gpio
import LCD1602
from urllib.request import urlopen
from urllib.parse import urlencode
cgitb.enable()


data = cgi.FieldStorage()
Tlow = data.getvalue('Tlow')
Thigh = data.getvalue('Thigh')
data = {"Tlow":Tlow, "Thigh":Thigh}

with open('cycler.txt', 'w') as f:
        json.dump(data,f)


spi = board.SPI()
cs2 = digitalio.DigitalInOut(board.D27)
T2= adafruit_max31855.MAX31855(spi, cs2)
TC2 = T2.temperature

api = "5ZWQ99RAB1F0MQN3"
params = {"api_key":api,1: TC2 }
params = urlencode(params)
url = "https://api.thingspeak.com/update?" + params

response = urlopen(url)


print('Content-type:text/html\n\n')
print('<html>')
print('<div style="width:550px;background:#cccccc;border:2px;text-align:center">')
print('<form action="/cgi-bin/cycler.cgi" method="POST">')
print('<label for="Tlow"> Temperature Low &nbsp; Current Low: %s</label><br>' %Tlow)
print('<input type="text" id="Tlow" name="Tlow"><br>')
print('<label for="Thigh"> Temperature High &nbsp; Current High: %s</label><br>'%Thigh)
print('<input type="text" id="Thigh" name="Thigh"><br>')
print('<input type="submit" name="Selection" value="submit" />')

print('</form>')
print('<iframe width="450" height="260" style="border: 1px solid black" src="https://thingspeak.com/channels/1604518/charts/1?bgcolor=%23ffffff&color=%23d62020&dynamic=true&results=60&type=line&yaxis=Temperature+%28C%29&yaxismax=100&yaxismin=0"></iframe>')
print('</html>')