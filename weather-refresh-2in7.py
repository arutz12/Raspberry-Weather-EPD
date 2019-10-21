# coding: utf-8
# 
# Weather station display for Raspberry and Waveshare 2.7" e-Paper display
# (generating frames)
# 
# Copyright by Antal Rutz
#
# Documentation and full source code:
# https://github.com/arutz74/raspberry-weather-epd-2in7
# 
# Base code and ideas from:
# English version https://diyprojects.io/weather-station-epaper-displaydashboard-jeedom-raspberry-pi-via-json-rpc-api/
#

import sys
import os
import time
import locale
from dotenv import load_dotenv
from textwrap import wrap
from datetime import datetime
from datetime import timedelta
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

LOCALE = os.environ.get('LOCALE')
locale.setlocale(locale.LC_TIME, LOCALE)

FORECAST_TITLE = os.environ.get('FORECAST_TITLE')
RUN_ENV = os.environ.get('RUN_ENV')

# globals
folder_img = os.path.join(base_dir, 'icons')
cond_height = 100
cond_width = 100
big_height = 18
icon_height = 25
icon_width = 25
border = 5
column1 = 70
column1_5 = 115
column2_5 = 200
column2 = 132
column3 = 198
bottom = 140
DEBUG = True
SLEEPTIME = 300

test_mode = False
if RUN_ENV == 'test':
    test_mode = True

if DEBUG:
    from pprint import pprint

if test_mode:
    EPD_WIDTH = 176
    EPD_HEIGHT = 264
else:
    sys.path.insert(0, base_dir)

    import waveshare_epd.epd2in7

    epd = waveshare_epd.epd2in7.EPD()
    epd.init()
    EPD_WIDTH = waveshare_epd.epd2in7.EPD_WIDTH
    EPD_HEIGHT = waveshare_epd.epd2in7.EPD_HEIGHT

# Charge les fonts et les images - Load Images and fonts
fontExtraSmall = ImageFont.truetype(os.path.join(folder_img, 'FreeMonoBold.ttf'), 10)
fontSmall = ImageFont.truetype(os.path.join(folder_img, 'FreeMonoBold.ttf'), 12)
fontMedium = ImageFont.truetype(os.path.join(folder_img, 'FreeMonoBold.ttf'), 14)
fontBig = ImageFont.truetype(os.path.join(folder_img, 'FreeMonoBold.ttf'), big_height)
fontExtraBig = ImageFont.truetype(os.path.join(folder_img, 'FreeMonoBold.ttf'), 32)

temperature = Image.open(os.path.join(folder_img, 'temperature.png'))
humidity = Image.open(os.path.join(folder_img, 'humidity.png'))
pressure = Image.open(os.path.join(folder_img, 'pressure.png'))
direction = Image.open(os.path.join(folder_img, 'direction.png'))
sunrise = Image.open(os.path.join(folder_img, 'sunrise.png'))
sunset = Image.open(os.path.join(folder_img, 'sunset.png'))
precip = Image.open(os.path.join(folder_img, 'Rain.png'))

# Resize pictures
temperature = temperature.resize((icon_height, icon_width))
humidity = humidity.resize((icon_height, icon_width))
pressure = pressure.resize((icon_height, icon_width))
direction = direction.resize((icon_height, icon_width))
sunrise = sunrise.resize((icon_height, icon_width))
sunset = sunset.resize((icon_height, icon_width))
precip = precip.resize((icon_height+10, icon_width+10))


# w,h = condition.size

def debug(val):
    if DEBUG:
        pprint(val)


def findIcon(cond):
    """
    clear-day, clear-night, rain, snow, sleet, wind, fog, cloudy, partly-cloudy-day, partly-cloudy-night
    """
    # icons Open Source https://github.com/kickstandapps/WeatherIcons

    icon_def = {
        'clear-day':            'Sun',
        'clear-night':          'Moon',
        'rain':                 'Rain',
        'snow':                 'Snow',
        'sleet':                'Hail',
        'wind':                 'wind',
        'fog':                  'Haze',
        'cloudy':               'Cloud',
        'partly-cloudy-day':    'PartlySunny',
        'partly-cloudy-night':  'PartlyMoon'
    }

    if cond in icon_def:
        return icon_def[cond]
    else:
        print('No icon for ', cond)
        return 'Tornado'


def getWeatherData():

    from DSweather import fetchDarkSkyWeather
    from TSfetch import fetchThingSpeak

    current, daily = fetchDarkSkyWeather()
    ts_data = fetchThingSpeak()
    debug(ts_data)

    weather = {
        'conditiontxt': current['summary'],
        'condition': findIcon(current['icon']),
        'sunRise': daily[0]['sunrise_time'],
        'sunSet': daily[0]['sunset_time'],
        'pressure': current['pressure'],
        'humidity': current['humidity'],
        'precip': current['precip_probability'],
        'currTemp': str(ts_data['TEMP']),
        'tempMin': str(daily[0]['temperature_min']),
        'tempMax': str(daily[0]['temperature_max']),
        'windSpeed': current['wind_speed'],
        'windDir': str(current['wind_bearing']),
        'windDirTxt': str(current['wind_direction']),
        "conditionDay1": findIcon(daily[0]['icon']),
        "conditionDay2": findIcon(daily[1]['icon']),
        "conditionDay3": findIcon(daily[2]['icon']),
        "conditionDay4": findIcon(daily[3]['icon']),
        "condDay1Txt": daily[0]['summary'],
        "condDay2Txt": daily[1]['summary'],
        "condDay3Txt": daily[2]['summary'],
        "condDay4Txt": daily[3]['summary'],
        "tempMinDay1": str(daily[0]['temperature_min']),
        "tempMinDay2": str(daily[1]['temperature_min']),
        "tempMinDay3": str(daily[2]['temperature_min']),
        "tempMinDay4": str(daily[3]['temperature_min']),
        "tempMaxDay1": str(daily[0]['temperature_max']),
        "tempMaxDay2": str(daily[1]['temperature_max']),
        "tempMaxDay3": str(daily[2]['temperature_max']),
        "tempMaxDay4": str(daily[3]['temperature_max'])
    }

    weather['city'] = 'Budapest'
    weather['battery'] = str(ts_data['VOLT'])

    debug('TIME: ' + str(datetime.now()))
    debug(weather)
    debug(current)
    # debug(daily)
    return weather


def clearDisplay():
    epd.Clear(0xFF)


def displayFrame(mask):
    # clearDisplay()
    epd.display(epd.getbuffer(mask))


def updateFrame1(weather):

    icon_width = 30
    row_height = 16

    mask = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)

    draw = ImageDraw.Draw(mask)

    condition = Image.open(os.path.join(folder_img,  weather['condition'] + '.png'))
    condition = condition.resize((cond_height, cond_width))
    # draw.rectangle((0, 0, cond_width, cond_height), fill=0)

    mask.paste(condition, (0, 0), condition)
    # draw.rectangle((cond_width, 0, EPD_HEIGHT, 50), fill=0)
    # draw.text((cond_width + border * 2, 0), str(weather['currTemp']) + '°C', font=fontExtraBig, fill=1)
    draw.text((cond_width + border * 2, 0), str(weather['currTemp']) + '°C', font=fontExtraBig, fill=0)

    condRows = wrap(weather['conditiontxt'], width=14)[:2]
    draw.text((cond_width + border*2, 47), condRows[0], font=fontBig, fill=0)
    if len(condRows) == 2:
        draw.text((cond_width + border*2, 72), condRows[1], font=fontBig, fill=0)

    mask.paste(temperature, (border*3, 115), temperature)
    draw.text((border + icon_width + border * 2, 7 * row_height - 4), str(weather['tempMinDay1']) + '°C', font=fontMedium, fill=0)
    draw.text((border + icon_width + border * 2, 8 * row_height - 4), str(weather['tempMaxDay1']) + '°C', font=fontMedium, fill=0)

    mask.paste(precip, (column1_5, 115), precip)
    draw.text((column1_5+35, 117), str(weather['precip']) + '%', font=fontMedium, fill=0)

    wind_dir = direction.rotate(float(weather['windDir']))
    mask.paste(wind_dir, (column2_5, 115), wind_dir)
    draw.text((column2_5 + 35, 117), weather['windDirTxt'], font=fontMedium, fill=0)
    draw.text((column2_5, bottom), str(int(weather['windSpeed'])) + 'km/h', font=fontMedium, fill=0)

    draw.line((cond_width, 50, EPD_HEIGHT, 50), fill=0)
    draw.line((0, cond_height, EPD_HEIGHT, cond_height), fill=0)
    draw.line((0, bottom + 20, EPD_HEIGHT, bottom + 20), fill=0)
    draw.line((cond_width, 0, cond_width, cond_height), fill=0)

    refresh_time = time.strftime("%H:%M")
    refresh_date = time.strftime("%Y-%m-%d")
    # refresh_date = time.strftime("%Y. %B %-d. %A")
    draw.text((border, EPD_WIDTH - 18), refresh_date + ' ' + refresh_time, font=fontSmall, fill=0)
    draw.text((column3 - border*2, EPD_WIDTH - 18), 'BAT: ' + weather['battery'] + 'V', font=fontSmall, fill=0)

    debug('Update frame1')
    mask.save(os.path.join(base_dir, 'frame1.bmp'), "bmp")
    if not test_mode:
        displayFrame(mask)


def updateFrame2(weather):
    mask = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)

    bottom = 138
    draw = ImageDraw.Draw(mask)

    condition = Image.open(os.path.join(folder_img, weather['condition'] + '.png'))
    condition = condition.resize((cond_height, cond_width))
    mask.paste(condition, (0, 0), condition)
    date = time.strftime("%Y-%m-%d") + "  " + time.strftime("%H:%M")
    draw.text((cond_width + border*2, 2), date, font=fontMedium, fill=0)

    condRows = wrap(weather['conditiontxt'], width=14)[:2]
    draw.text((cond_width + border*2, 20), condRows[0], font=fontBig, fill=0)
    if len(condRows) == 2:
        draw.text((cond_width + border*2, 40), condRows[1], font=fontBig, fill=0)

    mask.paste(sunrise, (cond_width + border, 70), sunrise)
    mask.paste(sunset, (cond_width + 90, 70), sunset)
    draw.text((cond_width + 40, 80), weather['sunRise'], font=fontSmall, fill=0)
    draw.text((cond_width + 120, 80), weather['sunSet'], font=fontSmall, fill=0)

    wind_dir = direction.rotate(float(weather['windDir']))
    mask.paste(temperature, (border, 110), temperature)
    mask.paste(humidity, (column1, 110), humidity)
    mask.paste(pressure, (column2, 110), pressure)
    mask.paste(wind_dir, (column3, 110), wind_dir)
    draw.text((border, bottom), str(weather['currTemp']) + '°C', font=fontMedium, fill=0)
    draw.text((column1, bottom), str(weather['humidity']) + '%', font=fontMedium, fill=0)
    draw.text((column2, bottom), str(weather['pressure']) + 'kPa', font=fontMedium, fill=0)
    draw.text((column3 + 35, 110), weather['windDirTxt'], font=fontMedium, fill=0)
    draw.text((column3, bottom), str(int(weather['windSpeed'])) + 'km/h', font=fontMedium, fill=0)

    # Lines
    draw.line((0, cond_height, EPD_HEIGHT, cond_height), fill=0)
    draw.line((0, 140 + 20, EPD_HEIGHT, 140 + 20), fill=0)
    draw.line((cond_width, 0, cond_width, cond_height), fill=0)

    refresh_time = time.strftime("%H:%M")
    refresh_date = time.strftime("%Y-%m-%d")
    # refresh_date = time.strftime("%Y. %B %-d. %A")
    draw.text((border, EPD_WIDTH - 18), refresh_date + ' ' + refresh_time, font=fontSmall, fill=0)
    draw.text((column3 - border*2, EPD_WIDTH - 18), 'BAT: ' + weather['battery'] + 'V', font=fontSmall, fill=0)

    # mask = mask.rotate(90)

    debug('Update frame2')
    mask.save(os.path.join(base_dir, 'frame2.bmp'), "bmp")


def updateFrame3(weather):
    row_height = 16

    mask = Image.new('1', (EPD_HEIGHT, EPD_WIDTH), 255)
    draw = ImageDraw.Draw(mask)

    draw.text((border, 0), FORECAST_TITLE, font=fontBig, fill=0)
    draw.line((0, 2 * border + big_height, EPD_HEIGHT, 2 * border + big_height), fill=0)
    draw.line((column1, 2 * border + big_height, column1, EPD_WIDTH - 15), fill=0)
    draw.line((column2, 2 * border + big_height, column2, EPD_WIDTH - 20), fill=0)
    draw.line((column3, 2 * border + big_height, column3, EPD_WIDTH - 20), fill=0)
    draw.line((0, EPD_WIDTH - 15, EPD_HEIGHT, EPD_WIDTH - 15), fill=0)

    # Day0
    date = datetime.now() + timedelta(days=0)
    draw.text((border, 3 * border + big_height), date.strftime("%A"), font=fontSmall, fill=0)
    c1 = Image.open(os.path.join(folder_img, weather['conditionDay1'] + '.png'))
    c1 = c1.resize((icon_height * 2, icon_width * 2))
    mask.paste(c1, (border, 5 * border + big_height), c1)
    condTxt = wrap(weather['condDay1Txt'], 10)[:2]
    prev1 = condTxt[0]
    if len(condTxt) > 1:
        prev2 = condTxt[1]
        draw.text((border, 5 * row_height+3), prev1, font=fontExtraSmall, fill=0)
        draw.text((border, 6 * row_height+2), prev2, font=fontExtraSmall, fill=0)
    else:
        draw.text((border, 6 * row_height+3), prev1, font=fontExtraSmall, fill=0)

    draw.text((border, 7 * row_height+1), str(weather['tempMinDay1']) + '°C', font=fontMedium, fill=0)
    draw.text((border, 8 * row_height+2), str(weather['tempMaxDay1']) + '°C', font=fontMedium, fill=0)

    # Day1
    date = datetime.now() + timedelta(days=1)
    draw.text((border + column1, 3 * border + big_height), date.strftime("%A"), font=fontSmall, fill=0)
    c1 = Image.open(os.path.join(folder_img, weather['conditionDay2'] + '.png'))
    c1 = c1.resize((icon_height * 2, icon_width * 2))
    mask.paste(c1, (border + column1, 5 * border + big_height), c1)
    condTxt = wrap(weather['condDay2Txt'], 10)[:2]
    prev1 = condTxt[0]
    if len(condTxt) > 1:
        prev2 = condTxt[1]
        draw.text((border + column1, 5 * row_height+3), prev1, font=fontExtraSmall, fill=0)
        draw.text((border + column1, 6 * row_height+2), prev2, font=fontExtraSmall, fill=0)
    else:
        draw.text((border + column1, 6 * row_height+3), prev1, font=fontExtraSmall, fill=0)

    draw.text((border + column1, 7 * row_height+1), str(weather['tempMinDay2']) + '°C', font=fontMedium, fill=0)
    draw.text((border + column1, 8 * row_height+2), str(weather['tempMaxDay2']) + '°C', font=fontMedium, fill=0)

    # Day2
    date = datetime.now() + timedelta(days=2)
    draw.text((border + column2, 3 * border + big_height), date.strftime("%A"), font=fontSmall, fill=0)
    c1 = Image.open(os.path.join(folder_img, weather['conditionDay3'] + '.png'))
    c1 = c1.resize((icon_height * 2, icon_width * 2))
    mask.paste(c1, (border + column2, 5 * border + big_height), c1)
    condTxt = wrap(weather['condDay3Txt'], 10)[:2]
    prev1 = condTxt[0]
    if len(condTxt) > 1:
        prev2 = condTxt[1]
        draw.text((border + column2, 5 * row_height+3), prev1, font=fontExtraSmall, fill=0)
        draw.text((border + column2, 6 * row_height+2), prev2, font=fontExtraSmall, fill=0)
    else:
        draw.text((border + column2, 6 * row_height+3), prev1, font=fontExtraSmall, fill=0)

    draw.text((border + column2, 7 * row_height+1), str(weather['tempMinDay3']) + '°C', font=fontMedium, fill=0)
    draw.text((border + column2, 8 * row_height+2), str(weather['tempMaxDay3']) + '°C', font=fontMedium, fill=0)

    # Day3
    date = datetime.now() + timedelta(days=3)
    draw.text((border + column3, 3 * border + big_height), date.strftime("%A"), font=fontSmall, fill=0)
    c1 = Image.open(os.path.join(folder_img, weather['conditionDay4'] + '.png'))
    c1 = c1.resize((icon_height * 2, icon_width * 2))
    mask.paste(c1, (border + column3, 5 * border + big_height), c1)
    condTxt = wrap(weather['condDay4Txt'], 10)[:2]
    prev1 = condTxt[0]
    if len(condTxt) > 1:
        prev2 = condTxt[1]
        draw.text((border + column3, 5 * row_height+3), prev1, font=fontExtraSmall, fill=0)
        draw.text((border + column3, 6 * row_height+2), prev2, font=fontExtraSmall, fill=0)
    else:
        draw.text((border + column3, 6 * row_height+3), prev1, font=fontExtraSmall, fill=0)

    draw.text((border + column3, 7 * row_height+1), str(weather['tempMinDay4']) + '°C', font=fontMedium, fill=0)
    draw.text((border + column3, 8 * row_height+2), str(weather['tempMaxDay4']) + '°C', font=fontMedium, fill=0)

    refresh_time = time.strftime("%H:%M")
    refresh_date = time.strftime("%Y-%m-%d")
    # refresh_date = time.strftime("%Y. %B %-d. %A")
    draw.text((border, EPD_WIDTH - 18), refresh_date + ' ' + refresh_time, font=fontSmall, fill=0)
    draw.text((column3 - border*2, EPD_WIDTH - 18), 'BAT: ' + weather['battery'] + 'V', font=fontSmall, fill=0)

    debug('Update frame3')
    mask.save(os.path.join(base_dir, 'frame3.bmp'), "bmp")


if __name__ == "__main__":
    while True:
        try:
            w = getWeatherData()
        # updateFrame1(w)
        # time.sleep(5)
        except Exception as e:
            print(e)
        else:
            updateFrame1(w)
            updateFrame2(w)
            updateFrame3(w)
        if test_mode:
            break
        time.sleep(SLEEPTIME)
