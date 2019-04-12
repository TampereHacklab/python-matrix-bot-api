#!/usr/bin/env python3

import subprocess
import os
import urllib.request

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        if len(args) == 2:
            icao = args[1]
            metar_url = "https://tgftp.nws.noaa.gov/data/observations/metar/stations/" + icao.upper() + ".TXT"
            response = urllib.request.urlopen(metar_url)
            lines = response.readlines()
            room.send_text(lines[1].decode("utf-8"))
        else:
            room.send_text('Usage: !metar <icao code>')
