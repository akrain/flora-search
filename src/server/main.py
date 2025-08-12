from typing import Optional

from fastapi import FastAPI, UploadFile, HTTPException

from server import chroma
from server.search import SearchService

app = FastAPI()
app.chromadb_client = chroma.client()
app.search_service = SearchService(app.chromadb_client)


@app.get("/")
def read_root():
    return {"Hello": "World", "And": "we are on..."}


@app.get("/flowers/{id}")
def get_flower(id: int):
    return {"flower_id": id}


@app.post("/flowers/search/")
def search_flowers(q: Optional[str] = None, q_img: Optional[UploadFile] = None):
    validate_search_params(q, q_img)
    results = app.search_service.search(q, q_img)
    return {"q": q, "q_img": q_img.filename if q_img else None, "results": results}


def validate_search_params(q, q_img):
    # Check if at least one parameter is provided and valid
    if not q and not q_img:
        raise HTTPException(status_code=400, detail="Either 'q' (text query) or 'q_img' (image file) must be provided")
    if q_img and q_img.size == 0:
        raise HTTPException(status_code=400, detail="Uploaded image file is empty")
