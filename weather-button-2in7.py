# coding: utf-8
# Weather station display for Raspberry and Waveshare 2.7" e-Paper display
# (button event handling)
#
# Copyright by Antal Rutz
#
# Documentation and full source code:
# https://github.com/arutz12/Raspberry-Weather-EPD-2in7
# 

import sys
import os
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from PIL import Image
from datetime import datetime

from gpiozero import Button
from signal import pause
from functools import partial
import waveshare_epd.epd2in7

DEBUG = False

if DEBUG:
    from pprint import pprint

epd = waveshare_epd.epd2in7.EPD()
epd.init()
EPD_WIDTH = waveshare_epd.epd2in7.EPD_WIDTH
EPD_HEIGHT = waveshare_epd.epd2in7.EPD_HEIGHT

def debug(val):
    if DEBUG:
        pprint(val)


def EPDsleep(c=None):
    clearDisplay()
    epd.sleep()


def clearDisplay(c=None):
    debug('TIME: ' + str(datetime.now()))
    debug('Clear Display')
    epd.Clear(0xFF)


def displayFrame(frame_name):
    # clearDisplay()
    debug('TIME: ' + str(datetime.now()))
    debug('Displaying ' + frame_name + '.bmp')
    frame = Image.open(os.path.join(base_dir, frame_name + '.bmp'))
    epd.display(epd.getbuffer(frame))


if __name__ == "__main__":
    key1 = 5
    key2 = 6
    key3 = 13
    key4 = 19
    keys = (key1, key2, key3, key4)
    buttons = []

    for key in keys:
        buttons.append(Button(key))

    for b in range(3):
        buttons[b].when_pressed = partial(displayFrame, 'frame' + str(b+1))
    buttons[3].when_pressed = clearDisplay

    print("Waiting for input.")
    pause()

