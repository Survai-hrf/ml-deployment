import argparse
import os
import json
import shutil
import requests

from mmdetection.src.apply_to_video import perform_video_od
from mmaction2.src.apply_to_video import perform_video_ar
from combine_model_data.combine_model_data import combine_model_data
from generate_visuals.generate_visuals import generate_visuals
from generate_master.generate_master import generate_master
from generate_statistics.generate_statistics import generate_statistics
from connect_and_download.connect_and_download import connect_and_download


def parse_args():
    '''THIS SCRIPT WIPES ALL PROCESSED DATA WHEN IT STARTS AND ENDS. TO DISABLE USE --dev-mode 
        - dev-mode also enables exporting of additional data such as an image version of the graph to review
    COMMAND TO RUN DEV MODE, AND FROM LOCAL FOLDER WITH FULL EXPORT:
     - python src/args.py blank blank --gen-video --folder /path/to/video/folder --dev-mode
     - The folder arguement can handle nested files and folders, and only pulls video files it knows it can process.
    '''
    parser = argparse.ArgumentParser(
        description='MMAction2 predict different labels in a long video demo')
    parser.add_argument('--gen-video', default=False, action='store_true', help='generates video overlay')
    parser.add_argument('--folder', default='', help='path/to/folder/of/videos')
    parser.add_argument('--dev-mode', default=False, action='store_true', help='does not wipe anything, \
                                                                                returns more data')
    args = parser.parse_args()
    return args


def processvideo(video_id, gen_video=False, folder='', dev_mode=False):

    while True:
        #don't wipe previous data if devmode was specified
        if dev_mode == False:
            try:    
                shutil.rmtree('temp_videodata_storage')
                shutil.rmtree('processed')
            except:
                pass    
        
        os.makedirs(f'temp_videodata_storage', exist_ok=True)
        os.makedirs(f'processed', exist_ok=True)

        print("downloading media...")
        video_id, resp = connect_and_download(args.folder)

        if resp == 0:
            print("No more messages, shutting down")
            break
        #process video
        print('initiating object detection model for inference...')
        perform_video_od(video_id, gen_video, folder) #TODO: FIX MODEL NOT STOPPING AT BATCH SIZE/SLOWING DOWN BY READING AT SECOND -- CALCULATE STATS AFTER HITTING THRESHOLD

        print('initiating action classification model for inference...')
        perform_video_ar(video_id, folder) #TODO: MODEL SUCKS

        print('combining model results...')
        combine_model_data(video_id, folder)

        print('generating visuals...')
        generate_visuals(video_id, dev_mode) #TODO: GRAPH SUCKS

        print('generating statistics...')
        generate_statistics(video_id) # what specifies a "violent action" and its calculation is specified here

        print('generating master json and saving...')
        final_json = generate_master(video_id) #TODO: violent actions broken , also formulate it right

        #save json as processed/(VIDEO_ID)/(VIDEO_ID).json
        if dev_mode == True:
            with open(f'processed/{video_id}.json', 'w+') as file:
                json.dump(final_json, file)

        #send json to web
        API_ENDPOINT = "https://glimpse-kjkgb.ondigitalocean.app/"
        data = final_json
        r = requests.post(url=API_ENDPOINT, data=data)
            
        if dev_mode == False:
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

    # if no folder is provided
    if args.folder == '':
        video_id=1
        processvideo(video_id, args.gen_video, args.folder, args.dev_mode)

    else:
        import os
        import mimetypes
        from cv2 import VideoCapture
        import traceback
        mimetypes.init()

        #iterate folder and all subfolders looking for videos
        for subdir, dirs, files in os.walk(args.folder):
            print('iterating all files in sub directories looking for videos...')
            for file in files:

                filepath = subdir + os.sep + file

                mimestart = mimetypes.guess_type(filepath)[0]

                if mimestart != None:
                    mimestart = mimestart.split('/')[0]

                    #if file is a video
                    if mimestart in ['video']:
                        #verify its a working video 
                        try:
                            capture = VideoCapture(filepath)
                            print(filepath)
                            processvideo(os.path.splitext(file)[0], args.gen_video, filepath, args.dev_mode)
                        except Exception as e:
                            print(f"broken video: {filepath}")
                            print(e)
                            print(traceback.format_exc())

            
