from typing import List, Dict, Any, Optional

import chromadb
from chromadb import ClientAPI, EmbeddingFunction
from chromadb.config import Settings
from chromadb.utils.data_loaders import ImageLoader
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction, DefaultEmbeddingFunction

_chromadb_client = None


def client(persistent: bool = True, path="chroma") -> ClientAPI:
    global _chromadb_client
    if _chromadb_client is None:
        if persistent:
            _chromadb_client = chromadb.PersistentClient(settings=Settings(), path=path)
        else:
            _chromadb_client = chromadb.Client(settings=Settings())
    return _chromadb_client


class FloraBase:
    def __init__(self, collection_name, chromadb_client,
                 embedding_function: EmbeddingFunction,
                 data_loader=None):
        self.collection_name = collection_name
        self.client = chromadb_client
        self.collection = self.client.get_or_create_collection(
            self.collection_name,
            embedding_function=embedding_function,
            data_loader=data_loader
        )

    def delete_collection(self) -> None:
        self.client.delete_collection(name=self.collection_name)

    def get_collection_count(self) -> int:
        return self.collection.count()

    def query(
            self,
            query_text: str,
            n_results: int = 5,
            where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where,
        )
        return results

    def get(
            self,
            ids: list = None,
            limit: int = 10,
            offset: int = 0,
            where: Optional[Dict[str, Any]] = None,
            where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        results = self.collection.get(
            ids=ids,
            limit=limit,
            offset=offset,
            where=where,
            where_document=where_document,
        )
        return results


class FloraTextDAO(FloraBase):
    """Class to interact with collection that stores Flower text and text embeddings"""

    def __init__(self, chromadb_client):
        super().__init__("flora_text", chromadb_client, embedding_function=OpenCLIPEmbeddingFunction())

    def add_document(
            self,
            document_id: str,
            document: str,
            metadata: Dict[str, Any]
    ) -> None:
        self.collection.add(
            ids=[document_id],
            documents=[document],
            metadatas=[metadata]
        )


class FloraImageDAO(FloraBase):
    """Interacts with collection that stores Flower image urls and image embeddings"""

    def __init__(self, chromadb_client):
        super().__init__("flora_images", chromadb_client, embedding_function=OpenCLIPEmbeddingFunction(),
                         data_loader=ImageLoader())

    def add_document(
            self,
            document_id: str,
            uri: str,
            metadata: Dict[str, Any]
    ) -> None:
        self.collection.add(
            ids=[document_id],
            uris=[uri],
            metadatas=[metadata]
        )

    def add_documents_batch(
            self,
            document_ids: List[str],
            uris: List[str],
            metadata_list: List[Dict[str, Any]]

    ) -> None:
        """Add multiple documents to the ChromaDB collection"""

        self.collection.add(
            ids=document_ids,
            uris=uris,
            metadatas=metadata_list
        )

    def query(
            self,
            query_img: list,
            n_results: int = 5,
            where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        results = self.collection.query(
            query_images=[query_img],
            n_results=n_results,
            where=where,
            include=["metadatas", "uris"]
        )
        return results


class FloraTextOnlyDAO(FloraBase):
    """Class to interact with collection that stores Flower text and text embeddings"""

    def __init__(self, chromadb_client):
        super().__init__("flora_text_only", chromadb_client, embedding_function=DefaultEmbeddingFunction())

    def add_document(
            self,
            document_id: str,
            document: str,
            metadata: Dict[str, Any]
    ) -> None:
        self.collection.add(
            ids=[document_id],
            documents=[document],
            metadatas=[metadata]
        )
