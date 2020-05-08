"""
Name: gsheets.py
Description:
This script is the class definition and implementation for the SheetService used
by assemble.py. The SheetService acts as a wrapper for the Google Sheets API and
is capable of updating and reading spreadsheet cells.
Coded by: Dom Stepek
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
import time

class SheetService:
  @property
  def MaxRetries(self) -> int:
    return self.__max_retries

  @MaxRetries.setter
  def MaxRetries(self, value : int) -> None:
    if value < 1:
      raise ValueError("Max retries must be greater than 0")
    self.__max_retries = value

  @property
  def TimeoutWait(self) -> float:
    return self.__timeout_wait

  @TimeoutWait.setter
  def TimeoutWait(self, value : float) -> None:
    if value < 0:
      raise ValueError("Value must be greater than 0")
      self.__timeout_wait = value

  def __init__(self):
    self.__scopes = ['https://www.googleapis.com/auth/spreadsheets'] # Read and write permissions
    self.__service_acc_file = "assets/service-account.json"
    self.__max_retries = 5 # Default: 5 max retries 
    self.__timeout_wait = 2.5 # Default: 2.5 second timeout

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
        while 'errorValue' in str(response) or 'Loading...' in str(response) and retry_count < self.MaxRetries:
          response = self.__service.spreadsheets().values().get(spreadsheetId=spreadsheetID,range=range).execute()
          time.sleep(self.TimeoutWait)

          retry_count += 1

        if 'errorValue' in response:
          raise ConnectionError('Could not retrieve data')
          
        return response.get('values', [])
      except ConnectionResetError:
        print ("Trying to connect to Google Sheets...")
        self.Login()

  def WriteSheetData(self, spreadsheetID : str, range : str, data : object, dimension = 'COLUMNS') -> bool:
    # Resource object needed by GSheet API
    data_resource = {
      'majorDimension' : dimension,
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

