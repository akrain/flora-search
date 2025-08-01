from typing import List, Dict, Any, Optional
import chromadb
from chromadb import ClientAPI
from chromadb.api import DataLoader
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction

_chromadb_client = None


def client(persistent: bool = True) -> ClientAPI:
    global _chromadb_client
    if _chromadb_client is None:
        if persistent:
            _chromadb_client = chromadb.PersistentClient(settings=Settings())
        else:
            _chromadb_client = chromadb.Client(settings=Settings())
    return _chromadb_client


class FloraBase:
    def __init__(self, collection_name, chromadb_client, data_loader=None):
        self.collection_name = collection_name
        self.client = chromadb_client
        self.collection = self.client.get_or_create_collection(
            self.collection_name,
            embeddding_function=OpenCLIPEmbeddingFunction(),
            data_loader=data_loader
        )

    def delete_collection(self) -> None:
        self.client.delete_collection(name=self.collection_name)

    def get_collection_count(self) -> int:
        return self.collection.count()


class FloraTextDAO(FloraBase):
    """Class to interact with collection that stores Flower text and text embeddings"""

    def __init__(self, chromadb_client):
        super().__init__("flora_collection", chromadb_client)

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

    def query(
            self,
            query_text: str,
            n_results: int = 5,
            where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        results = self.collection.query(
            query_text=query_text,
            n_results=n_results,
            where=where
        )
        return results


class FloraImageDAO(FloraBase):
    """Interacts with collection that stores Flower image urls and image embeddings"""

    def __init__(self, chromadb_client):
        super().__init__("flora_img_collection", chromadb_client, DataLoader())

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
            query_text: str,
            n_results: int = 5,
            where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        results = self.collection.query(
            query_text=query_text,
            n_results=n_results,
            where=where
        )
        return results
