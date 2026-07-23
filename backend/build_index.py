from pathlib import Path

import chromadb

DOCUMENTS_DIR = Path(__file__).parent.parent / "documents"
CHROMA_DB_DIR = Path(__file__).parent.parent / "chroma_db"


def load_and_chunk_documents() -> list[dict]:

    chunks = []
    for file_path in DOCUMENTS_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        for i, paragraph in enumerate(paragraphs):
            chunks.append({
                "id": f"{file_path.stem}-{i}",
                "text": paragraph,
                "source": file_path.name,
            })
    return chunks


def build_index():
    chunks = load_and_chunk_documents()
    print(f"{len(chunks)} Chunk found.")

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_or_create_collection("clinic_documents")

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"source": c["source"]} for c in chunks],
    )
    print(f"Index created: {CHROMA_DB_DIR}")


if __name__ == "__main__":
    build_index()