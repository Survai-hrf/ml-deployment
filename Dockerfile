# syntax=docker/dockerfile:1

FROM nvidia/cuda:11.3.1-devel-ubuntu20.04

RUN apt-get update && apt-get install -yq wget

ENV DEBIAN_FRONTEND=noninteractive
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"
ENV FORCE_CUDA="1"
ENV HOME /home

RUN apt-get install ffmpeg libsm6 libxext6 gcc ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6  -y
SHELL [ "/bin/bash", "--login", "-c" ]

#RUN apt-get install ffmpeg ninja-build
RUN apt-get install libsm6 libxext6 gcc libglib2.0-0 libsm6 libxrender-dev libxext6  -y

COPY environment.yml /tmp/
COPY entrypoint.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/entrypoint.sh

# install miniconda 
ENV CONDA_DIR $HOME/miniconda3
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    chmod +x ~/miniconda.sh && \
    ~/miniconda.sh -b -p $CONDA_DIR && \
    rm ~/miniconda.sh
# make non-activate conda commands available
ENV PATH=$CONDA_DIR/bin:$PATH
# make conda activate command available from /bin/bash --login shells
RUN echo ". $CONDA_DIR/etc/profile.d/conda.sh" >> ~/.profile
# make conda activate command available from /bin/bash --interative shells
RUN conda init bash

ENV PROJECT_DIR $HOME/app
RUN mkdir $PROJECT_DIR
WORKDIR $PROJECT_DIR

# build the conda environment
ENV ENV_PREFIX $PWD/env
RUN conda update --name base --channel defaults conda && \
    conda env create --prefix $ENV_PREFIX --file /tmp/environment.yml --force && \
    conda clean --all --yes

COPY . .

RUN conda activate $ENV_PREFIX && \
    pip install --no-cache-dir --upgrade pip wheel setuptools && \
    MMCV_WITH_OPS=1 pip install -e src/mmcv/  && \
    pip install -v -e src/mmaction2/  && \
    pip install -v -e src/mmdetection/ && \
    conda deactivate

EXPOSE 5000
ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]

#command to build:  docker image build --file Dockerfile -t sdeploy .
#command to run: docker run --rm --gpus all -p 5000:5000  sdeploy 
#docker tag sdeploy:latest seanbackstrom/sdeploy:sdeploy
#docker push seanbackstrom/sdeploy:sdeploy

#for AWS
#aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 683846764153.dkr.ecr.us-east-2.amazonaws.com
#docker build --file Dockerfile -t survai-ml-api .
#docker tag survai-ml-api:latest 683846764153.dkr.ecr.us-east-2.amazonaws.com/survai-ml-api:latest
#

CMD ["python", "src/args.py"]