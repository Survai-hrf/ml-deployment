import pandas as pd
import cv2
import os
import moviepy.editor as mp
import glob
import numpy as np
import collections
from mmdet.apis import inference_detector, init_detector
import json
import glob
import matplotlib
matplotlib.use('agg')



def perform_video_od(video_id, gen_video, folder):
    
    def calculate_mode(fps_frame_list, current_second):

        class_list = open("model_artifacts/classes.txt","r").readlines()

        temp_count_storage = {}

        #get all classes
        for i in class_list:
            class_name = i.split('\n')[0]
            temp_count_storage[class_name] = []

        #get all detections per frame into list for each class
        #print(fps_frame_list)

        for i in fps_frame_list:
            for key, value in i.items():
                if key in temp_count_storage.keys():
                    temp_count_storage[key].append(value)
            for key, val in temp_count_storage.items():
                if key not in i.keys():
                    temp_count_storage[key].append(0)


        #change values to the mode of all frames
        for key, value in temp_count_storage.items():
            try:
                temp_count_storage[key] = max(set(temp_count_storage[key]), key=temp_count_storage[key].count)
            except ValueError:
                return

        # remove empty
        temp_count_storage = {k: v for k, v in temp_count_storage.items() if v}

        if temp_count_storage:
            det_per_second[int(current_second)] = temp_count_storage




    def make_video(outvid, images=None, fps=30, size=None,
                is_color=True, format="FMP4"):

        from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize

        fourcc = VideoWriter_fourcc(*format)
        vid = None
        for image in images:
            if not os.path.exists(image):
                raise FileNotFoundError(image)
            img = imread(image)
            if vid is None:
                if size is None:
                    size = img.shape[1], img.shape[0]
                vid = VideoWriter(outvid, fourcc, float(fps), size, is_color)

            if size[0] != img.shape[1] and size[1] != img.shape[0]:
                img = resize(img, size)
            vid.write(img)
        if vid is None:
            return
        vid.release()
        return vid

    
    # def generate_json(batch_frame):
        




    
    # if folder of videos is not specified default to:
    if folder == '':
        video = f'temp_videodata_storage/{video_id}.mp4'
    else:
        video = folder

    config = glob.glob("model_artifacts/*.py")[0]
    checkpoint = glob.glob("model_artifacts/*.pth")[0]
    device = 'cuda:0'
    score_thr = 0.5


    VIDEO_DIR = 'temp_videodata_storage/'
    TEMP_IMAGE_STORAGE_DIR = 'src/mmdetection/image_temp'
    TEMP_AUDIO_STORAGE_DIR = 'src/mmdetection/audio_temp'
    RAW_FRAME_STORAGE_DIR = 'src/mmdetection/raw_frames'


    os.makedirs(VIDEO_DIR, exist_ok=True)
    os.makedirs(TEMP_IMAGE_STORAGE_DIR, exist_ok=True)
    os.makedirs(TEMP_AUDIO_STORAGE_DIR, exist_ok=True)
    os.makedirs(RAW_FRAME_STORAGE_DIR, exist_ok=True)

    #MODEL CONFIG
    # We use a RTX3090 with 24GB memory, which works on 36 images. 
    batch_size = 5


    #load model
    model = init_detector(config, checkpoint, device=device)
    #delete image_temp on first video in case of early stop
    for f in os.listdir(TEMP_IMAGE_STORAGE_DIR):
        os.remove(os.path.join(TEMP_IMAGE_STORAGE_DIR, f))
    # Pull Audio from video to apply to overlay video

    try:

        if gen_video == True:

            if folder == '':
                my_clip = mp.VideoFileClip(f'{VIDEO_DIR}{video_id}.mp4')
            else:
                my_clip = mp.VideoFileClip(folder)

            my_clip.audio.write_audiofile(f'{TEMP_AUDIO_STORAGE_DIR}/{video_id}.mp3')
            print("audio saved...")

    except Exception as e: 
        print(e)
        print("no audio!")

    capture = cv2.VideoCapture(video)

    
    
    frames = []
    
    #this counter is for data output

    frame_count = 0
    det_per_second = {}
    fps_frame_list = []
    json_list = {}
    # these 2 lines can be removed if you dont have a 1080p camera.
    height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    fps = round(capture.get(cv2.CAP_PROP_FPS))

    while True:
        
        ret, frame = capture.read()
        # Bail out when the video file ends
        if not ret:
            break
        
        # Save each frame of the video to a list
        frame_count += 1
        frames.append(frame)

        print('frame_count :{0}'.format(frame_count))
        
        # if need to reset gpu batch, or calculate the det per second
        if len(frames) == batch_size or frame_count % fps == 0:

            result = inference_detector(model, frames)

            # calculate and store detections in fps_frame_list
            i = 1
            for batch_frame in result:
                file_name = f'{frame_count + i - batch_size}.jpg'

                score_thr=score_thr # set confidence score threshold

                bbox_result, segm_result = batch_frame
                bboxes = np.vstack(bbox_result)
                #bbox_df = pd.DataFrame(bboxes, columns=['A', 'B', 'C', 'D', 'E'])
                #bbox_df.to_csv(r'bbox.csv', index=False)
                labels = [
                    np.full(bbox.shape[0], i, dtype=np.int32)
                    for i, bbox in enumerate(bbox_result)
                ]
                labels = np.concatenate(labels)
                #print(labels)

                scores = bboxes[:, -1]
                labels = labels[scores > score_thr] # keep only the labels that score above the confidence score threshold
                fps_frame_list.append(dict(collections.Counter([model.CLASSES[label] for label in labels])))
                json_list[file_name] = {
                    'bbox': bboxes.tolist(),
                    'labels': labels.tolist()
                }
                i += 1


            # generate json results every 1 second
            if len(frames) == batch_size:
                
                # save raw frames to folder
                for i, item in enumerate(zip(frames, result)):
                    name = '{0}.jpg'.format(frame_count + i - batch_size)
                    name = os.path.join(RAW_FRAME_STORAGE_DIR, name)
                    cv2.imwrite(name, frame)
                    print('saving raw frame:{0}'.format(name))

                if gen_video == True: 
                    for i, item in enumerate(zip(frames, result)):

                        frame = model.show_result(item[0], item[1], score_thr=score_thr)

                        name = '{0}.jpg'.format(frame_count + i - batch_size)
                        name = os.path.join(TEMP_IMAGE_STORAGE_DIR, name)
                        cv2.imwrite(name, frame)
                        print('writing to file:{0}'.format(name))

            if frame_count % fps == 0:
                calculate_mode(fps_frame_list, current_second=frame_count/fps)
                fps_frame_list = []

            print('Predicted')
            frames = []
            ### CALCULATE DETECTIONS PER FRAME #######################################################
            
            i=1
            for batch_frame in result:
                score_thr=score_thr
                file_name = f'{frame_count - batch_size + i}.jpg'
                bbox_result, segm_result = batch_frame
                bboxes = np.vstack(bbox_result)
                labels = [
                    np.full(bbox.shape[0], i, dtype=np.int32)
                    for i, bbox in enumerate(bbox_result)
                ]
                labels = np.concatenate(labels)

                scores = bboxes[:, -1]
                labels = labels[scores > score_thr]
                custom_labels = [model.CLASSES[label] for label in labels]
                #print(custom_labels)
                detection_counter = dict(collections.Counter(custom_labels))
                det_per_second[frame_count - batch_size + i] = detection_counter
                
                i += 1
            
            ##############################################################################################
            
            

    # WRITE ALL DET IN FRAME TO DICT
    with open(f'{VIDEO_DIR}{video_id}_od.json', 'w+') as file:
        json.dump(det_per_second, file)

    # Write file, bbox and label data to json
    with open(f'{VIDEO_DIR}{video_id}_export_data.json', 'w+') as f:
        json.dump(json_list, f)


    # WRITE FILE NAMES, BBOXES w/ LABELS TO DICT
        
    capture.release()

    if gen_video == True:

        # Directory of images to assemble video from
        images = list(glob.iglob(os.path.join(TEMP_IMAGE_STORAGE_DIR, '*.*')))
        # Sort the images by integer index
        images = sorted(images, key=lambda x: float(os.path.split(x)[1][:-3]))

        outvid = f'temp_videodata_storage/{video_id}_overlay.mp4'
        make_video(outvid, images, fps=round(fps))



    #Apply Audio to Overlay#################################################################################################################
    if gen_video == True:
        try:
            print("Applying audio...")
            audio_clip = mp.AudioFileClip(f'{TEMP_AUDIO_STORAGE_DIR}/{video_id}.mp3')
            my_clip = mp.VideoFileClip(outvid)
            my_clip = my_clip.set_audio(audio_clip)
            my_clip.write_videofile(f'processed/{video_id}_overlay.mp4')
            print("Audio Applied Succesfully, video saved to out dir")
        except:
            print("error on applying audio, or no audio!")


    #Delete traces of video left###################################################################################################3
    print("Cleaning up 0/2")

    for f in os.listdir(TEMP_IMAGE_STORAGE_DIR):
        os.remove(os.path.join(TEMP_IMAGE_STORAGE_DIR, f))
    print("temp frames removed 1/2")

    for f in os.listdir(TEMP_AUDIO_STORAGE_DIR):
        os.remove(os.path.join(TEMP_AUDIO_STORAGE_DIR, f))
    print("Temp audio removed 2/2")

    print('\n', video, " completed ^v^", '\n')

