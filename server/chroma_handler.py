from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
# from openai import OpenAI
import os


class ChromaDBHandler:
    """Handler for ChromaDB operations with OpenAI embeddings."""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "flora_collection"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings()
        )
        # self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get or create a ChromaDB collection."""
        try:
            return self.client.get_collection(name=self.collection_name)
        except ValueError:
            return self.client.create_collection(name=self.collection_name)
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI's text-embedding-ada-002 model."""
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    
    def add_document(
        self,
        document_id: str,
        text: str,
        metadata: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ) -> None:
        """Add a document to the ChromaDB collection."""
        if embedding is None:
            embedding = self._generate_embedding(text)
        
        self.collection.add(
            ids=[document_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    
    def add_documents_batch(
        self,
        document_ids: List[str],
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """Add multiple documents to the ChromaDB collection in batch."""
        if embeddings is None:
            embeddings = [self._generate_embedding(text) for text in texts]
        
        self.collection.add(
            ids=document_ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
    
    def query(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query the ChromaDB collection."""
        query_embedding = self._generate_embedding(query_text)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        
        return results
    
    def delete_collection(self) -> None:
        """Delete the ChromaDB collection."""
        self.client.delete_collection(name=self.collection_name)
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.collection.count()