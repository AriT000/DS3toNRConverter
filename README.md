# DS3toNRConverter
Converts Dark Souls 3 params to Nightreign
# Prerequisites
- Install Python for Windows
- Important: Make sure all the csv param files you want to convert have the name "AtkParam_Npc.csv" or "BehaviorParam.csv" for example. Smithbox should automatically import them in this naming format, but if not, make sure you do this.
# Usage Instructions
*You can convert params individually or all at once. If you have any problems/question, read everything and feel free to reach out.*
1. Click green Code button > Download ZIP. Extract to a folder called "DS3toNRConverter" or something.
2. Make a folder in this folder called "input".
3. Open Command Prompt in the DS3toNRConverter folder.
4. Run `python -m venv .venv` *If this gives any errors, copy and paste the command you just ran + error message into google/chatgpt to fix them*.  
   Folder structure should look like this:  
   <img width="182" height="190" alt="Screenshot 2026-04-13 161242" src="https://github.com/user-attachments/assets/21272e0e-2b52-488e-96d0-8f2896a5d937" />
5. Run `pip install pandas` *Again if errors, look them up and follow instructions*.
6. Drag and drop all your exported DS3 param .csv files in the "input/" folder
   Input folder should look like this:
   <img width="255" height="356" alt="Screenshot 2026-04-13 162755" src="https://github.com/user-attachments/assets/5f955ba8-0a84-4e57-8adf-eca637f35ff2" />
7. Run `./ConvertAll.sh` to convert all param files at once
8. Done! Converted params are in the "output/" folder. Important info ↓

*IMPORTANT: For SpEffectParam, you will probably have to change all "-1" values to 0, or smithbox will crash. (this is probably because some fields are unsigned integers and don't accept negative values)

*If you want to convert a param individually:  
1. Change into the Converters/ folder with `cd Converters` and change into the folder for the param you want to convert with `cd AtkParam_Npc` for example.
2. Now for converting AtkParams for example, run `python DS3toNR_ATKConverter.py --source ../../input/AtkParam_Npc.csv --target AtkTemplate.csv --output ../../output/output.csv`

From here you can import each csv file into your nightreign smithbox param editor.  

---
DM in the ?ServerName? discord `@americanbaldeagle` for any questions.
