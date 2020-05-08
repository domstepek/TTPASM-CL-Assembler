from googleapiclient.discovery import build
from google.oauth2 import service_account
import time

class SheetService:
  def __init__(self):
    self.__scopes = ['https://www.googleapis.com/auth/spreadsheets']
    self.__service_acc_file = "service-account.json"
    self.__enabled = False

  def Login(self) -> None:
    creds = service_account.Credentials.from_service_account_file(self.__service_acc_file, scopes=self.__scopes)
    self.__service = build('sheets', 'v4', credentials=creds)
    self.__enabled = True

  def GetSheetData(self, spreadsheetID : str, range : str, wait_for_ready : bool) -> list:
    while True:
      try:
        no_of_retry = 5
        retry_count = 0
        response = "errorValue"

        while 'errorValue' in str(response) or 'Loading...' in str(response) and retry_count < no_of_retry:
          response = self.__service.spreadsheets().values().get(spreadsheetId=spreadsheetID,range=range).execute()
          time.sleep(2.5)
          retry_count += 1

        if 'errorValue' in response:
          raise ConnectionError('Could not retrieve data')
          
        return response.get('values', [])
      except ConnectionResetError:
        print ("Trying to connect to Google Sheets...")
        self.Login()

  def WriteSheetData(self, spreadsheetID : str, range : str, data : object):
    data_resource = {
      'majorDimension' : 'COLUMNS',
      'values' : data
    }

    while True:
      try:
        self.__service.spreadsheets().values().update(spreadsheetId=spreadsheetID, range=range, body=data_resource, valueInputOption="RAW").execute()
        return True
      except ConnectionResetError:
        print ("Trying to connect to Google Sheets...")
        self.Login()

