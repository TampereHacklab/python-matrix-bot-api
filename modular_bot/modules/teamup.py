from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from pyteamup import Calendar, Event
from datetime import datetime
import time
import os

#
# TeamUp calendar notifications
#
# Set env variables:
# TU_APIKEY TU_CALENDARID TU_NOTIFYROOM (last is the room to notify)
#

class MatrixModule:
    def matrix_start(self, bot):
        if os.getenv("TU_APIKEY") is None:
            return
        self.api_key = os.getenv("TU_APIKEY")
        self.calendar_id = os.getenv("TU_CALENDARID")
        self.notify_room = os.getenv("TU_NOTIFYROOM")

        self.calendar = Calendar(self.calendar_id, self.api_key)
        self.timestamp = int(time.time())
        self.bot = bot

    def matrix_poll(self, bot, pollcount):
        if not self.api_key:
            return
        if pollcount & 6 == 0: # Poll every 1 min
            events = self.poll_server()
            for event in events:
                self.send_notification('Calendar: ' + self.eventToString(event))

    def help(self):
        return('Polls teamup calendar. No command line usage.')

    def poll_server(self):
        events, timestamp = self.calendar.get_changed_events(self.timestamp)
        self.timestamp = timestamp
        return events

    def to_datetime(self, dts):
        try:
            return datetime.strptime(dts, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            pos = len(dts) - 3
            dts = dts[:pos] + dts[pos+1:]
            return datetime.strptime(dts, '%Y-%m-%dT%H:%M:%S%z')

    def eventToString(self, event):
        startdt = self.to_datetime(event['start_dt'])
        if(event['delete_dt']):
            s = event['title'] + ' deleted.'
        else:
            s = event['title'] + " " + (event['notes'] or '') + ' ' + str(startdt.day) + '.' + str(startdt.month)
            if not event['all_day']:
                s = s + ' ' + startdt.strftime("%H:%M") + ' (' + str(event['duration']) + ' min)'
        return s

    def send_notification(self, notification):
        for id, room in self.bot.client.get_rooms().items():
            if self.notify_room in room.aliases:
                room.send_text(notification)
