import argparse
import os
import json
import shutil

from mmdetection.src.apply_to_video import perform_video_od
from mmaction2.src.apply_to_video import perform_video_ar
from combine_model_data.combine_model_data import combine_model_data
from generate_visuals.generate_visuals import generate_visuals
from generate_master.generate_master import generate_master
from generate_statistics.generate_statistics import generate_statistics
import urllib.request

def parse_args():
    parser = argparse.ArgumentParser(
        description='MMAction2 predict different labels in a long video demo')
    parser.add_argument('mux_url', help='mux url, writes out detections.json to processed/(VIDEO_ID)/')
    parser.add_argument('video_id', help='id to video to update table to')

    args = parser.parse_args()
    return args

args = parse_args()

def processvideo(mux_url, video_id):
    try:
        shutil.rmtree('processed')
    except:
        pass    
    #make print bool for prod or dev and have it remove print statements

    #download video for processing
    print("downloading media...")
    os.makedirs(f'temp_videodata_storage', exist_ok=True)
    os.makedirs(f'processed', exist_ok=True)
    urllib.request.urlretrieve(f"{mux_url}?download={video_id}.mp4", f'temp_videodata_storage/{video_id}.mp4') 
    print('downloading complete')

    #process video
    print('initiating object detection model for inference...')
    perform_video_od(video_id) #TODO: FIX MODEL NOT STOPPING AT BATCH SIZE/SLOWING DOWN BY READING AT SECOND -- CALCULATE STATS AFTER HITTING THRESHOLD

    print('initiating action classification model for inference...')
    perform_video_ar(video_id) #TODO: MODEL SUCKS

    print('combining model results...')
    combine_model_data(video_id)

    print('generating visuals...')
    generate_visuals(video_id) #TODO: GRAPH SUCKS

    print('generating statistics...')
    generate_statistics(video_id) #TODO: GENERATE VIOLENT ACTIONS

    print('generating master json and saving...')
    final_json = generate_master(video_id) #TODO: violent actions broken , also formulate it right

    #save json as processed/(VIDEO_ID)/(VIDEO_ID).json
    with open(f'processed/{video_id}.json', 'w+') as file:
        json.dump(final_json, file)

    #clear all temp storage from previous operation
    print('clearing all temp storage...')
    try:
        shutil.rmtree('temp_videodata_storage')
    except:
        pass

    print('all operations complete!')

    return

if __name__ == '__main__':
    args = parse_args()
    processvideo(args.mux_url, args.video_id)

