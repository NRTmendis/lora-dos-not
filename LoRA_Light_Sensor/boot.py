""" Created by Nissanka Mendis on 18/03/2018"""

from machine import UART
import machine
import os

uart = UART(0, baudrate=115200)
os.dupterm(uart)

machine.main('main.py')
