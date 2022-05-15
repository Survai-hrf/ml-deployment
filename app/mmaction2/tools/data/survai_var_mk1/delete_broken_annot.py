import argparse
import os
from decord import VideoReader
from decord import cpu, gpu









def delete_broken(dataset_root):

    dataset_name = dataset_root.split("/")[-1]

    #get all vid dataset subsets ex: train and val, or, train val and test
    splits = [names.split("_")[-1] for names in os.listdir(dataset_root) if "videos_" in names]
    print("data subsets: ", splits)
    delete_counter = 0
    #loop through every dataset subset
    for subset in splits:
        print(subset)
        #get all vids location in subset
        with open(dataset_root + f'/{dataset_name}_{subset}_list.txt') as f:
            all_vids = f.readlines()
        f.close()
        #go through and test each video
        for vid in all_vids:
            vid = vid.split(" ")[0]
            try:
                vr = VideoReader(f'{dataset_root}/videos_{subset}/{vid}', ctx=cpu(0))
            except:
                #videos here have errored and need to be deleted and removed from the list

                print("error with ", f'videos_{subset}/{vid}')

                #delete video
                os.remove(f'{dataset_root}/videos_{subset}/{vid}') 
                delete_counter +=1
                print(f"deleted {delete_counter} files")

                #delete reference in .txt
                """with open(dataset_root + f'/{dataset_name}_{subset}_list.txt', "w") as f:
                    for line in all_vids:
                        if line.strip("\n") != vid:
                            f.write(line)
                f.close()"""
                #print("reference deleted")

        print(args.dataset_root)




if __name__ == '__main__':
    description = 'Helper script for deleting broken videos in dataset with kinetics styling.'
    p = argparse.ArgumentParser(description=description)
    p.add_argument(
        'dataset_root',
        type=str,
        help=('root location of video dataset: ex: /survai_var_mk1 or /kinetics400'))
    

    args = p.parse_args()
    delete_broken(args.dataset_root)
    