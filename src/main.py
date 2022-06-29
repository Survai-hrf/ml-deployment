from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src import predict


app = FastAPI(
    title='ServAI Action & Object Recognition',
    description='to be explained later',
    version='0.1',
    docs_url='/',
)

app.include_router(predict.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    uvicorn.run(app)
