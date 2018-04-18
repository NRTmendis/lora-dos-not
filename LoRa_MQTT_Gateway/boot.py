""" Created by Nissanka Mendis on 18/03/2018"""
# boot.py -- run on boot-up
import os

from machine import UART
uart = UART(0, 115200)
os.dupterm(uart)