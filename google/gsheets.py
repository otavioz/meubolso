﻿from __future__ import print_function
import pickle
import consts as CONS
import os.path
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class GSheets:
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    def __init__(self):
        self.sheet_id = CONS.SPREADSHEET_ID
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'keys/credentials.json',CONS.GOOGLE_SHEETS_SCOPES) #excluir token.pickle caso mude o scope
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def append(self,values,range_,list_=False):
        values = [values] if not list_ else values
        body = {
            "range": range_,
            "values": values

        }
        service = build('sheets', 'v4', credentials=self.creds)
        return service.spreadsheets().values().append(spreadsheetId=self.sheet_id,valueInputOption="USER_ENTERED",range=range_,body=body).execute()
    
    def insert(self,values,range_,list_=False):
        values = [values] if not list_ else values
        body = {
            "range": range_,
            "values": values
        }
        service = build('sheets', 'v4', credentials=self.creds)
        return service.spreadsheets().values().update(spreadsheetId=self.sheet_id,valueInputOption="USER_ENTERED",range=range_,body=body).execute()

    def get(self,sheet_range,majorDimension='COLUMNS',value_render_option = 'UNFORMATTED_VALUE',date_time_render_option = 'FORMATTED_STRING'):
        service = build('sheets', 'v4', credentials=self.creds)
        # pylint: disable=maybe-no-member
        return service.spreadsheets().values().get(spreadsheetId=self.sheet_id,range=sheet_range,valueRenderOption=value_render_option,majorDimension=majorDimension,dateTimeRenderOption=date_time_render_option).execute()
 