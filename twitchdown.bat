@ECHO OFF
set id=%1
IF [%1]==[] (
set /p id=Enter Twitch Video ID: 
)
set start=%2
set end=%3

twitchdown.py %id% %start% %end%

IF EXIST %id% (
cd %id%
copy /b *.ts %id%.ts
mv %id%.ts ../%id%.ts
cd ..
)
