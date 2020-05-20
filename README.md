# TTPASM Assembler Wrapper

This project was designed to automate the process of taking a TTPASM file for Tak's Toy Processor and uploading data to the trace analyzer to speed up the debugging process. It works by uploading the TTPASM file to the Google Sheet assembler, retrieves the RAM file, sends the RAM file through the processor with the java command, outputs to a TSV file, and finally sends the TSV file to the trace analyzer.

## Requirements
* Must have Python 3.6+ installed
* Must have Google Sheets Python API Installed. This can be done with pip:
```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
* Must share the assembler and trace analyzer spreadsheets with read/write permissions to the service account
  **head-601@ttpassembler.iam.gserviceaccount.com**
* Must put correct info in settings.txt file

## How To Use
1. Download project (Clone or Download -> Download ZIP)
2. Run the following shell command (remember this project requires python3.6+)
```
python assemble.py <path to ttpasm file> <path to output without any extensions>
```

**Example Usage**

![example](https://github.com/domstepek/TTPASM-CL-Assembler/blob/master/assets/example.png?raw=true)

## Notes
- Please let me know if there are any errors that I can fix
- Please let me know if there are any features I can implement
- In the settings file, simply use exact path without any escape characters or sequences.
- In the settings file, the spreadsheet ID can be extracted from a link as such. The spreadsheet ID for the link `https://docs.google.com/spreadsheets/d/abcdefg123456789/edit` would be **abcdefg123456789**
- Use absolute paths everywhere!

## Common Errors and Problems
- If you get a 'invalid syntax' error, this is more than likely a result of you using the wrong Python version. The default `python` command refers to version 2.7. To use the right version, either install a virtual env version of Python3.6+ or use `python3` and `pip3` instead of `python` and `pip`.
- If you receive a message asking to locate `alu.circ` and `regbank.circ`, do not do it through this script. Open up the GUI logisim, open up `processor0003.circ`, locate both the circ files, then save your `processor0003.circ` file.


## TODO
- Retrieve the output of trace analyzer, perhaps?
