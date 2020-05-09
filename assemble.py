"""
Name: assemble.py
Description:
When called with proper arguments, this script will take the TTPASM code located
at the first argument and create two, CSV and TSV, output files as well as upload
the output TSV file to the trace analyzer Google spreadsheet.
Coded by: Dom Stepek
"""

import subprocess, sys, os, gsheets, re, datetime as dt
from typing import *

SETTINGS_FILE = '/assets/settings.txt'
SERVICE_ACCOUNT_FILE = '/assets/service-account.json'
SOURCE_RANGE = 'source!A:A'
RAMFILE_RANGE = 'RAM file!A:A'
TRACE_RANGE = 'Sheet1!A:M'

def Setup():
  current_directory = os.path.dirname(os.path.realpath(__file__))
  # Retrieves settings from settings file
  pattern = r'.+?=\"(.+)\"'
  with open(current_directory + SETTINGS_FILE, mode='r+') as settings_file:
    logisim_path, processor_path, assembler_id, trace_id = re.findall(pattern, settings_file.read())

  # Login to Google Sheets API
  sheets = gsheets.SheetService(current_directory + SERVICE_ACCOUNT_FILE)
  sheets.Login()

  return {
    'logisim_path' : logisim_path,
    'processor_path' : processor_path,
    'spreadsheet_id' : assembler_id,
    'trace_id' : trace_id,
    'sheets_service' : sheets
  }

def UploadCode(sheet_service : gsheets.SheetService, spreadsheet_id : str) -> None:
  # Convert TTPASM code into object valid for use with GSheet API
  with open(sys.argv[1], mode='r+') as ttpasm_file:
    code = [ttpasm_file.readlines()]
  
  sheet_service.ClearRange(spreadsheet_id, SOURCE_RANGE)
  sheet_service.WriteSheetData(spreadsheet_id, SOURCE_RANGE, code) # Writes new TTPASM code to sheet

def DownloadRAMFile(sheet_service : gsheets.SheetService, spreadsheet_id : str) -> list:
  return sheet_service.GetSheetData(spreadsheet_id, RAMFILE_RANGE) # Gets RAM file

def CreateOutputFiles(ram_file : list, logisim_path : str, processor_path : str) -> Tuple[list, list]:
  csv_data = [] # This object does not technically serve any purpose at the moment other than for the user convienence
  tsv_data = []

  # Create the CSV file from the RAM file
  with open(f'{sys.argv[2]}.csv', mode='w+') as csv_file:
    for line in ram_file:
      csv_file.write(line[0] + '\n\r')
      csv_data.append(line[0])

  # Run java to load the CSV file and output to a TSV file
  with open(f'{sys.argv[2]}.tsv', mode='w+') as output_file:
    subprocess.run(['java', '-jar', logisim_path, processor_path, '-tty', 'table', '-load', f'{sys.argv[2]}.csv'], stdout=output_file)

  # Get TSV data from the file
  # Had to separate the TSV file access from the subprocess.run() call
  # because it would be run concurrently, which is not desireable.
  with open(f'{sys.argv[2]}.tsv', mode='r+') as output_file:
    tsv_data = output_file.readlines()
    
  tsv_data = [line[:-1].split('\t') for line in tsv_data] # Remove '\n' at end of each line and split by tab escape sequences

  return {
    'csv_data' : csv_data,
    'tsv_data' : tsv_data
  }

def StartTraceAnalyzer(sheet_service : gsheets.SheetService, trace_id : str, trace : List[str]) -> None:
  sheet_service.ClearRange(trace_id, TRACE_RANGE)
  sheet_service.WriteSheetData(trace_id, TRACE_RANGE, trace, 'ROWS')

def TimeAndPerform(start_msg : str, func : Callable[[list], Any], *args) -> Tuple[Any, float]:
  print(start_msg.ljust(50), end='\r')

  start = dt.datetime.now()
  ret_data = func(*args)
  
  return (ret_data, (dt.datetime.now() - start).total_seconds())

def main():
  # Check for valid arg length
  if len(sys.argv) != 3:
    print ('proper usage: python assemble.py <path to assembly file> <path to output file without extension>')
    exit(1)

  setup_data, setup_time = TimeAndPerform("Setting up script...", Setup)
  _, upload_time = TimeAndPerform("Uploading TTPASM file to Google Sheets...", UploadCode, setup_data['sheets_service'], setup_data['spreadsheet_id'])
  ram_file, download_time = TimeAndPerform("Getting RAM file from Google Sheets...", DownloadRAMFile, setup_data['sheets_service'], setup_data['spreadsheet_id'])
  file_data, create_files_time = TimeAndPerform("Creating CSV and TSV files...", CreateOutputFiles, ram_file, setup_data['logisim_path'], setup_data['processor_path'])
  _, trace_analyzer_time = TimeAndPerform('Uploading Trace Data...', StartTraceAnalyzer, setup_data['sheets_service'], setup_data['trace_id'], file_data['tsv_data'])

  print(f"""Succesfully wrote output to '{sys.argv[2]}.csv' and '{sys.argv[2]}.tsv'
  Setup took {setup_time} seconds
  Uploading code took {upload_time} seconds
  Downloading RAM file took {download_time} seconds
  Creating output files took {create_files_time} seconds
  Uploading trace data took {trace_analyzer_time} seconds
  View trace analysis here:
    https://docs.google.com/spreadsheets/d/{setup_data['trace_id']}/edit""")

if __name__ == '__main__':
  main()