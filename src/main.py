from dataclasses import asdict
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import chroma
from search import SearchService

MAX_IMG_SIZE = 4 * 1024 * 1024

app = FastAPI()

# Enable CORS for local development and simple personal usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.chromadb_client = chroma.client()
app.search_service = SearchService(app.chromadb_client)

form_default = Form(default=None)
file_default = File(default=None)


@app.get("/")
def read_root():
    return {"Hello": "World", "And": "we are on..."}


@app.get("/flowers/{id}")
def get_flower(id: int):
    return {"flower_id": id}


@app.post("/flowers/search/")
def search_flowers(
        q: Optional[str] = form_default,
        q_img: Optional[UploadFile] = file_default,
):
    validate_search_params(q, q_img)
    try:
        results = app.search_service.search(q, q_img.file if q_img else None)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Search failed")
    finally:
        q_img.file.close() if q_img else None

    # Return dataclass payloads as plain dicts
    items = [asdict(f) for f in results]
    return {"q": q, "q_img": q_img.filename if q_img else None, "items": items}


def validate_file_properties(q_img: UploadFile):
    # Enforce 2MB max upload size for images
    if q_img is not None and q_img.file is not None:
        if q_img.size > MAX_IMG_SIZE:
            raise HTTPException(status_code=413, detail="Image must be 4MB or smaller")
        if q_img.content_type not in ("image/jpeg", "image/png"):
            print(q_img.content_type)
            raise HTTPException(status_code=415, detail="Image must be a JPEG or PNG file")


def validate_search_params(q: str, q_img: UploadFile):
    # Check if at least one parameter is provided and valid
    if not q and not q_img:
        raise HTTPException(
            status_code=400,
            detail="Either 'q' (text query) or 'q_img' (image file) must be provided",
        )
    validate_file_properties(q_img)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
