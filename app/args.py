import argparse
import os
import json
#import psycopg2

from mmdetection.src.apply_to_video import perform_video_od
from mmaction2.src.apply_to_video import perform_video_ar
from combine_model_data.combine_model_data import combine_model_data
#from generate_visuals.generate_visuals import generate_visuals

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


    #download video for processing
    os.makedirs(f'temp_videodata_storage', exist_ok=True)
    os.makedirs(f'processed', exist_ok=True)
    urllib.request.urlretrieve(f"{mux_url}?download={video_id}.mp4", f'temp_videodata_storage/{video_id}.mp4') 
    print('preprocessing complete')

    #process video through models
    perform_video_od(video_id) #TODO: FIX MODEL NOT STOPPING AT BATCH SIZE/SLOWING DOWN BY READING AT SECOND

    perform_video_ar(video_id) #TODO: MODEL SUCKS

    combined_json = combine_model_data(video_id)

    #visual_json = generate_visuals(combined_json, video_id)
    #all_stats_json = generate_statistics(combined_json)
    #final_json = generate_master(visual_json, all_stats_json)

    final_json = combined_json

    #save json as processed/(VIDEO_ID)/(VIDEO_ID).json
    with open(f'processed/{video_id}.json', 'w+') as file:
        json.dump(final_json, file)

    #clear all temp storage from previous operation
    try:
        #shutil.rmtree('temp_videodata_storage')
        pass
    except:
        pass

    print('post processing complete')
    '''
    #?update status table
    sql = """UPDATE video
                SET status_id = %s
                WHERE id = %s"""

    try:
        conn = psycopg2.connect()
        cur = conn.cursor()
        cur.execute(sql, (2, video_id))
        conn.commit()
        cur.close()
        conn.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    print("works")
    '''
    return

if __name__ == '__main__':
    args = parse_args()
    processvideo(args.mux_url, args.video_id)


# we need playhead, and zoom/scale window
