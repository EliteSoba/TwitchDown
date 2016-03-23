# TwitchDown
Download Past Broadcasts/Highlights from Twitch

For any questions/comments/concerns, please message [@Elite_Soba](http://twitter.com/Elite_Soba)

Usage:

twitchdown.bat
- Interactive Mode. Will prompt for video ID, and if you want a custom start/end time. See next point for details on start/end times

twitchdown.bat VIDEOID
- Will ask if you want to set a custom start/end time. Respond with Y/N for Yes/No respectively. If yes, it will prompt for the start and end times in HH:MM:SS format. MM:SS format will work as well

twitchdown.bat VIDEOID STARTTIME ENDTIME
- All arguments have been provided and it will automatically begin the download

Creates a folder named VIDEOID to store the temporary video files before merging them. It doesn't delete this folder after merging, so it's up to you to do that.
