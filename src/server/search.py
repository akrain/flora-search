from typing import Dict, Any, Optional

import numpy
from PIL import Image
from fastapi import UploadFile

from server.chroma import FloraTextDAO, FloraImageDAO


class SearchService:
    def __init__(self, chromadb_client):
        self.image_dao = FloraImageDAO(chromadb_client)
        self.text_dao = FloraTextDAO(chromadb_client)

    def search(
            self,
            query_text: str,
            query_img: UploadFile,
            n: int = 20,
            where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        if query_img:
            numpy_img = numpy.asarray(Image.open(query_img))
            images = self.image_dao.query(numpy_img, n, where)
        else:
            images = self.image_dao.query(query_text, n, where)

        ids = []
        for match in images["metadatas"][0]:
            ids.append(match["flora_id"])
        flowers = self.text_dao.get(ids)
        return flowers
