#!/usr/bin/env python3

import subprocess
import os
import urllib.request
import json
import time

class MatrixModule:
    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        icao = "EFJM"

        if len(args) == 2:
            icao = args[1]

        timenow = time.localtime(time.time())

        today = str(timenow[0]) + "-" + str(timenow[1]) + "-" + str(timenow[2])

        log_url = "https://ktrax.kisstech.ch/cgi-bin/ktrax.cgi?db=sortie&query_type=ap&tz=3&id=" + icao.upper() + "&dbeg=" + today + "&dend=" + today
        response = urllib.request.urlopen(log_url)
        data = json.loads(response.read().decode("utf-8"))
        # print(json.dumps(data, sort_keys=True, indent=4))
        out = ""
        if len(data["sorties"]) == 0:
            out = "No known flights today at " + icao
        else:
            out = "Flights at " + icao.upper() + " " + today + ":\n"
            for sortie in data["sorties"]:
                # Don't show towplanes
                if sortie["type"] != 2:
                    if sortie["ldg"]["time"] == "":
                        sortie["ldg"]["time"] = u"  \u2708  "
                    else:
                        sortie["ldg"]["time"] = "-" + sortie["ldg"]["time"]
                        if sortie["ldg"]["loc"] != sortie["tkof"]["loc"]:
                            sortie["tkof"]["time"] = sortie["tkof"]["time"] + "(" + sortie["tkof"]["loc"] + ")"
                            sortie["ldg"]["time"] = sortie["ldg"]["time"] + "(" + sortie["ldg"]["loc"] + ") "
                    if sortie["cs"] == "-":
                        sortie["cs"] = ""
                    if sortie["cn"] == "-":
                        sortie["cn"] = "?"
                    out = out + sortie["tkof"]["time"] + sortie["ldg"]["time"] + " " + sortie["dt"] + " " + sortie["actype"] + " " + sortie["cs"] + " " + sortie["cn"] + "\n"
            
        room.send_text(out)

    def help(self):
        return('OGN Field log (usage: !flog <icao code>)')
