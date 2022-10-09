import glob
import matplotlib
import cv2
import re
import json
import os
import _pickle as pickle
from webvtt import WebVTT
from config import my_config
from tqdm import tqdm_gui

try:
    i = 0
    wrong_vtt_list = []
    video_files = sorted(glob.glob(my_config.VIDEO_PATH + "/*.mp4"), key=os.path.getmtime)
    lang = my_config.LANG
    postfix_in_filename = '-' + lang + '-auto.vtt'

    for v_i, video_file in enumerate(tqdm_gui(video_files)):
        vid = os.path.split(video_file)[1][-15:-4]
        print(vid)

        file_list = glob.glob(my_config.SUBTITLE_PATH + '/*' + vid + postfix_in_filename)
        print(file_list[0])
        try:
            WebVTT().read(file_list[0])
        except Exception as e:
            print(e)
            i += 1
            wrong_vtt_list.append(vid)
            print("넘어가자!")
            continue

    print(i)
    print(wrong_vtt_list)
except Exception as e:
    print(e)
