import json
import argparse

#from mmdetection.src.map import intersection_over_union
from mmdetection.src.map import mean_average_precision
from mmdetection.src.run import perform_video_od



def parse_args():
    '''
    This script will generate evaluation statistics for a given model and store them in a json.
    '''
    parser = argparse.ArgumentParser(
        description='Evaluate a models performance')
    parser.add_argument('video_id', help='unique id for saving video and video info')
    parser.add_argument('--folder', default='ground_truth/videos', help='path/to/folder/of/videos')
    parser.add_argument('--gen-video', default=False, action='store_true', help='generates video overlay')
    parser.add_argument('--gt', default='ground_truth/jsons/ground_truth.json', help='path/to/ground/truth/data')
    parser.add_argument('--pred', default='ground_truth/jsons', help='path/to/store/predictions')
    parser.add_argument('--config', default='model_artifacts', help='path/to/config/folder')
    parser.add_argument('--checkpoint', default='model_artifacts', help='path/to/checkpoint/folder')
    args = parser.parse_args()
    return args





def evaluate_model(video_id, folder='', gen_video=False, gt='', pred='', config='', checkpoint=''):

    # run model to generate predictions
    perform_video_od(video_id, gen_video, folder, config, checkpoint, pred)


    # load model predictions along with ground_truth
    with open(f'{pred}/predictions.json') as p:
        predictions = json.load(p)

    with open(gt) as g:
        ground_truth = json.load(g)


    # compute map
    mean_average_precision(pred_boxes=predictions, true_boxes=ground_truth, 
                            iou_threshold=0.5, box_format="midpoint", num_classes=7)


    #TODO: store data from mean_average_precision in outfile along with model config and weights, maybe the date as well





if __name__ == '__main__':

    args = parse_args()

    '''
    # if no folder is provided
    if args.folder == '':
        evaluate_model(args.video_id, args.folder, args.gen_video, args.gt, args.pred, args.config, args.checkpoint)
    else:
    '''
        
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
                        evaluate_model(os.path.splitext(file)[0], filepath, args.gen_video, args.gt, args.pred, args.config, args.checkpoint)
                    except Exception as e:
                        print(f"broken video: {filepath}")
                        print(e)
                        print(traceback.format_exc())