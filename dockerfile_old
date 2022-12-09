# syntax=docker/dockerfile:1
FROM nvidia/cuda:11.3.1-devel-ubuntu20.04
RUN apt-get update && apt-get install -yq wget

ENV DEBIAN_FRONTEND=noninteractive
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0+PTX"
ENV TORCH_NVCC_FLAGS="-Xfatbin -compress-all"
ENV CMAKE_PREFIX_PATH="$(dirname $(which conda))/../"
ENV FORCE_CUDA="1"

RUN apt-get install ffmpeg libsm6 libxext6 gcc ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6  -y
SHELL [ "/bin/bash", "--login", "-c" ]

# Create a non-root user
ARG username=servai
ARG uid=1000
ARG gid=100
ENV USER $username
ENV UID $uid
ENV GID $gid
ENV HOME /home/$USER
RUN adduser --disabled-password \
    --gecos "Non-root user" \
    --uid $UID \
    --gid $GID \
    --home $HOME \
    $USER

COPY environment.yml /tmp/
RUN chown $UID:$GID /tmp/environment.yml
COPY entrypoint.sh /usr/local/bin/
RUN chown $UID:$GID /usr/local/bin/entrypoint.sh && \
    chmod u+x /usr/local/bin/entrypoint.sh

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

# TODO: IGNORE ARCHIVE

#command to build:  docker image build   --build-arg username=servai   --build-arg uid=1000   --build-arg gid=100   --file Dockerfile -t sdeploy .
#command to run: docker run --rm --gpus all -p 5000:5000  sdeploy 
#docker tag sdeploy2:latest seanbackstrom/sdeploy2:sdeploy2
#docker push seanbackstrom/sdeploy2:sdeploy2
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]