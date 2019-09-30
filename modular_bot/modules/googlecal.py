from __future__ import print_function
from matrix_bot_api.matrix_bot_api import MatrixBotAPI
from datetime import datetime
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


import time
import os

#
# Google calendar notifications
#
# Note: Provide a token.pickle file for the service. 
# It's created on first run (run from console!) and 
# can be copied to another computer.
#
# ENV variables:
#
# Google calendar creds file: (defaults to this)
# GCAL_CREDENTIALS="credentials.json"
#
# Room to deliver daily reports:
# GCAL_LIVE_ROOM="#room:matrix.org"
#  
#

class MatrixModule:
    def matrix_start(self, bot):
        self.bot = bot
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.credentials_file = "credentials.json"
        if os.getenv("GCAL_CREDENTIALS"):
            self.credentials_file = os.getenv("GCAL_CREDENTIALS")
        self.live_room = os.getenv("GCAL_LIVE_ROOM")
        self.service = None
        self.report_time = 10
        self.last_report_date = None

        creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)


    def matrix_callback(self, bot, room, event):
        if not self.service:
            room.send_text('Google calendar not set up for this bot.')
            return
        args = event['content']['body'].split()
        events = []

        if len(args) == 2:
            if args[1] == 'today':
                events = self.list_today()
        else:
            events = self.list_upcoming()

        if not events:
            room.send_text('No events found.')
        self.send_events(events, room)

    def send_events(self, events, room):
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            room.send_html(self.parseDate(start) + " <a href=\"" + event['htmlLink'] + "\">" + event['summary'] + "</a>")

    def list_upcoming(self):
        startTime = datetime.datetime.utcnow()
        now = startTime.isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def list_today(self):
        startTime = datetime.datetime.utcnow()
        startTime = startTime - datetime.timedelta(hours=startTime.hour, minutes=startTime.minute)
        endTime = startTime + datetime.timedelta(hours=24)
        now = startTime.isoformat() + 'Z'
        end = endTime.isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                    timeMax=end, maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def matrix_poll(self, bot, pollcount):
        if not self.service:
            return
        if not self.live_room:
            return
        if pollcount % (6 * 5) == 0: # Poll every 5 min
            pass # Not implemented
        
        today = datetime.datetime.now()
        since_last = 999
        if self.last_report_date:
            since_last = (today - self.last_report_date).total_seconds() / 60 / 60
        if since_last > 20 and today.hour >= self.report_time:
            self.last_report_date = today
            events = self.list_today()
            room = bot.get_room(self.live_room)
            self.send_events(events, room)

    def help(self):
        return('Google calendar. Lists 10 next events by default. today = list today\'s events.')

    def parseDate(self, start):
        try: 
            dt = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
            return dt.strftime("%d.%m %H:%M")
        except ValueError:
            dt = datetime.datetime.strptime(start, '%Y-%m-%d')
            return dt.strftime("%d.%m")
