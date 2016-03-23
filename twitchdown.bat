@ECHO OFF
IF [%1]==[] (
ECHO Invalid Command Line Arugment
ECHO Example: twitchdown.bat 55921134
GOTO :end
)

twitchdown.py %1

IF EXIST %1 (
cd %1
copy /b *.ts %1.ts
mv %1.ts ../%1.ts
cd ..
)
:end