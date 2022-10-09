import glob
import json
import os
import pickle
import subprocess

import shutil

from config import my_config

def get_frame_info_from_json(json_file_path):
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)

    total_valid_frame = 0
    total_frame = 0
    for j in json_data:
        s_frame = j['clip_info'][0]
        e_frame = j['clip_info'][1]
        if j['clip_info'][2] == True:
            total_valid_frame += e_frame - s_frame
        total_frame += e_frame - s_frame

    return total_frame, total_valid_frame


video_files = glob.glob(my_config.VIDEO_PATH + "/*.mp4")
clip_files = glob.glob(my_config.CLIP_PATH + "/*_aux_info.json")
sorted_video_files = sorted(video_files, key=os.path.getmtime)
sliced_video_files = sorted_video_files[328:]
print('비디오 갯수 ',len(video_files))
print('클립 갯수', len(clip_files))

all_files_total_frame = 0
all_files_total_valid_frame = 0

for file in sorted_video_files:
    vid = os.path.split(file)[1][-15:-4]
    json_file_path = my_config.CLIP_PATH + '/' + vid + '_aux_info.json'
    total_frame, total_valid_frame = get_frame_info_from_json(json_file_path)

    all_files_total_frame += total_frame
    all_files_total_valid_frame += total_valid_frame

    print(vid, '의 프레임 정보')
    print('total_frame: ', total_frame)
    print('total_valid_frame: ', total_valid_frame)
    print()

print('전체 영상 프레임 수: ', all_files_total_frame)
print('전체 영상 유효한 프레임 수: ', all_files_total_valid_frame)
print('전체 영상 시간: ', all_files_total_frame * 0.033 / 3600)
print('전체 영상 유효한 시간: ', all_files_total_valid_frame * 0.033 / 3600)



