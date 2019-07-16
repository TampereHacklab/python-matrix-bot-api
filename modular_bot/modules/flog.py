#!/usr/bin/env python3

import subprocess
import os
import urllib.request
import json
import time
import datetime
"""
 OGN Flight Log

 Supports !flog command and live logging
 Set FLOG_DEFAULT_FIELD to set the default airfield OGN site (for example EFJM)
 Set FLOG_LIVE_ROOM for live logging of the default field. Bot must be present in the room.

 Uses ktrax API for fetching data. Consider donating to ktrax if you use this.
"""

class MatrixModule:
    def matrix_start(self, bot):
        self.default_field = os.getenv("FLOG_DEFAULT_FIELD")
        print("flog default field is", self.default_field)
        self.live_room = os.getenv("FLOG_LIVE_ROOM")
        if os.getenv("FLOG_LIVE_ROOM"):
            print("flog live room is", self.live_room)
        self.bot = bot
        self.logged_flights = []
        self.logged_flights_date = ""

    def matrix_poll(self, bot, pollcount):
        if not self.live_room:
            return

        if pollcount % (6 * 5) == 0: # Poll every 5 min
            data = self.get_flights(self.default_field)

            # Date changed - reset flight count
            if data["begin_date"] != self.logged_flights_date:
                self.logged_flights = []
                self.logged_flights_date = data["begin_date"]

            flights = []

            for sortie in data["sorties"]:
                # Don't show towplanes
                if sortie["type"] != 2:
                    # Count only landed gliders
                    if sortie["ldg"]["time"] != "":
                        flights.append(
                            { 
                                "takeoff": sortie["tkof"]["time"], 
                                "landing": sortie["ldg"]["time"],
                                "duration": sortie["dt"],
                                "glider": self.glider2string(sortie),
                                "altitude": str(sortie["dalt"]),
                                "seq": sortie["seq"]
                            })
            for flight in flights:
                if flight["seq"] not in self.logged_flights:
                    bot.send_notification(flight["takeoff"] + "-" + flight["landing"] + " (" + flight["duration"] + ") - " + flight["altitude"] + "m " + flight["glider"], self.live_room)
                    self.logged_flights.append(flight["seq"])

    def matrix_callback(self, bot, room, event):
        args = event['content']['body'].split()
        icao = self.default_field

        if len(args) == 2:
            icao = args[1]

        data = self.get_flights(icao)

        out = ""
        if len(data["sorties"]) == 0:
            out = "No known flights today at " + icao
        else:
            out = "Flights at " + icao.upper() + " today:\n"
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

                    out = out + sortie["tkof"]["time"] + sortie["ldg"]["time"] + " " + sortie["dt"] + " " + str(sortie["dalt"]) + "m " + self.glider2string(sortie) + "\n"
            
        room.send_text(out)

    def help(self):
        return('OGN Field log (usage: !flog <icao code>)')

    def get_flights(self, icao):
        timenow = time.localtime(time.time())

        today = str(timenow[0]) + "-" + str(timenow[1]) + "-" + str(timenow[2])

        log_url = "https://ktrax.kisstech.ch/cgi-bin/ktrax.cgi?db=sortie&query_type=ap&tz=3&id=" + icao.upper() + "&dbeg=" + today + "&dend=" + today
        response = urllib.request.urlopen(log_url)
        data = json.loads(response.read().decode("utf-8"))
        # print(json.dumps(data, sort_keys=True, indent=4))
        return data

    def glider2string(self, sortie):
        actype = sortie["actype"]
        cs = sortie["cs"]
        cn = sortie["cn"]
        if cs == "-":
            cs = ""
        if cn == "-":
            cn = ""

        if actype == "" and cs == "" and cn == "":
            return "????"
        return (actype + " " + cs + " " + cn).strip()
