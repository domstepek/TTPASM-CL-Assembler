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
import time, os

class SheetService:
  @property
  def MaxRetries(self) -> int:
    return self.__max_retries

  @MaxRetries.setter
  def MaxRetries(self, value : int) -> None:
    if value < 1:
      raise ValueError("Value cannot be less than 1")
    self.__max_retries = value

  @property
  def TimeoutWait(self) -> float:
    return self.__timeout_wait

  @TimeoutWait.setter
  def TimeoutWait(self, value : float) -> None:
    if value < 0:
      raise ValueError("Value must be greater than 0")
    self.__timeout_wait = value

  def __init__(self, service_account_path):
    self.__scopes = ['https://www.googleapis.com/auth/spreadsheets'] # Read and write permissions
    self.__service_acc_file = service_account_path
    self.__max_retries = 5 # Default: 5 max retries 
    self.__timeout_wait = 2.5 # Default: 2.5 second timeout

  def Login(self) -> None:
    # Create a credentials object with read/write scope, build service object
    creds = service_account.Credentials.from_service_account_file(self.__service_acc_file, scopes=self.__scopes)
    self.__service = build('sheets', 'v4', credentials=creds)

  def GetSheetData(self, spreadsheetID : str, spreadsheet_range : str) -> list:
    while True:
      try:
        response = "errorValue"

        # Attempt to read spreadsheet data
        for retry in range(0, self.MaxRetries):
          if any(errorType in str(response) for errorType in ['errorValue', 'Loading...']):
            response = self.__service.spreadsheets().values().get(spreadsheetId=spreadsheetID,range=spreadsheet_range).execute()
            time.sleep(self.TimeoutWait)
          else: break

        if 'errorValue' in response:
          raise ConnectionError('Could not retrieve data')
        if 'Loading...' in response:
          raise ConnectionAbortedError('Could not retreieve data within the max attempts')
          
        return response.get('values', [])
      except ConnectionResetError:
        print ("Trying to connect to Google Sheets...", end='\r')
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
        print ("Trying to connect to Google Sheets...", end='\r')
        self.Login()
      except Exception:
        return False

  def ClearRange(self, spreadsheetID : str, range : str) -> bool:
    while True:
      try:
        # Send request to clear range
        self.__service.spreadsheets().values().clear(spreadsheetId=spreadsheetID, range=range).execute()
        return True
      except ConnectionResetError:
        print("Trying to connect to Google Sheets...", end='\r')
        self.Login()
      except Exception:
        return False