# TTPASM Assembler Wrapper

This project was designed to create an output TSV file from a TTPASM file. It works by uploading the TTPASM file to the Google Sheet assembler, retrieving the RAM file, sends the RAM file through the processor with the java command, and finally outputs to a TSV file.

## Requirements
* Must have Python 3.6+ installed
* Must have Google Sheets Python API Installed. This can be done with pip:
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
* Must share the assembler spreadsheet with full permissions to the service account
**head-601@ttpassembler.iam.gserviceaccount.com**
* Must put correct info in settings.txt file

## How to use
1. Simply download this project to your machine
2. Run the following shell command (remember this project requires python3.6+)
```
python python assemble.py <path to ttpasm file> <path to output without any extensions>
```
3. Check output directory for both the CSV and TSV files

## Example usage
This is an example of how I use the script to clarify usage.
![example](https://github.com/domstepek/TTPASM-CL-Assembler/blob/master/example.png?raw=true)

## Notes
- Please let me know if there are any errors that I can fix
- Please let me know if there are any features I can implement
- In the settings file, simply use exact path without any escape characters or sequences.
- In the settings file, the spreadsheet ID can be extracted from a link as such. The spreadsheet ID for the link `https://docs.google.com/spreadsheets/d/abcdefg123456789/edit` would be **abcdefg123456789**
