@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

set "CONVERTERS=%ROOT%\Converters"
set "INPUT=%ROOT%\input"
set "OUTPUT=%ROOT%\output"

if not exist "%OUTPUT%" mkdir "%OUTPUT%"

call :run_atk "AtkParam_Npc" "DS3toNR_ATKConverter.py" "AtkParam_Npc.csv" "AtkTemplate.csv"

call :run_std "BehaviorParam"    "DS3toNR_BehaviorConvert.py"    "BehaviorParam.csv"    "BehaviorTemplate.csv"
call :run_std "Bullet"           "DS3toNR_BulletConvert.py"      "Bullet.csv"           "BulletTemplate.csv"
call :run_std "LockCamParam"     "DS3toNR_LockCamConvert.py"     "LockCamParam.csv"     "LockCamTemplate.csv"
call :run_std "NpcParam"         "DS3toNR_NpcConvert.py"         "NpcParam.csv"         "NpcTemplate.csv"
call :run_std "NpcThinkParam"    "DS3toNR_NpcThinkConvert.py"    "NpcThinkParam.csv"    "NpcThinkTemplate.csv"
call :run_std "SpEffectParam"    "DS3toNR_SpEffectConvert.py"    "SpEffectParam.csv"    "SpEffectTemplate.csv"
call :run_std "SpEffectVfxParam" "DS3toNR_SpEffectVfxConvert.py" "SpEffectVfxParam.csv" "SpEffectVfxTemplate.csv"
call :run_std "ThrowParam"       "DS3toNR_ThrowConvert.py"       "ThrowParam.csv"       "ThrowTemplate.csv"

echo Done. Output files are in "%OUTPUT%"
pause
exit /b 0

:run_atk
set "FOLDER=%~1"
set "SCRIPT=%CONVERTERS%\%~1\%~2"
set "INFILE=%INPUT%\%~3"
set "OUTFILE=%OUTPUT%\%~3"
set "TEMPLATE=%CONVERTERS%\%~1\%~4"

if not exist "%SCRIPT%" (
    echo [skip] %~1
    goto :eof
)
if not exist "%INFILE%" (
    echo [skip] %~1
    goto :eof
)
if not exist "%TEMPLATE%" (
    echo [skip] %~1
    goto :eof
)

echo [run] %~1
python "%SCRIPT%" "%INFILE%" "%OUTFILE%" --template "%TEMPLATE%"
if errorlevel 1 (
    echo [fail] %~1
    exit /b 1
)
goto :eof

:run_std
set "FOLDER=%~1"
set "SCRIPT=%CONVERTERS%\%~1\%~2"
set "INFILE=%INPUT%\%~3"
set "OUTFILE=%OUTPUT%\%~3"
set "TEMPLATE=%CONVERTERS%\%~1\%~4"

if not exist "%SCRIPT%" (
    echo [skip] %~1
    goto :eof
)
if not exist "%INFILE%" (
    echo [skip] %~1
    goto :eof
)
if not exist "%TEMPLATE%" (
    echo [skip] %~1
    goto :eof
)

echo [run] %~1
python "%SCRIPT%" --source "%INFILE%" --target "%TEMPLATE%" --output "%OUTFILE%"
if errorlevel 1 (
    echo [fail] %~1
    exit /b 1
)
goto :eof