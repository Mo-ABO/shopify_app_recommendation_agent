from langchain.chains.base import Chain
from typing import Any, Dict, ClassVar
from pydantic import PrivateAttr
from langchain.embeddings import OpenAIEmbeddings
import chromadb
from config import settings as s
import os

os.environ["OPENAI_API_KEY"] = s.openai_api_key
    
class RetrievalChain(Chain):
    """custom chain that retrieves raw context from Chroma DB using a query."""
    input_keys: ClassVar[list[str]] = ["query"]
    output_keys: ClassVar[list[str]] = ["raw_context"]

    _db_path: str = PrivateAttr()
    _collection_name: str = PrivateAttr()
    _k: int = PrivateAttr()

    def __init__(self, db_path: str, collection_name: str = "shopify_apps", k: int = 3, **kwargs: Any):
        super().__init__(**kwargs)
        self._db_path = db_path
        self._collection_name = collection_name
        self._k = k

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs["query"]
        raw_context = self.retrieve_context(query, db_path=self._db_path, collection_name=self._collection_name, k=self._k)
        return {"raw_context": raw_context}

    @property
    def _chain_type(self) -> str:
        return "retrieval_chain"
    
    def retrieve_semantic_context(self, query: str, collection, k: int = 3, distance_threshold: float = 0.3) -> str:
        embeddings = OpenAIEmbeddings()
        query_embedding = embeddings.embed_query(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=k, include=["documents", "metadatas", "distances"])

        distances = results.get("distances", [])

        if distances and distances[0] and min(distances[0]) > distance_threshold:
            return ""

        context_parts = []
        for docs in results.get("documents", []):
            if docs:
                context_parts.append(docs[0])

        context = "\n".join(context_parts)
        return context

    def retrieve_keyword_context(self, query: str, collection) -> str:
        all_data = collection.get(include=["documents", "metadatas"])
        query_words = set(query.lower().split())
        
        keyword_context_parts = []
        for docs, metadata in zip(all_data.get("documents", []), all_data.get("metadatas", [])):
            if docs:
                text = docs[0]

                if metadata and "categories" in metadata:
                    cat_words = set(word.strip().lower() for word in metadata["categories"].split(","))

                    if query_words.intersection(cat_words):
                        keyword_context_parts.append(text)

        context = "\n".join(keyword_context_parts)
        return context
    
    def retrieve_context(self, query: str, db_path: str, collection_name: str = "shopify_apps", k: int = 3, hybrid: bool = True) -> str:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(name=collection_name)
        
        # semantic search
        semantic_context = self.retrieve_semantic_context(query, collection, k)
        if semantic_context == "":
            return ""
        
        if not hybrid:
            return semantic_context.strip()
        
        # keyword search
        keyword_context = self.retrieve_keyword_context(query, collection)

        combined_context = semantic_context + "\n" + keyword_context
        return combined_context.strip()