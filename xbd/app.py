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

@app.post("/predict", response_model=PredictionResponse)
async def create_prediction(file: UploadFile | None = None) -> Any:
  if not file:
    raise HTTPException(status_code=404, detail="No file uploaded")

  if not file.content_type.startswith("image"):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="이미지 파일만 업로드 가능합니다.",
    )

  if file.filename.split(".")[-1].lower() not in ["png"]:
    raise HTTPException(
        status.HTTP_400_BAD_REQUEST,
        detail="업로드 불가능한 이미지 확장자입니다."
    )

  random_name = secrets.token_urlsafe(16)
  file.filename = f"{random_name}.png"
  image = PILImage.open(file.file)

  image.save(f"/content/{file.filename}", "png")
  result = prediction(f"/content/{file.filename}")

  return {
      "status": "success",
      "message": "추론 성공",
      "instance_detected": len(result),
      "instances": result
    }

ngrok_tunnel = ngrok.connect(8000)
print('공용 URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
uvicorn.run(app, port=8000)

# ngrok.kill()