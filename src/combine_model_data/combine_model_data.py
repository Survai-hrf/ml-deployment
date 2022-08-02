import json
import cv2


def combine_model_data(video_id, folder):

    def get_length(filename):
        cap = cv2.VideoCapture(filename)
        fps = cap.get(cv2.CAP_PROP_FPS)      # OpenCV2 version 2 used "CV_CAP_PROP_FPS"
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count/fps
        return duration
    
    def mergeDictionary(dict_1, dict_2):
        dict_3 = {**dict_1, **dict_2}
        for key, value in dict_3.items():
            if key in dict_1 and key in dict_2:
                    dict_3[key] = {**value, **dict_1[key]}
        dict_3 = dict(sorted(dict_3.items()))
        return dict_3

    with open(f'temp_videodata_storage/{video_id}_od.json') as json_file:
        od_json = json.load(json_file)
        od_json = {int(k):v for k,v in od_json.items()}

    with open(f'temp_videodata_storage/{video_id}_ar.json') as json_file:
        ar_json = json.load(json_file)
        ar_json = {int(k):v for k,v in ar_json.items()}
    
    if folder == '':
        video_length = get_length(f"temp_videodata_storage/{video_id}.mp4")
    else:
        video_length = get_length(folder)
    merged_json = mergeDictionary(od_json, ar_json)
    combined_json = {}
    combined_json['seconds'] = merged_json
    combined_json['videoInfo'] = {'videoLength': int(video_length)}

    with open(f"temp_videodata_storage/{video_id}_combined.json", "w") as f:
        json.dump(combined_json, f)
    

