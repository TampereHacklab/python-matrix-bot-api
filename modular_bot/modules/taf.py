#!/usr/bin/env python3

import subprocess
import os
import urllib.request

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        if len(args) == 2:
            icao = args[1]
            taf_url = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=tafs&requestType=retrieve&format=csv&hoursBeforeNow=3&timeType=issue&mostRecent=true&stationString=" + icao.upper()
            response = urllib.request.urlopen(taf_url)
            lines = response.readlines()
            if len(lines) > 6:
                taf = lines[6].decode("utf-8").split(',')[0]
                room.send_text(taf.strip())
            else:
                room.send_text('Cannot find taf for ' + icao)
        else:
            room.send_text('Usage: !taf <icao code>')
            
    def help(self):
        return('Taf data access (usage: !taf <icao code>)')
