# Weather station for Raspberry with E-Paper HAT

This is a quick-and-dirty project for displaying temperature sensor data and forecast info on the Waveshare 2.7inch E-Paper HAT.

The refresh scipt runs every 5 minutes and generates three frames which can be displayed with the help of the buttons of the HAT.
For the output see the screenshots dir. Sensor data is pulled from ThingSpeak, forecast from DarkSky.

Please edit the .env for your needs.

The sensor is a Wemos Mini D1 ESP8266-based board operating via 2xAA step-up to 5V. The sensor is a DS18B20. The battery is connected to the A0 ADC pin to measure the voltage and sending some notifications for battery change. You should edit this file for Wifi, ThingSpeak and PIN settings.

The base idea and big part of the refresh script comes from (many thanks for that):
https://diyprojects.io/weather-station-epaper-displaydashboard-jeedom-raspberry-pi-via-json-rpc-api/
