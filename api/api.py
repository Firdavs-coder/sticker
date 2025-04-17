from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

import shutil, uuid, uvicorn, sys

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from main import StickerMaker


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/create-sticker")
async def create_sticker(image: UploadFile = File(...)):
    temp_file = UPLOAD_DIR / f"{uuid.uuid4()}.png"
    output_file = temp_file.with_suffix(".png")

    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    StickerMaker(
        crop=False,
        alpha_threshold=200,
        border_size=10,
        shadow_blur_strength=5,
        bg_transparent=True,
    ).process(
        input_path=temp_file,
        output_path=output_file
    )
    
    with open(output_file, "rb") as file:
        content = file.read()
        
    temp_file.unlink(missing_ok=True)
    output_file.unlink(missing_ok=True)
        
    return StreamingResponse(
        content=iter([content]),
        media_type="image/png",
    )

@app.get("/")
async def root(request: Request):
    templates = Jinja2Templates(directory="templates")

    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)