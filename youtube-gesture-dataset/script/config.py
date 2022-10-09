# ------------------------------------------------------------------------------
# Copyright (c) ETRI. All rights reserved.
# Licensed under the BSD 3-Clause License.
# This file is part of Youtube-Gesture-Dataset, a sub-project of AIR(AI for Robots) project.
# You can refer to details of AIR project at https://aiforrobots.github.io
# Written by Youngwoo Yoon (youngwoo@etri.re.kr)
# ------------------------------------------------------------------------------

from datetime import datetime


class Config:
    DEVELOPER_KEY = "AIzaSyDU5_CIzz469CtI_YuQbQEmSOrZCsRlQmc"  # your youtube developer id
    OPENPOSE_BASE_DIR = 'C:\\Users\\makem\\ProjectHcb\\work\\openpose'
    OPENPOSE_BIN_PATH = 'C:\\Users\\makem\\ProjectHcb\\work\\openpose\\bin\\OpenPoseDemo.exe'


class YoutubeConfig(Config):
    YOUTUBE_CHANNEL_ID = "UC_pOKLycxyVwNneMVjfMBUA"
    WORK_PATH = 'C:\\Users\\makem\\ProjectHcb\\res\\Youtube_Dataset'
    CLIP_PATH = WORK_PATH + "/clip_ted"
    VIDEO_PATH = WORK_PATH + "/videos_ted"
    SKELETON_PATH = WORK_PATH + "/skeleton_ted"
    SUBTITLE_PATH = VIDEO_PATH
    OUTPUT_PATH = WORK_PATH + "/output"
    VIDEO_SEARCH_START_DATE = datetime(2019, 11, 18, 0, 0, 0)
    LANG = 'ko'
    SUBTITLE_TYPE = 'auto'
    FILTER_OPTION = {"threshold": 100}
    USE_3D_POSE = False


# SET THIS
my_config = YoutubeConfig
