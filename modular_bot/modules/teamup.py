from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from pyteamup import Calendar, Event
from datetime import datetime
import time
import os

#
# TeamUp calendar notifications
#
# Set env variables:
#
# TU_APIKEY - api key to use
# TU_CALENDARS - list of calendar id's and rooms to notify about them
#
# Example: TU_CALENDARS="123abcdefg#example:matrix.org,987asdfg#other:matrix.org"
#

class MatrixModule:
    def matrix_start(self, bot):
        self.api_key = None
        self.calendars = []

        if os.getenv("TU_APIKEY"):
            self.api_key = os.getenv("TU_APIKEY")
        else:
            return

        calendars = os.getenv("TU_CALENDARS").split(',')

        for calendarstring in calendars:
            calendardef = calendarstring.split('#')
            calendar = Calendar(calendardef[0], self.api_key)
            calendar.timestamp = int(time.time())
            calendar.notifyroom = '#' + calendardef[1]
            self.calendars.append(calendar)
            
        self.bot = bot

    def matrix_poll(self, bot, pollcount):
        if not self.api_key:
            return
        if pollcount % (6 * 5) == 0: # Poll every 5 min
            for calendar in self.calendars:
                events,timestamp = self.poll_server(calendar)
                calendar.timestamp = timestamp
                for event in events:
                    bot.send_notification('Calendar: ' + self.eventToString(event), calendar.notifyroom)

    def help(self):
        return('Polls teamup calendar. No command line usage.')

    def poll_server(self, calendar):
        events, timestamp = calendar.get_changed_events(calendar.timestamp)
        return events, timestamp

    def to_datetime(self, dts):
        try:
            return datetime.strptime(dts, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            pos = len(dts) - 3
            dts = dts[:pos] + dts[pos+1:]
            return datetime.strptime(dts, '%Y-%m-%dT%H:%M:%S%z')

    def eventToString(self, event):
        startdt = self.to_datetime(event['start_dt'])
        if len(event['title']) == 0:
            event['title'] = '(empty name)'

        if(event['delete_dt']):
            s = event['title'] + ' deleted.'
        else:
            s = event['title'] + " " + (event['notes'] or '') + ' ' + str(startdt.day) + '.' + str(startdt.month)
            if not event['all_day']:
                s = s + ' ' + startdt.strftime("%H:%M") + ' (' + str(event['duration']) + ' min)'
        return s
