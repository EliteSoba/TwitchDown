@ECHO OFF
set id=%1
IF [%1]==[] (
set /p id=Enter Twitch Video ID: 
)

twitchdown.py %id%

IF EXIST %id% (
cd %id%
copy /b *.ts %id%.ts
mv %id%.ts ../%id%.ts
cd ..
)
