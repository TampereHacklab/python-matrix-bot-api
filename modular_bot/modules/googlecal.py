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
# ENV variables:
#
# Google calendar creds file:
# GCAL_CREDENTIALS="credentials.json" 
#

class MatrixModule:

    def matrix_start(self, bot):
        self.bot = bot
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.credentials_file = os.getenv("GCAL_CREDENTIALS")
        self.service = None
        if not self.credentials_file:
            return

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

        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            room.send_text('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            room.send_html(self.parseDate(start) + " <a href=\"" + event['htmlLink'] + "\">" + event['summary'] + "</a>")


    def matrix_poll(self, bot, pollcount):
        if not self.service:
            return
        if pollcount % (6 * 5) == 0: # Poll every 5 min
            pass

    def help(self):
        return('Google calendar. No command line usage.')

    def parseDate(self, start):
        try: 
            dt = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
            return dt.strftime("%d.%m %H:%M")
        except ValueError:
            dt = datetime.datetime.strptime(start, '%Y-%m-%d')
            return dt.strftime("%d.%m")
