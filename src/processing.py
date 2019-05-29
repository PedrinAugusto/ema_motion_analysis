import os
import sys
import cv2
import time
import json
import numpy as np
import matplotlib.pyplot as plt
from support import *
from detection import *

videos_dir = "../Videos/"
data_dir = "../Data/"

n_points = 18

map_idx = np.array([[31,32], [39,40], [33,34], [35,36], [41,42], [43,44], 
          [19,20], [21,22], [23,24], [25,26], [27,28], [29,30], 
          [47,48], [49,50], [53,54], [51,52], [55,56], 
          [37,38], [45,46]])

pose_pairs = np.array([[1,2], [1,5], [2,3], [3,4], [5,6], [6,7],
              [1,8], [8,9], [9,10], [1,11], [11,12], [12,13],
              [1,0], [0,14], [14,16], [0,15], [15,17],
              [2,17], [5,16], [2, 8], [5, 11]])

colors = [[0,100,255], [0,100,255], [0,255,255], [0,100,255], [0,255,255], [0,100,255],
         [0,255,0], [255,200,100], [255,0,255], [0,255,0], [255,200,100], [255,0,255],
         [0,0,255], [255,0,0], [200,200,0], [255,0,0], [200,200,0], 
         [0,0,0], [0,0,0], [0,255,0], [0,255,0]]


def saveProcessedFile(video_name_ext, file_name, output_name, function_ext, summary):
    
    print("Processing...")
    
    if(video_name_ext == "None"):
        print("No video found")
        return
    if(file_name == "None"):
        print("No DATA found")
        return
    video_name = (video_name_ext).split(sep='.')[0]
    file_dir = data_dir + video_name + '/'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_path = file_dir + file_name
    metadata, data = readFrameDATA(file_path, frame_n=0)
    n_frames, fps = metadata["n_frames"], metadata["fps"]
    frame_height, frame_width = metadata["frame_height"], metadata["frame_width"]
    
    joint_pairs = metadata["joint_pairs"]
    pairs = []
    for j in joint_pairs:
        pairs.append(pose_pairs[j])
    joints = np.unique(pairs)

    output_path = file_dir + output_name + ".data"
    video_path = file_dir + output_name + ".mp4"
    
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    vid_writer = cv2.VideoWriter(video_path, fourcc, fps, (frame_width,frame_height))

    metadata["summary"] = str(summary)
    with open(output_path, 'w') as f:
        f.write(json.dumps(metadata))
        f.write('\n')
    
    sys.path.append('../postprocessing/')
    function = (function_ext).split(sep='.')[0]

    for n in range(n_frames):
        t = time.time()

        processing = __import__(function)
        processing_function = getattr(processing, 'processing_function')
        main_keypoints = processing_function(file_path, n)
        file_data = {
            'keypoints': main_keypoints.tolist()
        }
        
        with open(output_path, 'a') as f:
            f.write(json.dumps(file_data))
            f.write('\n')
        
        frame, _, _ = getFrame(video_name_ext, n)
        
        for i in joint_pairs:
            pose_pairs[i][0]
            a_idx = (joints.tolist()).index(pose_pairs[i][0])
            b_idx = (joints.tolist()).index(pose_pairs[i][1])
            A = tuple(main_keypoints[a_idx].astype(int))
            B = tuple(main_keypoints[b_idx].astype(int))
            if (-1 in A) or (-1 in B):
                continue
            cv2.line(frame, (A[0], A[1]), (B[0], B[1]), colors[i], 3, cv2.LINE_AA)
                
        vid_writer.write(frame)
       
        time_taken = time.time() - t
        print("[{0:d}/{1:d}] {2:.1f} seconds/frame".format(n+1, n_frames, time_taken), end="\r")
    
    vid_writer.release()
    print()
    print("Done")