import Estimate3d
import pickle
import warnings
import json

import collections
import os

import lmdb
import pyarrow
import numpy as np
from tqdm import tqdm_gui
import unicodedata
import joblib
from config import my_config
from data_utils import *

warnings.filterwarnings("ignore")


def read_subtitle(vid):
    postfix_in_filename = '-en.vtt'
    file_list = glob.glob(my_config.SUBTITLE_PATH + '/*' + vid + postfix_in_filename)
    if len(file_list) > 1:
        print('more than one subtitle. check this.', file_list)
        assert False
    if len(file_list) == 1:
        return WebVTT().read(file_list[0])
    else:
        return []


# lowercase, trim, and remove non-letter characters
def normalize_string(s, lang='en'):
    s = re.sub(r"([,.!?])", r" \1 ", s)  # isolate some marks
    s = re.sub(r"(['])", r"", s)  # remove apostrophe (i.e., shouldn't --> shouldnt)
    s = re.sub(r"[^가-힣0-9,.!?]+", r" ", s)  # replace other characters with whitespace
    s = re.sub(r"\s+", r" ", s).strip()
    return s


def normalize_subtitle(vtt_subtitle):
    for i, sub in enumerate(vtt_subtitle):
        vtt_subtitle[i].text = normalize_string(vtt_subtitle[i].text)
    return vtt_subtitle


def normalize_skeleton(data, resize_factor=None):
    def distance(x1, y1, x2, y2):
        return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    if data[1 * 2] == 0 or data[2 * 2] == 0 or data[5 * 2] == 0:  # neck or shoulder joints are missing
        return [np.nan] * len(data), resize_factor

    anchor_pt = (data[1 * 2], data[1 * 2 + 1])  # neck
    if resize_factor is None:
        neck_height = float(abs(data[1] - data[1 * 2 + 1]))
        shoulder_length = distance(data[1 * 2], data[1 * 2 + 1], data[2 * 2], data[2 * 2 + 1]) + \
                          distance(data[1 * 2], data[1 * 2 + 1], data[5 * 2], data[5 * 2 + 1])
        resized_neck_height = neck_height / float(shoulder_length)
        if resized_neck_height > 0.6:
            resize_factor = shoulder_length * resized_neck_height / 0.6
        else:
            resize_factor = shoulder_length

    normalized_data = data.copy()
    for i in range(0, len(data), 2):
        if data[i] > 0:
            normalized_data[i] = (data[i] - anchor_pt[0]) / resize_factor
        else:
            normalized_data[i] = np.nan
        if data[i + 1] > 0:
            normalized_data[i + 1] = (data[i + 1] - anchor_pt[1]) / resize_factor
        else:
            normalized_data[i + 1] = np.nan

    return normalized_data, resize_factor


def normalize_skeleton_3d(data, resize_factor=None):

    def distance(x1, y1, z1, x2, y2, z2):
        return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 +(z1 - z2) ** 2)

    if data[1][2] == 0 or data[2][2] == 0 or data[5][2] == 0:  # neck or shoulder joints are missing
        return [[np.nan] * 3] * len(data), resize_factor

    anchor_pt = (data[1][0], data[1][1], data[1][2])  # neck
    if resize_factor is None:
        neck_height = float(abs(data[0][1] - data[1][1]))
        shoulder_length = distance(data[1][0], data[1][1], data[1][2], data[2][0], data[2][1], data[2][2]) + \
                          distance(data[1][0], data[1][1], data[1][2], data[5][0], data[5][1], data[5][2])
        resized_neck_height = neck_height / float(shoulder_length)
        if resized_neck_height > 0.6:
            resize_factor = shoulder_length * resized_neck_height / 0.6
        else:
            resize_factor = shoulder_length

    normalized_data = data.copy()
    for i in range(0, len(data)):
        if data[i][0] >= 0:
            normalized_data[i][0] = (data[i][0] - anchor_pt[0]) / resize_factor
        else:
            normalized_data[i][0] = np.nan
        if data[i][1] >= 0:
            normalized_data[i][1] = (data[i][1] - anchor_pt[1]) / resize_factor
        else:
            normalized_data[i][1] = np.nan
        if data[i][2] >= 0:
            normalized_data[i][2] = (data[i][2] - anchor_pt[2]) / resize_factor
        else:
            normalized_data[i][2] = np.nan

    return normalized_data


def make_lmdb_gesture_dataset():
    model_json = '3D_model/multistage_best/model_multistage_dropout.json'
    model_weight = '3D_model/multistage_best/model_multistage_weight_dropout.h5'
    estimate3d = Estimate3d.Inference(model_json, model_weight)

    if not os.path.exists(my_config.OUTPUT_PATH):
        os.makedirs(my_config.OUTPUT_PATH)

    map_size = 1024 * 20  # in MB
    map_size <<= 20  # in B
    db = [lmdb.open(os.path.join(my_config.OUTPUT_PATH, 'lmdb_train'), map_size=map_size),
            lmdb.open(os.path.join(my_config.OUTPUT_PATH, 'lmdb_val'), map_size=map_size),
            lmdb.open(os.path.join(my_config.OUTPUT_PATH, 'lmdb_test'), map_size=map_size)]
    n_saved_clips = [0, 0, 0]

    #delete previous items
    for i in range(3):
        with db[i].begin(write=True) as txn:
            txn.drop(db[i].open_db())

    video_files = sorted(glob.glob(my_config.VIDEO_PATH + "/*.mp4"), key=os.path.getmtime)

    total_num = 0
    total_3d_value = [0] * 30

    for v_i, video_file in enumerate(tqdm_gui(video_files)):

        vid = os.path.split(video_file)[1][-15:-4]
        print(vid)
        # load clip, video, and subtitle
        clip_data = load_clip_data(vid)
        if clip_data is None:
            print('[WARNING] clip data file does not exist! skip this video.')
            clip_data = []

        video_wrapper = read_video(my_config.VIDEO_PATH, vid)

        subtitle_type = my_config.SUBTITLE_TYPE
        subtitle = SubtitleWrapper(vid, subtitle_type).get()
        if subtitle is None:
            print('[WARNING] subtitle does not exist! skip this video.')
            clip_data = []

        # process
        clips = [{'vid': vid, 'framerate': video_wrapper.framerate, 'clips': []},  # train
                 {'vid': vid, 'framerate': video_wrapper.framerate, 'clips': []},  # val
                 {'vid': vid, 'framerate': video_wrapper.framerate, 'clips': []}]  # test

        word_index = 0
        valid_clip_count = 0
        for clip_idx, clip in enumerate(clip_data):
            start_frame_no, end_frame_no, clip_pose_all = clip['clip_info'][0], clip['clip_info'][1], clip['frames']
            clip_word_list = []

            # skip FALSE clips
            if not clip['clip_info'][2]:
                continue

            # train/val/test split
            if v_i % 10 == 0:
                dataset_idx = 2  # test
            elif v_i % 10 == 1:
                dataset_idx = 1  # val
            else:
                dataset_idx = 0  # train
            valid_clip_count += 1

            # get subtitle that fits clip
            for ib in range(word_index - 1, len(subtitle)):
                if ib < 0:
                    continue

                word_s = subtitle[ib]['start']
                word_e = subtitle[ib]['end']
                word = subtitle[ib]['word']
                if video_wrapper.second2frame(word_s) >= end_frame_no:
                    word_index = ib
                    break

                if video_wrapper.second2frame(word_e) <= start_frame_no:
                    continue

                word = normalize_string(word, my_config.LANG)
                if len(word) > 0:
                    clip_word_list.append([word, word_s, word_e])

            if clip_word_list:
                clip_skeleton = []
                custom_clip_skeleton = []
                clip_skeleton_3d = []

                n_detected_poses = 0

                # get skeletons of the upper body in the clip
                n_joints = 8
                custom_joints = 15
                for frame in clip_pose_all:
                    if frame:
                        skeleton = get_skeleton_from_frame(frame)[:n_joints * 3]
                        custom_skeleton = get_skeleton_from_frame(frame)[:custom_joints * 3]
                        del skeleton[2::3]  # remove confidence values
                        del custom_skeleton[2::3]  # remove confidence values
                        skeleton, _ = normalize_skeleton(skeleton)
                        clip_skeleton.append(skeleton)
                        custom_clip_skeleton.append(custom_skeleton)
                        n_detected_poses += 1
                    else:  # frame with no skeleton
                        clip_skeleton.append([np.nan] * (n_joints * 2))
                        custom_clip_skeleton.append([np.nan] * (custom_joints * 2))

                # proceed if skeleton list is not empty
                if n_detected_poses > 5:

                    # save subtitles and skeletons corresponding to clips
                    n_saved_clips[dataset_idx] += 1
                    clip_skeleton = np.asarray(clip_skeleton, dtype=np.float16)
                    clip_skeleton_3d_list = estimate3d.make3D(custom_clip_skeleton)

                    clip_skeleton_3d_result = []

                    for i in range(len(clip_skeleton_3d_list)):
                        normalized = normalize_skeleton_3d(clip_skeleton_3d_list[i])

                        neck_x = (normalized[1][0] + normalized[2][0]) / 2
                        neck_y = (normalized[1][1] + normalized[2][1]) / 2
                        neck_z = (normalized[1][2] + normalized[2][2]) / 2                                             
                        normalized.insert(2, [neck_x, neck_y, neck_z])

                        for j in range(len(normalized)):
                            total_3d_value[j * 3] += normalized[j][0]
                            total_3d_value[j * 3 + 1] += normalized[j][1]
                            total_3d_value[j * 3 + 2] += normalized[j][2]

                        total_num += 1
                        clip_skeleton_3d_result.append(normalized)

                    clip_skeleton_3d = np.asarray(clip_skeleton_3d_result)
                    clips[dataset_idx]['clips'].append({'words': clip_word_list,
                                                                                                                                                                                                                                                                                                                      'skeletons': clip_skeleton,
                                                        'skeletons_3d': clip_skeleton_3d.astype('float16'),
                                                        'start_frame_no': start_frame_no, 'end_frame_no': end_frame_no,
                                                        'start_time': video_wrapper.frame2second(start_frame_no),
                                                        'end_time': video_wrapper.frame2second(end_frame_no)
                                                        })
                    print('{} ({}, {})'.format(vid, start_frame_no, end_frame_no))
                else:
                    print('{} ({}, {}) - consecutive missing frames'.format(vid, start_frame_no, end_frame_no))

        # write to db
        for i in range(3):
            with db[i].begin(write=True) as txn:
                if len(clips[i]['clips']) > 0:
                    k = '{:010}'.format(v_i).encode('ascii')
                    v = bytes(pyarrow.serialize(clips[i]).to_buffer())

                    txn.put(k, v)

    print('no. of saved clips: train {}, val {}, test {}'.format(n_saved_clips[0], n_saved_clips[1], n_saved_clips[2]))

    for k in range(len(total_3d_value)):
        total_3d_value[k] /= total_num

    print("==========Total 3D Value==========")
    print(total_3d_value)

    # close db
    for i in range(3):
        db[i].sync()
        db[i].close()


if __name__ == '__main__':
    make_lmdb_gesture_dataset()