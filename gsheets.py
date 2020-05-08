from googleapiclient.discovery import build
from google.oauth2 import service_account
import time

class SheetService:
  MAX_RETRIES = 5 # Max amount of retries available
  TIMEOUT_WAIT = 2.5 # Time between retries

  def __init__(self):
    self.__scopes = ['https://www.googleapis.com/auth/spreadsheets'] # Read and write permissions
    self.__service_acc_file = "service-account.json"
    self.__enabled = False

  def Login(self) -> None:
    # Create a credentials object with read/write scope, build service object
    creds = service_account.Credentials.from_service_account_file(self.__service_acc_file, scopes=self.__scopes)
    self.__service = build('sheets', 'v4', credentials=creds)

  def GetSheetData(self, spreadsheetID : str, range : str) -> list:
    while True:
      try:
        retry_count = 0
        response = "errorValue"

        # Attempt to read RAM file
        while 'errorValue' in str(response) or 'Loading...' in str(response) and retry_count < self.MAX_RETRIES:
          response = self.__service.spreadsheets().values().get(spreadsheetId=spreadsheetID,range=range).execute()
          time.sleep(self.TIMEOUT_WAIT)

          retry_count += 1

        if 'errorValue' in response:
          raise ConnectionError('Could not retrieve data')
          
        return response.get('values', [])
      except ConnectionResetError:
        print ("Trying to connect to Google Sheets...")
        self.Login()

  def WriteSheetData(self, spreadsheetID : str, range : str, data : object) -> bool:
    # Resource object needed by GSheet API
    data_resource = {
      'majorDimension' : 'COLUMNS',
      'values' : data
    }

    while True:
      try:
        # Send request to write
        self.__service.spreadsheets().values().update(spreadsheetId=spreadsheetID, range=range, body=data_resource, valueInputOption="RAW").execute()
        return True
      except ConnectionResetError:
        print ("Trying to connect to Google Sheets...")
        self.Login()

