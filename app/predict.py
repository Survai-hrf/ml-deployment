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
    mux_url: str = Field(..., example='to be filled')
    video_id: int = Field(..., example=3)


# Returns a prediction to anyone making a request to the API
@router.post('/predict')
async def predict(detections: Data):

    subprocess.call([f"python args.py --mux_url {detections.mux_url} --video_id {detections.video_id}"])

    with open(f'{detections.video_id}.json') as f:
        final_json = json.load(f)
    
    shutil.rmtree('processed')
    
    return final_json