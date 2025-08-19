import inspect
from typing import Dict, Any, Optional, List

import numpy
from PIL import Image
from anyio import AsyncFile

from chroma import FloraImageDAO, FloraTextDAO
from models import Flower


def unique_ids(image_matches):
    ids = []
    seen_ids = set()
    for match in image_matches["metadatas"][0]:
        flora_id = match["flora_id"]
        if flora_id not in seen_ids:
            seen_ids.add(flora_id)
            ids.append(flora_id)
    return ids


def process_results(metadatas: List[Dict[str, str]], ids: List[str], ordered_ids: List[str]) -> List[Flower]:
    flowers = []
    for id in ordered_ids:
        metadata = metadatas[ids.index(id)]
        flower_fields = inspect.signature(Flower).parameters
        flower_dict = {k: v for k, v in metadata.items() if k in flower_fields}
        flowers.append(Flower(**flower_dict))
    return flowers


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
    ) -> List[Flower]:

        if query_img_file:
            image = Image.open(query_img_file)
            numpy_img = numpy.asarray(image)
            image_matches = self.image_dao.query(numpy_img, n, where)
            ordered_ids = unique_ids(image_matches)
            flower_matches = self.text_dao.get(ordered_ids, len(ordered_ids))
            return process_results(flower_matches["metadatas"], flower_matches["ids"], ordered_ids)
        else:

            # WIP: Activate and make this code switchable based on parameter
            # image_matches = FloraBase.query(self.image_dao, query_text, n, where)
            # ordered_ids = unique_ids(image_matches)
            # flower_matches = self.text_dao.get(ordered_ids, len(ordered_ids))
            # return process_results(flower_matches["metadatas"], flower_matches["ids"], ordered_ids)
            text_matches = self.text_dao.query(query_text, n, where)
            return process_results(text_matches["metadatas"][0], text_matches["ids"][0], text_matches["ids"][0])
