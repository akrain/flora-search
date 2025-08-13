from typing import Dict, Any, Optional

import numpy
from PIL import Image
from anyio import AsyncFile

from chroma import FloraImageDAO, FloraTextDAO


class SearchService:
    def __init__(self, chromadb_client):
        self.image_dao = FloraImageDAO(chromadb_client)
        # Use the same collection that import currently writes to
        self.text_dao = FloraTextDAO(chromadb_client)

    def search(
            self,
            query_text: Optional[str],
            query_img_file: AsyncFile,
            n: int = 20,
            where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        if query_img_file:
            image = Image.open(query_img_file)
            numpy_img = numpy.asarray(image)
            image_matches = self.image_dao.query(numpy_img, n, where)
            ids = [match["flora_id"] for match in image_matches["metadatas"][0]]
            ids = list(set(ids))
            print(image_matches)
            flowers = self.text_dao.get(ids)

            return flowers
        else:
            text_matches = self.text_dao.query(query_text, n, where)
            return text_matches
