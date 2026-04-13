# DS3toNRConverter
Converts Dark Souls 3 params to Nightreign
# Prerequisites
- Install Python for Windows
# Usage Instructions
1. Click green Code button > Download ZIP. Extract to a folder called "DS3toNRConverter" or something.
2. Open Command Prompt in this folder.
3. Run `python -m venv .venv` *If this gives any errors, copy and paste the command you just ran + error message into google/chatgpt to fix them*.
4. Run `pip install pandas` *again if errors ^*.
5. Drag and drop all your exported DS3 param .csv files in the "input/" folder
6. Run `chmod +x ConvertAll.sh`
7. Run `./ConvertAll.sh` to convert all param files at once

*To run each one individually
1. Change into the Converters/ folder with `cd Converters` and change into the folder for the param you want to convert with `cd AtkParam_Npc` for example.
2. Now for converting AtkParams for example, run `python DS3toNR_ATKConverter.py AtkParam_Npc_midir.csv output.csv --template AtkTemplate.csv`

From here you can import each csv file into your nightreign smithbox param editor.
