#!/usr/bin/env bash

DATASET=$1
CUSTOM_ANNOT_NAME=$2

if [ "$DATASET" == "survai_var_mk1" ]; then
        echo "We are processing $DATASET"
else
        echo "Bad Argument, we only support survai_var_mk1"
        exit 0
fi

#cd ../../../
PYTHONPATH=. python tools/data/build_file_list.py ${DATASET} data/${DATASET}/videos/ --level 2 --format videos --num-split 1 --subset train --shuffle --custom_annot_name $CUSTOM_ANNOT_NAME
echo "Train filelist for video generated."

PYTHONPATH=. python tools/data/build_file_list.py ${DATASET} data/${DATASET}/videos/ --level 2 --format videos --num-split 1 --subset val --shuffle --custom_annot_name $CUSTOM_ANNOT_NAME
echo "Val filelist for video generated."
cd tools/data/$DATASET/
