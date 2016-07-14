import urllib2
import json
import sys
import os

#Created by: @Elite_Soba
#Usage: twitchdown.py VIDEOID
#Usage: twitchdown.py VIDEOID STARTTIME ENDTIME
#Choosing a STARTTIME < 0 is equivalent to setting STARTTIME to 0
#Choosing an ENDTIME > video length is equivalent to setting ENDTIME to video length
#Choosing STARTTIME < ENDTIME will get you nothing
#STARTTIME and ENDTIME will be off by approximately 1-2 seconds because of how Twitch works
#This 1-2 second error is true with every Video Downloader, though.

def hmsToSec(hms):
	#Works for HH:MM:SS and MM:SS
	split = hms.split(":")
	rate = 1
	total = 0
	for part in reversed(split):
		total = total + rate * int(part)
		rate = rate * 60
	return total

def main(argv):
	video = ""
	if len(argv) == 0:
		video = raw_input("Enter Twitch Video ID: ")
	else:
		video = argv[0]
	
	start = False
	end = False
	
	if len(argv) == 3:
		start = hmsToSec(argv[1])
		end = hmsToSec(argv[2])
	else:
		response = raw_input("Would you like to download a specific part (Y/N)? ")
		if response.lower()[0] == "y":
			start = raw_input("Enter Start Time (HH:MM:SS): ")
			end = raw_input("Enter End Time (HH:MM:SS): ")
			start = hmsToSec(start)
			end = hmsToSec(end)

	try:
		x = urllib2.urlopen("https://api.twitch.tv/api/videos/v" + video).read()
	except:
		print "Error getting video. Please confirm video ID"
		return
	s3 = False
	y = json.loads(x)
	prev = y["preview"]
	index = prev[prev.find("v1/AUTH_system"):prev.find("thumb")]
	if len(index) < 2:
		#New API system
		index = prev[prev.find("/s3_vods")+9:prev.find("thumb")]
		s3 = True
	
	#Inelegant way to do this, but eh whatever.
	header1 = "http://vod.edgecast.hls.ttvnw.net/"
	header2 = "http://vod.ak.hls.ttvnw.net/"
	footer1 = "chunked/highlight-" + video + ".m3u8"
	footer2 = "chunked/index-dvr.m3u8"
	combinations = [(header1, footer1), (header2, footer1), (header1, footer2), (header2, footer2)]
	header = ""
	footer = ""
	playlist = ""
	success = False
	for combination in combinations:
		header, footer = combination
		playlist_url = header + index + footer
		try:
			playlist = urllib2.urlopen(playlist_url)
			success = True
			break
		except:
			pass
	#print "Playlist was: " + playlist_url
	list = playlist.read()
	parts = list.split("\n")
	segments = []
	time = 0
	for part in parts:
		if "#EXTINF" in part:
			time = time + float(part[8:-1])
		if len(part) != 0 and part[0] != "#":
			if start or end:
				#Get only parts of video between start and end
				if time >= start and time <= end:
					segments.append(part)
			else:
				#Get whole video
				segments.append(part)

	map = {}

	for segment in segments:
		if not s3:
			#They changed how offsets work so I can't group everything together now
			s = segment.split(".")[0].split("-")[1]
			#BECAUSE WHY NOT WHO NEEDS DECENT SUBSTRINGING LET'S JUST SPLIT BY FUN DELIMITERS
			start = segment.split(".")[1].split("&")[0].split("=")[1]
			map[(int(s), int(start))] = segment
			"""
			key = segment[0:segment.find("?")]
			if key in map:
				map[key] = (map[key][0], segment[segment.find("end_offset="):])
			else:
				map[key] = (segment[segment.find("start_offset="):segment.find("end_offset=")], segment[segment.find("end_offset="):])"""
		else:
			#Different format not using offsets
			s = segment.split(".")[0].split("-")
			map[(int(s[1]), int(s[3]))] = segment
	
	filename = video + ".ts"
	i = 1
	while os.path.exists(filename) and os.path.isfile(filename):
		filename = video + "-" + str(i) + ".ts"
		i = i + 1
	vid = open(filename, "wb")
	
	print "Downloading " + str(len(map)) + " parts. This could take a while."
	#print "URL is: " + header + index
	progress = 0
	for ts in sorted(map):
		time = map[ts]
		if s3:
			part = urllib2.urlopen(header + index + "chunked/" + time).read()
			vid.write(part)
		else:
			try:
				#print header + index + "chunked/" + ts + "?" + time[0] + time[1]
				#part = urllib2.urlopen(header + index + "chunked/" + ts + "?" + time[0] + time[1]).read()
				part = urllib2.urlopen(header + index + "chunked/" + time).read()
				vid.write(part)
			except:
				#If the part is muted instead
				#part = urllib2.urlopen(header + index + "chunked/" + ts[:ts.find(".ts")] + "-muted.ts?" + time[0] + time[1]).read()
				time.replace(".ts", "-muted.ts")
				part = urllib2.urlopen(header + index + "chunked/" + time).read()
				vid.write(part)
		progress = progress + 1
		if progress % 10 == 0:
			print "Downloaded " + str(progress) + " parts out of " + str(len(map))
	
	print "Download succeeded"
	vid.close()

if __name__ == "__main__":
	main(sys.argv[1:])