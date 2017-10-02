# Converter
Convert YouTube videos into .mp4 and .mp3

Roungseo (Peter) Youn

The script begins with a given YouTube video url, downloads the video, rips the audio from the video, then crawls to a new video for given number of times.

The script ensures non-duplicates by calculating similarity in the titles via Jaccard coefficient.

Users can filter out videos from unwanted uploaders by adding the channel name to blacklist.txt

Need to delete .gitkeep from the three ("dl/", "video/", "audio/") directories to run the script.

The script is optimized for videos that are not too old and require 720p resolution available on YouTube. If such is not possible, simply change the limits within converter.py
