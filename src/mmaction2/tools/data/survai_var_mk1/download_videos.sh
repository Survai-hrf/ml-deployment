#!/usr/bin/env bash

# set up environment
#conda env create -f environment.yml
#source activate kinetics
#pip install --upgrade youtube-dl

#ANNOT TYPE = master or train_val
ANNOT_NAME=$1

DATA_DIR="data/survai_var_mk1"

ANNO_DIR="data/survai_var_mk1/annotations"

python tools/data/survai_var_mk1/download.py ${ANNO_DIR}/${ANNOT_NAME}_master.csv ${DATA_DIR}/videos

#python download.py ${ANNO_DIR}/${ANNOT_NAME}_train.csv ${DATA_DIR}/videos_train
#echo "dfgwefg"
#python download.py ${ANNO_DIR}/${ANNOT_NAME}_val.csv ${DATA_DIR}/videos_val

#source deactivate kinetics
#conda remove -n kinetics --all
