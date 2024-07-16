import nest_asyncio
import uvicorn
import secrets
from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image as PILImage
from pyngrok import ngrok
from pydantic import BaseModel
from typing import List, Tuple, Dict, Any

# Copy paste https://github.com/sibas-lab/segmentation-model/blob/90ec79852720da8bd49fcfcb62b3acf55a96d07c/xbd/inference.py

ngrok.set_auth_token(userdata.get('NGROK_AUTH_TOKEN'))

class HealthResult(BaseModel):
  isAlive: bool

class PredictionResponse(BaseModel):
  status: str
  message: str
  instance_detected: int
  instances: list[Instance]

app = FastAPI()

app.mount("/static", StaticFiles(directory="/content/result_img"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/health")
async def get_health() -> HealthResult:
    return HealthResult(isAlive=True)

ngrok_tunnel = ngrok.connect(8000)
print('공용 URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)

# ngrok.kill()