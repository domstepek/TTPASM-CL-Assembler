import subprocess, sys, gsheets, re, datetime as dt

SETTINGS_FILE = 'settings.txt'

if len(sys.argv) != 3:
  print ('assemble.py <path to assembly file> <path to output file without extension>')
  exit(1)

print("Setting up script...".ljust(50), end='\r')
start = dt.datetime.now()

pattern = r'.+?=\"(.+)\"'
with open(SETTINGS_FILE, mode='r+') as settings_file:
  logisim_path = re.search(pattern, settings_file.readline()).group(1)
  processor_path = re.search(pattern, settings_file.readline()).group(1)
  spreadsheet_id = re.search(pattern, settings_file.readline()).group(1)

with open(sys.argv[1], mode='r+') as ttpasm_file:
  code = [ttpasm_file.readlines()]

sheets = gsheets.SheetService()
sheets.Login()

print("Writing TTPASM file to Google Sheets...".ljust(50), end='\r')
sheets.WriteSheetData(spreadsheet_id, 'source!A:A', code)
print("Getting RAM file from Google Sheets...".ljust(50), end='\r')
data = sheets.GetSheetData(spreadsheet_id, 'RAM file!A:A', True)

print("Creating CSV and TSV files...".ljust(50), end='\r')
with open(f'{sys.argv[2]}.csv', mode='w+') as csv_file:
  for line in data:
    csv_file.write(line[0] + '\n\r')

with open(f'{sys.argv[2]}.tsv', mode='w+') as output_file:
  subprocess.run(['java', '-jar', logisim_path, processor_path, '-tty', 'table', '-load', f'{sys.argv[2]}.csv'], stdout=output_file)

stop = dt.datetime.now()
print(f"Succesfully wrote output to {sys.argv[2]}.tsv in {(stop - start).total_seconds()} seconds")




