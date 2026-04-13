# DS3toNRConverter
Converts Dark Souls 3 params to Nightreign
# Prerequisites
- Install Python for Windows
- Important: Make sure all the csv param files you want to convert have the name "AtkParam_Npc.csv" or "BehaviorParam.csv" for example. Smithbox should automatically import them in this naming format, but if not, make sure you do this.
# Usage Instructions
1. Click green Code button > Download ZIP. Extract to a folder called "DS3toNRConverter" or something.
2. Make a folder in this folder called "input".
3. Open Command Prompt in the DS3toNRConverter folder.
4. Run `python -m venv .venv` *If this gives any errors, copy and paste the command you just ran + error message into google/chatgpt to fix them*.  
   Folder structure should look like this:  
   <img width="182" height="190" alt="Screenshot 2026-04-13 161242" src="https://github.com/user-attachments/assets/21272e0e-2b52-488e-96d0-8f2896a5d937" />
6. Run `pip install pandas` *Again if errors, look them up and follow instructions*.
7. Drag and drop all your exported DS3 param .csv files in the "input/" folder
8. Run `chmod +x ConvertAll.sh`
9. Run `./ConvertAll.sh` to convert all param files at once

*To run each one individually
1. Change into the Converters/ folder with `cd Converters` and change into the folder for the param you want to convert with `cd AtkParam_Npc` for example.
2. Now for converting AtkParams for example, run `python DS3toNR_ATKConverter.py AtkParam_Npc_midir.csv output.csv --template AtkTemplate.csv`

From here you can import each csv file into your nightreign smithbox param editor.  

---
DM in the ?ServerName? discord `@americanbaldeagle` for any questions.
