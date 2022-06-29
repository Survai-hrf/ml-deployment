import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field
import subprocess
import json
import shutil


# Connecting to fast API
log = logging.getLogger(__name__)
router = APIRouter()

class Data(BaseModel):
    """Use this data model to parse the request body JSON."""
    mux_url: str = Field(..., example='https://stream.mux.com/Ghdtz01zXgvdspi1mD9f1kEu2FkfoGGHlCcs2tiFRGaE/high.mp4')
    video_id: int = Field(..., example=3)


# Returns a prediction to anyone making a request to the API
@router.post('/predict')
async def predict(detections: Data):

    subprocess.call(["python", "src/args.py", f"{detections.mux_url}", f"{detections.video_id}"])
    print("done")

    with open(f'processed/{detections.video_id}.json', 'r') as f:
        final_json = json.load(f)
    
    #clear all temp storage from previous operation
    try:
        shutil.rmtree('temp_videodata_storage')
        shutil.rmtree('processed')
    except:
        pass

    return final_json