from pathlib import Path

import chromadb

CHROMA_DB_DIR = Path(__file__).parent.parent / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
collection = client.get_collection("clinic_documents")


def search(query: str, n_results: int = 3) -> list[dict]:
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    chunks = []
    for text, metadata in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({"text": text, "source": metadata["source"]})

    return chunks


if __name__ == "__main__":
    test_results = search("How long would take root canal treatment??")
    for r in test_results:
        print(f"[{r['source']}] {r['text']}\n")