import json
import random
from collections import deque
from operator import itemgetter
import glob 

import cv2
import mmcv
import numpy as np
import torch
from mmcv import Config
from mmcv.parallel import collate, scatter

from mmaction.apis import init_recognizer
from mmaction.datasets.pipelines import Compose

def perform_video_ar(video_id, folder):

    def get_results_video(det_per_second, result_queue,thr,ind,fps):
        if len(result_queue) != 0:
            results = result_queue#.popleft()
            timestamp = int((ind/round(fps, 1))) 

            if timestamp < 11:
                timestamp = 1
            else:
                timestamp -= 10

            det_per_second[timestamp] = {}

            for result in results[0]:

                selected_label, score = result
                if selected_label == "striking" and score >= 4.0:
                    pass
                elif selected_label == "throwing" and score <= 4.4:
                    continue
                elif selected_label == 'spray' and score <= 4.5:
                    continue
                elif selected_label == 'aiming' and score <= 6.0:
                    continue
                elif selected_label == 'person_on_ground' and score <= 4.0:
                    continue
                elif selected_label == 'restraining' and score <= 5.5:
                    continue
                elif selected_label == 'brawling' and score <= 2.6:
                    continue
                elif selected_label == 'crowd' and score <= 5.2:
                    continue
                elif selected_label == 'nothing':
                    continue
                if score < thr:
                    continue
                
                #TODO: TEST MODEL PRED SCORE THRESHOLDS?
                score = str(round(score, 2))
                det_per_second[timestamp][selected_label] = 1

            if not det_per_second[timestamp]:
                del det_per_second[timestamp]

                    
                    


    def show_results(model, data, label):

        video = str(video_id) + '.mp4'
        det_per_second = {}
        frame_queue = deque(maxlen=sample_length)
        result_queue = deque(maxlen=1)

        #if folder is not specified default to this
        if folder == '':
            cap = cv2.VideoCapture(f'{VIDEO_DIR}{video}')
        # if a folder of videos is specified
        else:
            cap = cv2.VideoCapture(folder)
        num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        ind = 0

        prog_bar = mmcv.ProgressBar(num_frames)
        backup_frames = []

        while ind < num_frames:
            ind += 1
            prog_bar.update()
            ret, frame = cap.read()

            # ensure it has time to load in the frames
            if ret:
                pass
            else:
                ind -= 1
                cv2.waitKey(100)
                continue
            if frame is None:
                # drop it when encounting None
                print("none")
                continue
            backup_frames.append(np.array(frame)[:, :, ::-1])
            if ind == sample_length:
                # provide a quick show at the beginning
                frame_queue.extend(backup_frames)
                backup_frames = []
            elif ((len(backup_frames) == input_step
                and ind > sample_length) or ind == num_frames):

                chosen_frame = random.choice(backup_frames)
                backup_frames = []
                frame_queue.append(chosen_frame)

            ret, scores = inference(model, data, frame_queue)

            if ret:
                num_selected_labels = min(len(label), 5)
                scores_tuples = tuple(zip(label, scores))
                scores_sorted = sorted(
                    scores_tuples, key=itemgetter(1), reverse=True)
                results = scores_sorted[:num_selected_labels]

                if results[0][1] >= threshold:
                    result_queue.append(results)

            get_results_video(det_per_second,result_queue,threshold,ind,fps)

        cap.release()
        cv2.destroyAllWindows()
        #print(det_per_second)
        with open(f'{VIDEO_DIR}/{video_id}_ar.json', 'w') as js:
            json.dump(det_per_second, js)

    def inference(model, data, frame_queue):
        if len(frame_queue) != sample_length:
            # Do no inference when there is no enough frames
            return False, None

        cur_windows = list(np.array(frame_queue))
        if data['img_shape'] is None:
            data['img_shape'] = frame_queue[0].shape[:2]

        cur_data = data.copy()
        cur_data['imgs'] = cur_windows
        cur_data = test_pipeline(cur_data)
        cur_data = collate([cur_data], samples_per_gpu=1)

        if next(model.parameters()).is_cuda:
            cur_data = scatter(cur_data, [device])[0]
        with torch.no_grad():
            scores = model(return_loss=False, **cur_data)[0]

        if stride > 0:
            pred_stride = int(sample_length * stride)
            for _ in range(pred_stride):
                frame_queue.popleft()

        return True, scores

    



    VIDEO_DIR = f'temp_videodata_storage/'
    config = glob.glob('src/model_artifacts/ar/*.py')[0]
    checkpoint= glob.glob('src/model_artifacts/ar/*.pth')[0]
    label= glob.glob('src/model_artifacts/ar/*.txt')[0]
    input_step=1
    device='cuda:0'
    threshold=4.0
    stride=0.9
    cfg_options={}

    EXCLUED_STEPS = [
        'OpenCVInit', 'OpenCVDecode', 'DecordInit', 'DecordDecode', 'PyAVInit',
        'PyAVDecode', 'RawFrameDecode', 'FrameSelector']

    device = torch.device(device)
    cfg = Config.fromfile(config)
    cfg.merge_from_dict(cfg_options)

    model = init_recognizer(cfg, checkpoint, device=device)
    data = dict(img_shape=None, modality='RGB', label=-1)
    with open(label, 'r') as f:
        label = [line.strip() for line in f]

    # prepare test pipeline from non-camera pipeline
    cfg = model.cfg
    sample_length = 0
    pipeline = cfg.data.test.pipeline
    pipeline_ = pipeline.copy()
    for step in pipeline:
        if 'SampleFrames' in step['type']:
            sample_length = step['clip_len'] * step['num_clips']
            data['num_clips'] = step['num_clips']
            data['clip_len'] = step['clip_len']
            pipeline_.remove(step)
        if step['type'] in EXCLUED_STEPS:
            # remove step to decode frames
            pipeline_.remove(step)
    test_pipeline = Compose(pipeline_)

    assert sample_length > 0
    sample_length = sample_length
    test_pipeline = test_pipeline
    show_results(model, data, label)

