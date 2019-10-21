#
# Weather station sensor with micropython running on Wemos Mini D1
# - DS18B20 conncted to D1
# - battery voltage connected to A0
# 
# Note: you need to install 'urequests'
# Copyright by Antal Rutz
#
# Documentation and full source code:
# https://github.com/arutz12/Raspberry-Weather-EPD-2in7
# 

import machine
import time
import onewire
import ds18x20
import network
import urequests

# PINS
PIN_D1 = 5 # LED / just for testing
PIN_D2 = 4 # Temp sensor PIN
PIN_A0 = 0 # ADC PIN (battery)

# ThingSpeak fields
FIELD_TEMP = 1  # TS Temperature field
FIELD_VOLT = 2  # TS Volt field

REFERENCE_VOLTAGE = 3.2 # Wemos ref. Voltage
SLEEP_TIME = 5*60*1000  # 5 min

# ThingSpeak
TS_WRITE_API_KEY = '123123123123123123'

# Wifi setup
WIFI_SSID = 'WIFI_SSID'
WIFI_PWD = 'WIFI_PWD'
WIFI_IP = '192.168.1.1'
WIFI_IP_MASK = '255.255.255.0'
WIFI_IP_GW = '192.168.1.254'
WIFI_DNS = '192.168.1.1'

WIFI_SETUP = (
    WIFI_IP,
    WIFI_IP_MASK,
    WIFI_IP_GW,
    WIFI_DNS
)

TS_WRITE_URL = 'https://api.thingspeak.com/update?api_key=' + TS_WRITE_API_KEY + '&field1={}&field2={}'

# configure RTC.ALARM0 to be able to wake the device
#rtc = machine.RTC()
#rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

# set RTC.ALARM0 to fire after X seconds (waking the device)
#rtc.alarm(rtc.ALARM0, SLEEP_TIME)

# check if the device woke from a deep sleep
if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print('woke from a deep sleep')

def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig(WIFI_SETUP)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PWD)
        wifi_error = 0
        while not wlan.isconnected():
            if wifi_error == 10:
                machine.deepsleep(SLEEP_TIME)
            time.sleep(1)
            wifi_error += 1

    print('network config:', wlan.ifconfig())

def get_volt():
    adc = machine.ADC(PIN_A0)   # create an ADC object acting on a pin
    val = adc.read()
    volt = (val * REFERENCE_VOLTAGE) / 1023.0;
    print(volt)
    return round(volt, 2)

def get_temp():
    ow = onewire.OneWire(machine.Pin(PIN_D2))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()
    ds.convert_temp()
    temp = ds.read_temp(roms[0])
    print(temp)
    return round(temp, 1)

def main():
    # Connect to WIFI AP
    wifi_connect()

    temp = get_temp()
    volt = get_volt()
    URL = TS_WRITE_URL.format(temp, volt)
    try:
        urequests.get(URL)
    except Exception as e:
        print(e)
    time.sleep(1)

    machine.deepsleep(SLEEP_TIME)


main()
