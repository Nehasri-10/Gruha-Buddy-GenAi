from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import shutil
import uuid
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

HF_TOKEN = "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"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...)):

    unique_name = str(uuid.uuid4())

    image_path = f"static/{unique_name}.jpg"
    depth_path = f"static/depth/{unique_name}.png"

    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    API_URL = "https://api-inference.huggingface.co/models/Intel/dpt-hybrid-midas"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }

    with open(image_path, "rb") as f:
        response = requests.post(API_URL, headers=headers, data=f)

    if response.status_code != 200:
        return HTMLResponse(f"API Error: {response.text}")

    with open(depth_path, "wb") as f:
        f.write(response.content)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "image_url": f"/static/{unique_name}.jpg",
            "depth_url": f"/static/depth/{unique_name}.png"
        }
    )