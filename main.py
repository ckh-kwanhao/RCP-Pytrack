#!/usr/bin/env python
#
# Copyright (c) 2019, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

import machine
import math
import network
import os
import time
import utime
import gc
import socket

from network import LoRa
from machine import RTC
from machine import SD
#from L76GNSS import L76GNSS
from L76GNSV4 import L76GNSS
from pytrack import Pytrack


time.sleep(2)
gc.enable()


#setup LoRa
lora = network.LoRa(mode=LoRa.LORA, region=LoRa.AS923, frequency=923000000, tx_power=14, bandwidth=LoRa.BW_125KHZ, sf=12, preamble=6, coding_rate=LoRa.CODING_4_5, power_mode=LoRa.ALWAYS_ON, tx_iq=False, rx_iq=False, adr=False, public=True, tx_retries=1, device_class=LoRa.CLASS_A)
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
s.setblocking(False)

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(7200)
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

py = Pytrack()
l76 = L76GNSS(py, timeout=30)

sd = SD()
os.mount(sd, '/sd')
#a=open("/sd/lorastats.csv", "w")
#a.close()
#b=open("/sd/gps-lora.csv", "w")
#b.close()
#c=open("/sd/gps-record.csv", "w")
#c.close()
#import utime; start = utime.ticks_us();diff = time.ticks_diff(time.ticks_us(), start); print(diff)
i=0

while (True):
    start = utime.ticks_ms()
    l76_coord = l76.coordinates()
    get_loc = l76.get_location()

    gps_stats = [get_loc['latitude'],get_loc['longitude'],get_loc['altitude']]
    print(gps_stats)
    rtcnow = rtc.now()
    for r in rtcnow:
        gps_stats.append(r)
    print(gps_stats)

    if s.recv(64) == b'Ping':
        i += 1
        print('Received Ping', i)
        lorastats = lora.stats()
        print(lorastats)
        with open("/sd/lorastats_080220_S2_test4.csv", "a") as lora_file:
            lora_file.write(", ".join(str(j) for j in lorastats) + "\n")
        lora_file.close()

        with open('/sd/gps-lora_080220_S2_test4.csv', 'a') as gps_lora:
            #gps_lora.write("{} - {} - {} - {}\n".format(get_loc['latitude'], get_loc['longitude'],get_loc['altitude'], rtc.now()))
            gps_lora.write(", ".join(str(k) for k in gps_stats) + "\n")
        gps_lora.close()

    with open('/sd/gps-record__080220_S2_test4.csv', 'a') as gps_file:
        #gps_file.write("{} - {} - {} - {}\n".format(get_loc['latitude'], get_loc['longitude'],get_loc['altitude'], rtc.now()))
        gps_file.write(", ".join(str(k) for k in gps_stats) + "\n")

    gps_file.close()
    #f.write("{} - {}\n".format(coord, rtc.now()))
    print("{} - {} - {} - {}".format(get_loc['latitude'], get_loc['longitude'],get_loc['altitude'], gc.mem_free()))
    time.sleep(5)
    print('Looping')
