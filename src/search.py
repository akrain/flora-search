from typing import Dict, Any, Optional

import numpy
from PIL import Image

from chroma import FloraImageDAO, FloraTextOnlyDAO


class SearchService:
    def __init__(self, chromadb_client):
        self.image_dao = FloraImageDAO(chromadb_client)
        # Use the same collection that import currently writes to
        self.text_dao = FloraTextOnlyDAO(chromadb_client)

    def search(
            self,
            query_text: Optional[str],
            query_img: Optional[bytes],
            n: int = 20,
            where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        if query_img:
            numpy_img = numpy.asarray(Image.open(query_img))
            image_matches = self.image_dao.query(numpy_img, n, where)
            ids = [match["flora_id"] for match in image_matches["metadatas"][0]]
            flowers = self.text_dao.get(ids)
            return flowers
        else:
            text_matches = self.text_dao.query(query_text, n, where)
            return text_matches
