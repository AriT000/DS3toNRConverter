# DS3toNRConverter
Converts Dark Souls 3 params to Nightreign

1. Download all the folders (AtkParam, BeaviorParam, etc.) and save them to a folder called "DS3toNRConverter" or something.
2. Open Command Prompt in this folder.
3. Run `python -m venv .venv` *If this gives any errors, copy and paste the command you just ran + error message into google/chatgpt to fix them*.
4. Run `pip install pandas` *again if errors ^*.
5. Change into the folder for the param you want to convert with `cd AtkParam_Npc` for example.
6. Now for converting AtkParams for example, run `python DS3toNR_ATKConverter.py AtkParam_Npc_midir.csv output.csv --template ATKTemplate.csv`

*To run all of them at once, run AllParams.sh
