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
	header1 = "http://vod.edgecast.hls.ttvnw.net/"
	header2 = "http://vod.ak.hls.ttvnw.net/"
	footer1 = "chunked/highlight-" + video + ".m3u8"
	footer2 = "chunked/index-dvr.m3u8"
	combinations = [(header1, footer1), (header2, footer1), (header1, footer2), (header2, footer2)]
	header = ""
	footer = ""
	playlist = ""
	for combination in combinations:
		header, footer = combination
		playlist_url = header + index + footer
		try:
			playlist = urllib2.urlopen(playlist_url)
			break
		except:
			pass
	
	list = playlist.read()
	parts = list.split("\n")
	segments = []
	time = 0
	for part in parts:
		if "#EXTINF" in part:
			time = time + float(part[8:-1])
		if len(part) != 0 and part[0] != "#":
			segments.append(part)

	map = {}

	for segment in segments:
		key = segment[0:segment.find("?")]
		if key in map:
			map[key] = (map[key][0], segment[segment.find("end_offset="):])
		else:
			map[key] = (segment[segment.find("start_offset="):segment.find("end_offset=")], segment[segment.find("end_offset="):])
	
	for i in sorted(map):
		print i, map[i]

	return
	downloader = urllib.URLopener()
	
	if not os.path.exists(video):
		os.mkdir(video)
	
	print "Downloading " + str(len(map)) + " parts to folder: " + video + ". This could take a while."
	progress = 0
	for ts, time in map.items():
		downloader.retrieve(header + index + "chunked/" + ts + "?" + time[0] + time[1], video + "/" + ts)
		progress = progress + 1
		if progress % 10 == 0:
			print "Downloaded " + str(progress) + " parts out of " + str(len(map))
	
	print "Download succeeded. Now merging files"

if __name__ == "__main__":
	main(sys.argv[1:])