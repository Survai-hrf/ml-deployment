
import torch
from collections import Counter
import json
import argparse

#from mmdetection.src.map import intersection_over_union
from mmdetection.src.map import mean_average_precision
from mmdetection.src.test import perform_video_od



def parse_args():
    '''
    This script will generate evaluation statistics for a given model and store them in a json.
    '''
    parser = argparse.ArgumentParser(
        description='Evaluate a models performance')
    parser.add_argument('video_id', help='unique id for saving video and video info')
    parser.add_argument('--folder', default='', help='path/to/folder/of/videos')
    parser.add_argument('--gt', default='', help='path/to/ground/truth/data')
    parser.add_argument('--dev-mode', default=False, action='store_true', help='does not wipe anything, \
                                                                                returns more data')
    args = parser.parse_args()
    return args



#TODO: run model and generate predictions json
def evaluate_model(video_id, folder='', gt='', dev_mode=False):

    perform_video_od(video_id, folder, gt)




    # load ground truth and prediction bbox data
    pred = open('predictions.json')
    predictions = json.load(pred)
    gt = open('ground_truth.json')
    ground_truth = json.load(gt)

    # compute map
    mean_average_precision(pred_boxes=predictions, true_boxes=ground_truth, 
                            iou_threshold=0.5, box_format="midpoint", num_classes=7)


    #TODO: store data from mean_average_precision in outfile along with model config and weights, maybe the date as well



if __name__ == '__main__':

    args = parse_args()
    evaluate_model(args.video_id, args.folder, args.gt, args.dev_mode)