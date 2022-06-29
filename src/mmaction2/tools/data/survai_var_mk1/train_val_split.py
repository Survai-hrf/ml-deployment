import pandas as pd
from decord import VideoReader, cpu
from sklearn.model_selection import train_test_split
import argparse



def train_val_split(master_csv_path):

    CSV_MASTER_PATH = master_csv_path
    df = pd.read_csv(CSV_MASTER_PATH)
    error_counter = 0

    for index, row in df.iterrows():
        folder_name = row['label']
        vid_folder = "/home/beanbagthomas/code/hrf/Video-Swin-Transformer/data/survai_var_mk1/videos/" + folder_name + '/'
        vid_name = f"{row['youtube_id']}_{format(row['time_start'], '06d')}_{format(row['time_end'], '06d')}.mp4"
        full_vid_path = vid_folder + vid_name
        
        # Check if video is working
        try:
            vr = VideoReader(full_vid_path, ctx=cpu(0))
        except:
            df.drop(index, inplace=True)
            error_counter += 1
            print("error count: ", error_counter)

    train, val = train_test_split(df, test_size=0.20, random_state=69, stratify=df['label'])
    train.to_csv(CSV_MASTER_PATH.split(".")[0] + "_train.csv", index=False)
    val.to_csv(CSV_MASTER_PATH.split(".")[0] + "_val.csv", index=False)


if __name__ == '__main__':
    description = 'Helper script for train and val splitting a csv with kinetics styling.'
    p = argparse.ArgumentParser(description=description)

    p.add_argument(
        'csv_path',
        type=str,
        help=('location of master_csv to split. Checking if videos work is built in'))
    

    args = p.parse_args()
    train_val_split(args.csv_path)