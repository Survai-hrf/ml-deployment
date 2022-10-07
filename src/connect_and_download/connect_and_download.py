import boto3
import urllib.request
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

REGION_NAME = os.getenv('REGION_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
QUEUE_URL = os.getenv('QUEUE_URL')

def connect_and_download(folder):
    # recieve sqs message

    # if not using folders, download video from mux
    if folder == '':    
        try:
            sqs = boto3.client('sqs', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            queue_url = QUEUE_URL

            # Receive message from SQS queue
            response = sqs.receive_message(
                QueueUrl=queue_url,
                AttributeNames=[
                    'SentTimestamp'
                ],
                MaxNumberOfMessages=1,
                MessageAttributeNames=[
                    'All'
                ],
                VisibilityTimeout=10,
                WaitTimeSeconds=20
            )
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

            data = eval(message['Body'])
            video_id = data['video_id']
            mux_url = data['mux_url']

            urllib.request.urlretrieve(f"{mux_url}?download={video_id}.mp4", f'temp_videodata_storage/{video_id}.mp4') 
            print('downloading complete')
            resp=1

        except Exception as e:
            video_id='failure'
            resp=0
            print(f"FAILURE: {e}")

        return video_id, resp

    else:
        video_id = ''
        resp = 1
        return video_id, resp