import urllib2
import urllib
import json
import sys
import os
import subprocess

#Created by: @Elite_Soba

def main(argv):
	if len(argv) == 0:
		print "Error: Please input a video id"
		print "ex: \"twitchdown.py 55921134\""
		return
	video = argv[0]

	try:
		x = urllib2.urlopen("https://api.twitch.tv/api/videos/v" + video).read()
	except:
		print "Error getting video. Please confirm video ID"
		return
	y = json.loads(x)
	prev = y["preview"]
	index = prev[prev.find("v1/AUTH_system"):prev.find("thumb")]
	header = "http://vod.edgecast.hls.ttvnw.net/"
	footer = "chunked/index-dvr.m3u8" #or "chunked/highlight-" + video + ".m3u8"
	playlist_url = header + index + footer
	
	playlist = ""
	try:
		playlist = urllib2.urlopen(playlist_url)
	except:
		header = "http://vod.ak.hls.ttvnw.net/"
		playlist = urllib2.urlopen(header + index + footer)
	
	list = playlist.read()
	parts = list.split("\n")
	segments = []
	for part in parts:
		if len(part) != 0 and part[0] != "#":
			segments.append(part)

	map = {}

	for segment in segments:
		map[segment[0:segment.find("?")]] = segment[segment.find("end_offset="):]
	#print map

	downloader = urllib.URLopener()
	
	if not os.path.exists(video):
		os.mkdir(video)
	
	print "Downloading to folder: " + video + ". This could take a while."
	progress = 0
	for ts, end in map.items():
		downloader.retrieve(header + index + "chunked/" + ts + "?start_offset=0&" + end, video + "/" + ts)
		progress = progress + 1
		if progress % 10 == 0:
			print "Downloaded " + str(progress) + " parts out of " + str(len(map))
	
	print "Download succeeded. Now merging files"

if __name__ == "__main__":
	main(sys.argv[1:])