"""
embed.py — Milestone 4: Embed Chunks + Test Retrieval
Model:  all-MiniLM-L6-v2 (sentence-transformers, runs locally, no API key)
Store:  ChromaDB persistent (saved to ./chroma_db/)
Top-k:  5, per planning.md
"""

from sentence_transformers import SentenceTransformer
import chromadb
from ingest import load_documents, clean_document, chunk_document

# ── CONFIG ───────────────────────────────────────────────────────────────────
DOCS_FOLDER = "documents"
CHROMA_PATH = "./chroma_db"        # folder ChromaDB writes to disk
COLLECTION  = "tech_career_advice"
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE  = 300
OVERLAP     = 50
TOP_K       = 5


# ── 1. LOAD + CHUNK ──────────────────────────────────────────────────────────

def build_chunks():
    """Re-use ingest.py pipeline to produce all chunks."""
    documents = load_documents(DOCS_FOLDER)
    all_chunks = []
    for doc in documents:
        cleaned = clean_document(doc["raw_text"])
        chunks  = chunk_document(cleaned, source=doc["source"],
                                 chunk_size=CHUNK_SIZE, overlap=OVERLAP)
        all_chunks.extend(chunks)
    print(f"Total chunks ready to embed: {len(all_chunks)}")
    return all_chunks


# ── 2. EMBED + STORE ─────────────────────────────────────────────────────────

def embed_and_store(chunks):
    """
    Embed every chunk with all-MiniLM-L6-v2 and persist in ChromaDB.

    Each chunk is stored with:
        - id:        unique chunk_id from ingest.py
        - embedding: 384-dim float vector
        - document:  the raw chunk text (ChromaDB calls this 'document')
        - metadata:  {source, chunk_id} — used for attribution in Milestone 5
    """
    print(f"\nLoading model: {EMBED_MODEL} (first run downloads ~90 MB) ...")
    model = SentenceTransformer(EMBED_MODEL)

    print("Embedding all chunks — this takes ~10-30 seconds ...")
    texts      = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)

    print(f"\nConnecting to ChromaDB at '{CHROMA_PATH}' ...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Safe re-run: delete old collection so we don't get duplicate-id errors
    try:
        client.delete_collection(COLLECTION)
        print("Old collection deleted — rebuilding fresh.")
    except Exception:
        pass

    collection = client.create_collection(
    name=COLLECTION,
    metadata={"hnsw:space": "cosine"}
)

    print("Storing chunks ...")
    collection.add(
        ids        = [c["chunk_id"] for c in chunks],
        embeddings = embeddings.tolist(),
        documents  = texts,
        metadatas  = [{"source": c["source"], "chunk_id": c["chunk_id"]}
                      for c in chunks],
    )

    print(f"✓ {collection.count()} chunks stored in collection '{COLLECTION}'")
    return collection, model


# ── 3. RETRIEVE ──────────────────────────────────────────────────────────────

def retrieve(query, collection, model, k=TOP_K):
    """
    Embed the query and return the top-k closest chunks.

    Returns a ChromaDB result dict with keys:
        documents, metadatas, distances  (each is a list-of-lists)
    Distance = cosine distance (lower = more similar).
    """
    query_embedding = model.encode([query]).tolist()
    return collection.query(
        query_embeddings = query_embedding,
        n_results        = k,
        include          = ["documents", "metadatas", "distances"],
    )


def print_results(query, results):
    """Pretty-print retrieval results with distance flags."""
    docs      = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")

    for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances), 1):
        if dist < 0.5:
            flag = "✓ strong"
        elif dist < 0.7:
            flag = "⚠ weak  "
        else:
            flag = "✗ poor  "

        print(f"\nResult {i} | {flag} | distance: {dist:.3f} | {meta['source']}")
        print("-" * 50)
        print(doc)
        print("-" * 50)


# ── 4. TEST QUERIES ──────────────────────────────────────────────────────────
# These are 3 of your 5 evaluation-plan questions from planning.md

TEST_QUERIES = [
    "What should I put on my resume if I have no experience?",
    "How do I negotiate a higher salary offer?",
    "How many LeetCode problems do I need to solve before interviews?",
]


# ── 5. MAIN ──────────────────────────────────────────────────────────────────

def main():
    print("STEP 1: Building chunks ...")
    chunks = build_chunks()

    print("\nSTEP 2: Embedding + storing in ChromaDB ...")
    collection, model = embed_and_store(chunks)

    print("\nSTEP 3: Testing retrieval with 3 evaluation queries ...")
    for query in TEST_QUERIES:
        results = retrieve(query, collection, model)
        print_results(query, results)

    print("\n" + "="*60)
    print("DISTANCE SCORE GUIDE:")
    print("  ✓  < 0.5  — strong match, good retrieval")
    print("  ⚠  0.5–0.7 — weak match, chunks may be too small")
    print("  ✗  > 0.7  — poor match, debug before Milestone 5")
    print("="*60)
    print("\nIf top results look relevant, you're ready to commit:")
    print("  git add embed.py")
    print("  git commit -m 'M4: embed + retrieval — ChromaDB, all-MiniLM-L6-v2'")


if __name__ == "__main__":
    main()