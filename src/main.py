import io
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Form, File, UploadFile

import chroma
from search import SearchService

app = FastAPI()
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
    if q_img:
        file_content = q_img.file.read()
        file_bytes = io.BytesIO(file_content)
    results = app.search_service.search(q, file_bytes)
    return {"q": q, "q_img": q_img.filename if q_img else None, "results": results}


def validate_search_params(q, q_img):
    # Check if at least one parameter is provided and valid
    if not q and not q_img:
        raise HTTPException(
            status_code=400,
            detail="Either 'q' (text query) or 'q_img' (image file) must be provided",
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
