# Weather station for Raspberry with E-Paper HAT

![RPI_Weather_EPD](./screenshots/raspi-weather-small1.jpg)

This is a combined RaspberryPi and ESP8266 project for measuring temperature and displaying sensor data and forecast info on the Waveshare 2.7inch E-Paper HAT.

The microcontroller uploads outside temperature to an IoT data collector then the Raspberry Pi collects it along weather forecast and shows them on a nice E-Paper display. All you need to do is to buy the stuff and follow the installation steps. Some bit of extra reading is needed if your are not familiar with ESP8266 development boards and micropython however the Raspberry setup is far easier and you can get the current data from the weather provider as well and leave the ESP stuff. The sensor just adds accuracy and a nice learning experience regarding microcontrollers.

It is mainly a fun project which you can extend freely. I hope you'll enjoy building it as well.

### The stuff you need:
+ [ESP8266](https://en.wikipedia.org/wiki/ESP8266) development board (I prefer the [Wemos Mini D1](https://wiki.wemos.cc/products:d1:d1_mini))
+ [DS18B20](https://components101.com/sensors/ds18b20-temperature-sensor) temperature sensor
+ [Raspberry Pi 2B/3B/Zero/Zero W](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
+ [Waveshare 2.7" E-Ink display HAT for Raspberry Pi 2B/3B/Zero/Zero W](https://www.aliexpress.com/item/32830012306.html) 

## The PI and the E-Ink display

For keeping things simple I created two scripts which run simultaneously. The one fetches sensor data and forecast the other handles button events.
The refresh scipt runs every 5 minutes and generates three frames which can be displayed with the help of the buttons of the HAT.
For the output see the screenshots dir. Sensor data is pulled from ThingSpeak, forecast from DarkSky.

This E-Paper HAT has four buttons which are used in this project according to the followings:
1. Frame1: sensor data and todays min-max temperature, wind and precipitation forecast along with short weather condition text
2. Frame2: sensor data, humidity, air pressure, wind, sunrise/sunset
3. Frame3: 4-day weather forecast
4. clear display

The status line contains the last display refresh time and the battery voltage.
The screenshots were taken the RPi set to Hungarian language - you can alter it very easily, you'll see below.

I borrowed the skeleton of the refresh script from [here](https://diyprojects.io/weather-station-epaper-displaydashboard-jeedom-raspberry-pi-via-json-rpc-api/)

## Installation steps

### 1. Create accounts
+ [ThingSpeak](https://thingspeak.com/) account
+ [DarkSky](https://darksky.net) account

Both DarkSky and ThingSpeak are free for limited personal usage.

### 2. Clone the git repo into _pi_ user home

``` c++
cd ~
git clone https://github.com/arutz12/Raspberry-Weather-EPD-2in7
```

### 3. Optional (but recommended): create a virtual python environment

### 4. Install all the modules in _requirements.txt_
``` shell
pip install -r requirements.txt
```

### 5. Edit paths and install systemd services:

``` shell
sudo cp weather.service epd-button.service /lib/systemd/system
cd /etc/systemd/system/multi-user.target.wants
sudo ln -s /lib/systemd/system/weather.service
sudo ln -s /lib/systemd/system/epd-button.service
```

### 6. Rename the _.env.sample_ to _.env_ and set all the variables 

_LOCALE_ determines the name of the days in the 4-days forecast frame and the _DARKSKY_LANGUAGE_ is responsible for DarkSky weather condition texts.

``` c++
LOCALE = 'en_US.UTF-8'  # change to your language locale
FORECAST_TITLE = '4-days forecast'  # or change to your language

# DarkSky
DARKSKY_API_KEY = ''
DARKSKY_LONGITUDE = 19.223344  # your coordinates
DARKSKY_LATITUDE = 44.556677   # your coordinates
DARKSKY_LANGUAGE = ''  # e.g. 'ENGLISH'
DARKSKY_UNITS = 'SU'  # ('AUTO', 'CA', 'UK2', 'US', 'SU') SU==metric

# ThingSpeak
TS_READ_API_KEY = ''
TS_CHANNEL_ID = ''

# Running environment
RUN_ENV = ''  # 'production' or 'test'
```

#### Note:
The micropython script needs your ThingSpeak _WRITE API KEY_ and the _.env_ your _READ API KEY_.

## Testing:
You can test the whole thing on your own machine (virtual environment recommended) by setting the RUN_MODE to _test_ in _.env_. Then run
``` shell
python weather-refresh-2in7.py
```

and look for _frame[123].bmp_.

## The sensor
The sensor station is a Wemos Mini D1 ESP8266-based board operating via 2xAA step-up to 5V. The temperature sensor is a DS18B20 which is connected to the D1 pin and the battery voltage is measured on the A0 ADC. The sensor weaks up from deepsleep every every five minutes and sends the data to a [ThingSpeak](https://thingspeak.com/) channel. Depending on your powering setup it can last from weeks to months. The Wemos board runs [micropython](http://micropython.org/) which is far easier to use (for me) than Arduino's C++. The script is fairly simple and can be easily customized for more complex DHT sensors - micropython has everything you need for that, just head over to the documentation.

#### Note
you will need the _urequests_ micropython module which you can obtain from [here](https://github.com/pfalcon/pycopy-lib/blob/master/urequests/urequests) or [here](https://github.com/micropython/micropython-lib/blob/master/urequests). Either build the firmware with it or just copy the file to the root dir.

I put everything (sensor, devboard, batteries) into a waterresistant box and found some place outside, didn't bothered with the aesthetics. (If you're interested I can thoroughly detail the sensor cabling however you can find tons of info on the net, you need a breadboard a bunch of jumper cables and you're done.)

### Sensor setup

You should edit the global variables of the micrpython script which relate to Wifi (I configured it with static IP for quicker connection setup), ThingSpeak and sensor PIN.
Copy the script to the root of the board as _main.py_. (I use [RSHELL](https://github.com/dhylands/rshell) for that.)
You should setup a ThingSpeak account, create a channel and put the _WRITE API KEY_ into the script file.

#### Edit global variables

``` shell
# PINS
PIN_D2 = 4 # Temp sensor PIN
PIN_A0 = 0 # ADC PIN (battery)

# ThingSpeak fields
FIELD_TEMP = 1  # TS Temperature field
FIELD_VOLT = 2  # TS Volt field

# ThingSpeak
TS_WRITE_API_KEY = ''

# Wifi setup
WIFI_SSID = 'WIFI_SSID'
WIFI_PWD = 'WIFI_PWD'
WIFI_IP = '192.168.1.1'
WIFI_IP_MASK = '255.255.255.0'
WIFI_IP_GW = '192.168.1.254'
WIFI_DNS = '192.168.1.1'

```

## Misc:
If you don't want to 3D-print a case the [Pimoroni Pibow Coupé](https://shop.pimoroni.com/products/pibow-coupe-for-raspberry-pi-3-b-plus) can be a good choice for RPI 2/3B/3B+.

Feel free to contact me if you're stuck anywhere while building this project.

![RPI_Weather_EPD3](./screenshots/raspi-weather-small3.jpg)
