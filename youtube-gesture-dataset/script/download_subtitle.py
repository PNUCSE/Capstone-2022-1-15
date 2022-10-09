from __future__ import unicode_literals

import glob
import json
import traceback

import youtube_dl
import urllib.request
import sys
import os
from apiclient.discovery import build
from datetime import datetime, timedelta
from config import my_config

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

RESUME_VIDEO_ID = ""  # resume downloading from this video, set empty string to start over


def video_filter(info):
    passed = True

    exist_proper_format = False
    format_data = info.get('formats')
    for i in format_data:
        if i.get('ext') == 'mp4' and i.get('height') >= 720 and i.get('acodec') != 'none':
            exist_proper_format = True

    if not exist_proper_format:
        passed = False

    if passed:
        duration_hours = info.get('duration') / 3600.0
        if duration_hours > 1.0:
            passed = False

    try:
        if passed:
            if len(info.get('automatic_captions')) == 0 and len(info.get('subtitles')) == 0: # len(info.get('automatic_captions')) == 0 and
                passed = False
    except:
        return False

    return passed


def download_subtitle(url, filename, postfix):
    urllib.request.urlretrieve(url, '{}-{}.vtt'.format(filename, postfix))


def get_subtitle_url(subtitles, language, ext):
    subtitles = subtitles.get(language)
    url = None
    for sub in subtitles:
        if sub.get('ext') == ext:
            url = sub.get('url')
            break
    return url

def main():
    if not os.path.exists(my_config.VIDEO_PATH):
        os.makedirs(my_config.VIDEO_PATH)

    language = my_config.LANG

    os.chdir(my_config.VIDEO_PATH)
    vid_list = []

    # read video list
    try:
        rf = open("video_ids.txt", 'r')
    except FileNotFoundError:
        print("fetching video ids...")
        vid_list = fetch_video_ids(my_config.YOUTUBE_CHANNEL_ID, my_config.VIDEO_SEARCH_START_DATE)
        wf = open("video_ids.txt", "w")
        for j in vid_list:
            wf.write(str(j))
            wf.write('\n')
        wf.close()
    else:
        while 1:
            value = rf.readline()[:11]
            if value == '':
                break
            vid_list.append(value)
        rf.close()


    for i in range(len(vid_list)):
        error_count = 0
        with youtube_dl.YoutubeDL() as ydl:
            vid = vid_list[i]
            url = "https://youtu.be/{}".format(vid)
            info = ydl.extract_info(url, download=False)

            if video_filter(info):
                if info.get('automatic_captions') != {}:
                    auto_sub_url = get_subtitle_url(info.get('automatic_captions'), language, 'vtt')
                    download_subtitle(auto_sub_url, vid, language + '-auto')


if __name__ == '__main__':
    # test_fetch()
    main()