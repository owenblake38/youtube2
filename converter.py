#!/usr/bin/python

from pytube import YouTube
import re
import logging
import sys, os, subprocess
import urllib.request as ur
import lxml.html
import random
import pafy

# default quality and extension - may weed out wanted choices
quality = "720p"
extension = "mp4"
# turn off warnings
logging.getLogger().setLevel(logging.ERROR)
# create dict of int id: str "actual name" pairs
names_dict = {}

def main():
	# number of crawls
	n = int(sys.argv[1])
	# starting url, 20char
	base = "http://www.youtube.com"
	tail = "/watch?v=_AADHVsit4A"

	
	dl_video("https://www.youtube.com/watch?v=Amq-qlqbjYA", n)
	del_duplicates()
	create_audio()
	separate_vid_aud()

	print("\n\nDownloaded:")
	os.chdir("audio/")
	files = os.listdir(os.curdir)
	mp3_files = [file for file in files if not file.endswith(".mp4")]
	for file in mp3_files:
		print(file)
	os.chdir("../")
	return 1

def dl_video(link, n):
	for i in range(n):
		# check "video" is not a live stream
		# if live stream, skip
		check_video = pafy.new(link)
		if check_video.length == 0:
			continue
		# check blacklisted uploaders
		# to filter spam, unwanted content
		if check_video.author in open("blacklist.txt").read():
			continue
		# create YT object
		yt = YouTube(link)
		# take out non-alpha characters, give title
		video_title = yt.filename
		title_list = re.split("[^a-zA-Z]", video_title)
		title = filter(None, title_list)
		# set video name as title
		yt.set_filename(" ".join(str(x) for x in title))
		# grab video
		video = yt.get(extension, quality)
		# print to reconfirm/debug
		print(yt.filename)
		# if video not already downloaded
		# then write video name in names.txt
		# and download the video into video/ directory
		if yt.filename not in open("names.txt").read():
			with open("names.txt", "a") as file:
				file.write("\n" + yt.filename)
			video.download("dl/")
		# grab href urls from current site
		links = ur.urlopen(link)
		readlinks = links.read()
		dom = lxml.html.fromstring(readlinks)
		# make a set of href urls
		lst = set()
		for link in dom.xpath("//a/@href"):
			if link.startswith("/watch?v=") and len(link) == 20:
				lst.add(link)
		# choose a random url and begin next iteration on random url
		lst = list(lst)
		tail = random.choice(lst)
		link = "https://www.youtube.com" + tail
		print(link)

	return

def del_duplicates():
	# read in lines of video names
	with open("names.txt") as f:
		lines = f.read().splitlines()
	lst = []
	for line in lines:
		lst.append(line.split(" "))
	# go through all possible combinations of video names
	# and filter based on Jaccard coefficient
	# current implementation takes O(n^2), can be more efficient
	for title1 in lst:
		for title2 in lst:
			if title1 != title2 and Jaccard(title1, title2) > 0.6:
				video_name = " ".join(title2)
				os.remove("dl/"+video_name)
				with open("names.txt", "r+") as f:
					t = f.read()
					f.seek(0)
					for line in t.split("\n"):
						if line != video_name:
							f.write(line + "\n")
					f.truncate()

	return


def Jaccard(lst1, lst2):
	A = set(a.lower() for a in lst1)
	B = set(b.lower() for b in lst2)

	inter = A.intersection(B)
	union = A.union(B)

	Jaccard = len(inter)/float(len(union))

	return Jaccard

def create_audio():
	# go into download directory
	os.chdir("dl/")
	# rename long video names
	rename()

	# access all video files
	files = os.listdir(os.curdir)
	# convert mp4 to mp3 for every mp4 file using ffmpeg
	for file in files:
		#os.rename(file, file.replace(" ", ""))
		command = "ffmpeg -i " + file + " -ab 160k -ac 2 -ar 44100 -vn " + file[:-3] + "mp3"
		subprocess.call(command, shell=True)

	# restore all original names to mp4 and mp3 files
	restore_name()
	# go back to parent directory
	os.chdir("../")
	return

def rename():
	files = os.listdir(os.curdir)
	# key to be used in global dictionary for original names
	names_id = 0
	for file in files:
		names_dict[names_id] = file
		os.rename(file, str(names_id)+".mp4")
		names_id += 1
	return

def restore_name():
	# restore names to mp3 files
	files = os.listdir(os.curdir)
	mp3_files = [file for file in files if not file.endswith(".mp4")]
	for file in mp3_files:
		os.rename(file, names_dict[int(file[:-4])][:-3] + "mp3")

	# restore names to mp4 files
	mp4_files = [file for file in files if not file.endswith(".mp3")]
	for file in mp4_files:
		os.rename(file, names_dict[int(file[:-4])])

	return

def separate_vid_aud():
	# current directory in /converter/ 
	# the parent directory

	# set directory vars
	parent_dir = os.getcwd()
	os.chdir("dl/")
	dl_dir = os.getcwd()
	os.chdir("../video/")
	vid_dir = os.getcwd()
	os.chdir("../audio/")
	aud_dir = os.getcwd()
	# move back to parent directory
	os.chdir("../")
	# grab files from dl directory
	# separate by mp3 or mp4
	files = os.listdir(dl_dir)
	mp4_files = [file for file in files if not file.endswith(".mp3")]
	mp3_files = [file for file in files if not file.endswith(".mp4")]
	# move mp4 into vid and mp3 into audio
	for file in mp4_files:
		os.rename(dl_dir+"/"+file, vid_dir+"/"+file)
	for file in mp3_files:
		os.rename(dl_dir+"/"+file, aud_dir+"/"+file)

	return

if __name__ == '__main__':
	main()