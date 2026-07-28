from chroma_client import get_collection

collection = get_collection()


def search(query: str, n_results: int = 3) -> list[dict]:
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    chunks = []
    for text, metadata, distance in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        chunks.append({
            "text": text,
            "source": metadata["source"],
            "distance": distance,
        })

    return chunks


if __name__ == "__main__":
    print("--- Relevant query ---")
    for r in search("how long does a root canal take?"):
        print(f"{r['distance']:.4f}  [{r['source']}]  {r['text'][:60]}...")

    print("\n--- Irrelevant query ---")
    for r in search("what is the capital of France?"):
        print(f"{r['distance']:.4f}  [{r['source']}]  {r['text'][:60]}...")