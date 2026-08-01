from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from config import CHROMA_MODE, CHROMA_HOST, CHROMA_PORT

CHROMA_DB_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "clinic_documents"

# Multilingual model so queries in Russian/Turkish/Georgian still match the
# (English-only) document chunks during retrieval.
_embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

def get_collection():
    if CHROMA_MODE == "http":
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    else: client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

    return client.get_or_create_collection(COLLECTION_NAME, embedding_function=_embedding_function)