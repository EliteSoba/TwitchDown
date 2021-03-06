﻿import urllib2
import json
import sys
import os
from HTMLParser import HTMLParser

#Created by: @Elite_Soba
#Usage: openrec.py VIDEOID
#Usage: openrec.py VIDEOID STARTTIME ENDTIME
#Choosing a STARTTIME < 0 is equivalent to setting STARTTIME to 0
#Choosing an ENDTIME > video length is equivalent to setting ENDTIME to video length
#Choosing STARTTIME < ENDTIME will get you nothing
#Choosing specific times is difficult because it only works in 10 second chunks
#So it may dl an extra 10s or miss 10s.

def hmsToSec(hms):
	#Works for HH:MM:SS and MM:SS
	split = hms.split(":")
	rate = 1
	total = 0
	for part in reversed(split):
		total = total + rate * int(part)
		rate = rate * 60
	return total

def tupleListToDict(list):
	dict = {}
	for tuple in list:
		dict[tuple[0]] = tuple[1]
	return dict

class getDataParser(HTMLParser):
	def handle_starttag(self, tag, attrs):
		if tag == "div":
			attributes = tupleListToDict(attrs)
			if "class" in attributes and attributes["class"] == "js-data__player":
				if "data-file" in attributes:
					self.vidSource = attributes["data-file"]

def cutBandwidth(info):
	if not "BANDWIDTH" in info:
		return 0
	bw = info[info.find("BANDWIDTH=")+10:]
	bw = bw[:bw.find(",")]
	out = 0
	try:
		out = int(bw)
	except:
		print "Error getting bandwidth"
	return out
	
def main(argv):
	video = ""
	if len(argv) == 0:
		video = raw_input("Enter Openrec Video ID: ")
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
		x = urllib2.urlopen("https://www.openrec.tv/movie/" + video).read()
	except:
		print "Error getting video. Please confirm video ID"
		return
	parser = getDataParser()
	parser.feed(x)
	url = "/".join(parser.vidSource.split("/")[:-1]) + "/"
	header = url.replace("https", "http")
	print parser.vidSource.replace("https", "http")
	try:
		x = urllib2.urlopen(parser.vidSource.replace("https", "http")).read()
	except:
		print "Error getting video. Please let me know which video it was"
		return
	qualities = {}
	lines = x.split("\n")
	for i in range(len(lines)-1):
		line = lines[i]
		if line and line[0] == "#":
			if "EXT-X-STREAM-INF" in line:
				bw = cutBandwidth(line)
				playlist = lines[i+1]
				qualities[bw] = playlist
	
	print "Bandwidth options are: " + str(", ".join([str(x) for x in sorted(qualities)]))
	print "Choosing Bandwidth option: " + str(sorted(qualities)[-1])
	footer = qualities[sorted(qualities)[-1]]#"2000kbps.m3u8"
	playlist = ""
	print header + footer
	try:
		playlist = urllib2.urlopen(header + footer)
	except:
		print "Error getting video. Please let me know which video it was"
		return
	
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
	
	filename = video + ".ts"
	i = 1
	while os.path.exists(filename) and os.path.isfile(filename):
		filename = video + "-" + str(i) + ".ts"
		i = i + 1
	vid = open(filename, "wb")
	
	header = "/".join((header + footer).split("/")[:-1]) + "/"
	
	print "Downloading " + str(len(segments)) + " parts. This could take a while."
	progress = 0
	for segment in segments:
		part = urllib2.urlopen(header + segment).read()
		vid.write(part)
		progress = progress + 1
		if progress % 10 == 0:
			print "Downloaded " + str(progress) + " parts out of " + str(len(segments))
	
	print "Download succeeded"
	vid.close()

if __name__ == "__main__":
	main(sys.argv[1:])