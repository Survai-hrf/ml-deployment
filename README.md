
# SurvAI Model Production & Deployment Repository

![image (1)](https://user-images.githubusercontent.com/29393311/189803632-58275057-3501-4c93-8b75-77c37062d182.png)

Contained in this repo is the full model architecture that makes up SurvAI. It contains the Action Recognition and Object Detection model as well as meta tools to
utilize both models in tandem. These meta tools allow the exporting of all necessary JSON information for web which includes a serialized graph for the front end.
With optional commands, the detections made in a video can be exported in a variety of formats including csv or on a per-model basis, as well as a video with overlays
of detections. Finally, the ml-deployment repo is built to be activated as an api, and/or a fully functioning docker container with an API. 

**ADVISORY:** The code inside the model folders has been minimalized, and heavily customized and some code unrelated to deployment and inference has been removed. 
For full repositories please see the original models hosted at MMLab's github. 
[Object Detection](https://github.com/open-mmlab/mmdetection), 
[Action Recognition](https://github.com/open-mmlab/mmaction2)


## Environment Setup

### Description

SurvAI's Machine Learning environment is complex, balancing very specific versions of packages that each model needs. It is important that the version numbers
of each package are maintained as listed in the requirements.txt. Due to the many helper scripts found in this repo, if a package is used in a script not covered
by the requirements.txt, it is okay to just pip install it, as it will be a non critical package. 

### Requirements

- Ubuntu 20.04
- CUDA 11.3
- Conda (Up to date)
- 8 GB VRAM GPU or > 

### Install Instructions

First, make sure CUDA 11.3 has been properly installed at the system level of your workstation. There is a variety of ways to do it, 
but ensure that while in your conda environment (this environment is created in the next step) the command
``` torch.cuda.is_available() ``` returns True.

1. ) Some packages are needed at the system level of Ubuntu to properly crop videos and local install model packages. In a bash terminal run:
     - ```apt-get install ffmpeg libsm6 libxext6 gcc ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6  -y```
     
2. ) With miniconda3 installed, at the root directory of ml-deployment run:

     -  ```conda env create -f environment.yml```
     -  ```conda activate sdeploy```
     -  ```MMCV_WITH_OPS=1 pip install -e src/mmcv/```
     -  ```pip install -v -e src/mmaction2/```
     -  ```pip install -v -e src/mmdetection/```
     
          **ADVISORY:**  If you install any more packages into this environment, be sure to use pip. Using conda will cause package conflicts and break the environment.


## Live Deployment

Inside the main python script args.py, the function connect_and_download() will automatically pull a message from the AWS queue and procvess and return the results to the web API server. 

The AWS queue accepts the following parameters:

    ) Mux url (ex: https://stream.mux.com/{PLAYBACK_ID}/{HIGHEST_AVAILABLE_RESOLUTION}.mp4)

    ) Unique video id

NOTE: you must be connected to the appropriate AWS queue. To connect to the AWS queue, you must have the following information in a .env file:

    REGION_NAME=” ”
    AWS_ACCESS_KEY_ID=” ”
    AWS_SECRET_ACCESS_KEY=” “
    QUEUE_URL=” “

### Processing description


After a message is sent to the queue, the script args.py will download the video, process it, and return all necessary json data to the Glimpse web API server. All of these files used to generate the response
are stored in the "processed" folder inside src. **Mux videos will only download if [MP4 Support](https://docs.mux.com/guides/video/enable-static-mp4-renditions) 
has been enabled in Mux for that video  (this process is not done on the ML API side).

## Docker
The docker images task is to automatically do this process. Be sure that if you intend to run locally you have NVIDIA-docker installed to enable gpu support with your docker images and containers.

The Dockerfile should be generated with the following command:
- ```docker image build --file Dockerfile -t sdeploy .```

This image can be ran with the following command:
- ```docker run --rm --gpus all sdeploy```
 

## Performing inference locally
The easiest way to run models on videos is the ```args.py``` file inside the src folder. It is a high level script allowing you to do a variety of tasks easily.
It accepts the following arguements:

- "--gen-video"
- "--folder"
- "--dev-mode"

### --gen-video
setting this to ```True``` will output the input video with object and action bounding boxes into the processed folder.

### --folder
if you have a folder of local videos you want to run through the models without having to upload them to mux, pass this arguement a folder path. It will only pull confirmed functioning videos, so if the folder contains images, documents, or any other file types they will be ignored. It also accepts nested folders!

### --dev-mode
Normally when args.py runs, all the data that is temporarily saved is wiped at the end. Setting dev-mode to ```True``` preserves all files that are generated by the script pipeline, as well as a few specific outputs such as .csv's to help debug and understand the model process. It assists greatly with debugging or experimentation with individual functions inside this pipeline.

## Acknowledgement & Support
Original models: [Object Detection](https://github.com/open-mmlab/mmdetection), [Action Recognition](https://github.com/open-mmlab/mmaction2)

Created by: Sean Backstrom, sean.backstrom@gmail.com

Feel free to reach out anytime to the email above for any support or problems with the codebase.
     
     
     
