from pathlib import Path

import chromadb

from config import CHROMA_MODE, CHROMA_HOST, CHROMA_PORT

CHROMA_DB_DIR = Path(__file__).parent.parent / "chroma_db"
COLLECTION_NAME = "clinic_documents"


def get_collection():
    if CHROMA_MODE == "http":
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    else:
        client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

    return client.get_or_create_collection(COLLECTION_NAME)