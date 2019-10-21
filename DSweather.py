# coding: utf-8
#
# Weather station display for Raspberry and Waveshare 2.7" e-Paper display
# (fetch DarkSky weather data)
#
# Copyright by Antal Rutz
#
# Documentation and full source code:
# https://github.com/arutz12/Raspberry-Weather-EPD-2in7
#


import os
from darksky.api import DarkSky
from darksky.types import languages, units, weather
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))

# .env
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

DARKSKY_API_KEY = os.environ.get('DARKSKY_API_KEY')
DARKSKY_LONGITUDE = os.environ.get('DARKSKY_LONGITUDE')
DARKSKY_LATITUDE = os.environ.get('DARKSKY_LATITUDE')
DARKSKY_LANGUAGE = os.environ.get('DARKSKY_LANGUAGE')
DARKSKY_UNITS = os.environ.get('DARKSKY_UNITS')

MAX_DAYS = 4
MAX_HOURS = 24


def wind_direction(degrees):
    """ Convert wind degrees to direction """
    try:
        degrees = int(degrees)
    except ValueError:
        return ''

    if degrees < 23 or degrees >= 338:
        return 'N'
    elif degrees < 68:
        return 'NE'
    elif degrees < 113:
        return 'E'
    elif degrees < 158:
        return 'SE'
    elif degrees < 203:
        return 'S'
    elif degrees < 248:
        return 'SW'
    elif degrees < 293:
        return 'W'
    elif degrees < 338:
        return 'NW'


def fetchDarkSkyWeather():
    dark_sky = DarkSky(DARKSKY_API_KEY)

    forecast = dark_sky.get_forecast(
        DARKSKY_LATITUDE, DARKSKY_LONGITUDE,
        extend=False,
        lang=getattr(languages, DARKSKY_LANGUAGE, 'ENGLISH'),
        units=getattr(units, DARKSKY_UNITS, 'SU'),
        exclude=[weather.MINUTELY, weather.ALERTS, weather.HOURLY]
    )

    cur_weather = forecast.currently
    # hourly_weather = forecast.hourly.data
    daily_weather = forecast.daily.data[0:MAX_DAYS+1]

    # CURRENT
    CURRENT = {
        'summary':              cur_weather.summary,
        'icon':                 cur_weather.icon,
        'precip_probability':   round(int(cur_weather.precip_probability * 100), -1),
        'precip_type':          cur_weather.precip_type,
        'temperature':          cur_weather.temperature,
        'humidity':             int(cur_weather.humidity * 100),
        'wind_speed':           cur_weather.wind_speed,
        'wind_bearing':         cur_weather.wind_bearing,
        'pressure':             round(cur_weather.pressure),
        'wind_direction':       wind_direction(cur_weather.wind_bearing),
        'cloud_cover':          int(cur_weather.cloud_cover * 100)
    }

    # DAILY
    DAILY = []
    for i, d in enumerate(daily_weather):
        DAILY.append({
            'date': str(d.time.date()),
            'summary':              d.summary,
            'icon':                 d.icon,
            'sunrise_time':         d.sunrise_time.time().strftime('%H:%M'),
            'sunset_time':          d.sunset_time.time().strftime('%H:%M'),
            'moon_phase':           d.moon_phase,
            'precip_intensity':     d.precip_intensity,
            'precip_probability':   round(int(d.precip_probability * 100), -1),
            'precip_type':          d.precip_type,
            'humidity':             int(d.humidity * 100),
            'pressure':             round(d.pressure),
            'wind_speed':           d.wind_speed,
            'wind_bearing':         d.wind_bearing,
            'wind_direction':       wind_direction(d.wind_bearing),
            'cloud_cover':          int(d.cloud_cover * 100),
            'uv_index':             d.uv_index,
            'temperature_min':      round(d.temperature_min),
            'temperature_max':      round(d.temperature_max)
        })

    return CURRENT, DAILY


if __name__ == '__main__':
    from pprint import pprint

    cur, daily = fetchDarkSkyWeather()
    pprint(cur)
    print('\n######################\n\n')
    pprint(daily)
