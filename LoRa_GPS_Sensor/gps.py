import os
import time
import struct
import machine
from machine import UART


#Minimalistic NMEA-0183 message parser, based on micropyGPS
#Version 0.1 - January 2017
#Autor: Peter Affolter

import utime


def GPS_UART_start():
    #print ('Start GPS UART1')
    com = UART(1,  pins=("P3",  "P4"),  baudrate=9600)
    # pins=("G23",  "G24")  
    com.init(9600,  bits=8,  parity=None,  stop=1)
    time.sleep(1)
    return(com)


def GPS_go(com):
    while (True):
        if (com.any()):
            data =com.readline()
            #print (data)
            if (data[0:7] == b'$GPGGA,'):
                place = NmeaParser()
                place.update(data)
                print (place.longitude,  ":",  place.latitude)
                info1 = struct.pack('hii',  machine.rng()&0xffff,  int(place.longitude*100000),  int(place.latitude*100000))

                
                

class NmeaParser(object):
    """NMEA Sentence Parser. Creates object that stores all relevant GPS data and statistics.
    Parses sentences using update(). """
    
    def __init__(self):
        """Setup GPS Object Status Flags, Internal Data Registers, etc"""

        #####################
        # Data From Sentences
        # Time
        self.utc = (0)
        
        # Object Status Flags
        self.fix_time = 0
        self.valid_sentence = False

        # Position/Motion
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0

        # GPS Info
        self.satellites_in_use = 0
        self.hdop = 0.0
        self.fix_stat = 0
        
        #raw data segments
        self.nmea_segments = []

    def update(self,  sentence):
        self.valid_sentence = False
        self.nmea_segments = str(sentence).split(',')
       
        #Parse GPGGA
        if (self.nmea_segments[0] == "b'GPGGA"):
            self.valid_sentence = True
            try:
                # UTC Timestamp
                 utc_string = self.nmea_segments[1]
                 
                # Skip timestamp if receiver doesn't have on yet
                 if utc_string:
                    hours = int(utc_string[0:2])
                    minutes = int(utc_string[2:4])
                    seconds = float(utc_string[4:])
                 else:
                    hours = 0
                    minutes = 0
                    seconds = 0.0
                    
                 # Number of Satellites in Use
                 satellites_in_use = int(self.nmea_segments[7])
                 # Horizontal Dilution of Precision
                 hdop = float(self.nmea_segments[8])

                 # Get Fix Status
                 fix_stat = int(self.nmea_segments[6])
            except ValueError:
                return False
            
         # Process Location and Speed Data if Fix is GOOD
            if fix_stat:
                # Longitude / Latitude
                try:
                    # Latitude
                    l_string = self.nmea_segments[2]
                    lat_degs = float(l_string[0:2])
                    lat_mins = float(l_string[2:])
                    lat_hemi = self.nmea_segments[3]
                    # Longitude
                    l_string = self.nmea_segments[4]
                    lon_degs = float(l_string[0:3])
                    lon_mins = float(l_string[3:])
                    lon_hemi = self.nmea_segments[5]				
                except ValueError:
                    return False
        
                # Altitude / Height Above Geoid
                try:
                    altitude = float(self.nmea_segments[9])
                    geoid_height = float(self.nmea_segments[11])
                except ValueError:
                    return False
                    
                # Update Object Data
                self.latitude = lat_degs + (lat_mins/60)
                if lat_hemi == 'S':
                    self.latitude = -self.latitude
                self.longitude = lon_degs + (lon_mins/60)
                if lon_hemi == 'W':
                    self.longitude = -self.longitude
                self.altitude = altitude
                self.geoid_height = geoid_height
                
            # Update Object Data
            self.timestamp = (hours, minutes, seconds)
            self.satellites_in_use = satellites_in_use
            self.hdop = hdop
            self.fix_stat = fix_stat
        
            # If Fix is GOOD, update fix timestamp
            if fix_stat:
                self.fix_time = utime.time()

            return True
            

com=GPS_UART_start()
