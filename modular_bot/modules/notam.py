#!/usr/bin/env python3

import subprocess
import os
import urllib.request
import re

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        if len(args) == 2 and len(args[1]) == 4:
            icao = args[1].upper()
            icao_first_letter = icao[2]
            if icao_first_letter < 'M':
                notam_url = "https://www.ais.fi/ais/bulletins/envfra.htm"
            else:
                notam_url = "https://www.ais.fi/ais/bulletins/envfrm.htm"
            print(notam_url)
            response = urllib.request.urlopen(notam_url)
            lines = response.readlines()
            lines = b''.join(lines)
            lines = lines.decode("ISO-8859-1")
            # Strip EN-ROUTE from end
            lines = lines[0:lines.find('<a name="EN-ROUTE">')]

            startpos = lines.find('<a name="' + icao + '">')
            notamfound = False
            if startpos > -1:
                endpos = lines.find('<h3>', startpos)
                if endpos == -1:
                    endpos = len(lines)
                notam = lines[startpos:endpos]
                notam = re.sub('<[^<]+?>', ' ', notam)
                if len(notam) > 4:
                    notamfound = True
                    room.send_text(notam)
            if not notamfound:
                room.send_text('Cannot parse notam for ' + icao + ' at ' + notam_url)

        else:
            room.send_text('Usage: !notam <icao code>')

    def help(self):
        return('Finnish notam access (usage: !notam <icao code>)')
