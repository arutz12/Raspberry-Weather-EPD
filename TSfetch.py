# coding: utf-8
#
# Weather station display for Raspberry and Waveshare 2.7" e-Paper display
# (fetch ThingSpeak data)
#
# Copyright by Antal Rutz
#
# Documentation and full source code:
# https://github.com/arutz74/raspberry-weather-epd-2in7
#

import os
import requests
import json
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path)

TS_API_KEY = os.environ.get('TS_API_KEY')
TS_CHANNEL_ID = os.environ.get('TS_CHANNEL_ID')
TS_READ_URL = 'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results=1'.format(TS_CHANNEL_ID, TS_API_KEY)


def fetchThingSpeak():
    TS_DATA = {}
    try:
        r = requests.get(TS_READ_URL)
    except Exception as e:
        print(e)
        return {'TEMP': 0, 'VOLT': 0, 'UPDATED': 0}

    ts_result = json.loads(r.content)
    TS_DATA['TEMP'] = ts_result['feeds'][0]['field1']
    TS_DATA['VOLT'] = ts_result['feeds'][0]['field2']
    TS_DATA['UPDATED'] = ts_result['feeds'][0]['created_at']

    return TS_DATA


if __name__ == '__main__':
    from pprint import pprint

    ts_data = fetchThingSpeak()
    pprint(ts_data)
