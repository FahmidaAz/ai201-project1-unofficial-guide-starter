
"""
ingest.py — Milestone 3: Document Pipeline
Domain: Tech Career Advice
Spec: chunk_size=300 chars, overlap=50 chars
Each chunk returns: text, source, chunk_id
"""

import os
import re
import random
from collections import Counter


# ── 1. LOAD ──────────────────────────────────────────────────────────────────

def load_documents(folder_path):
    """Load all .txt files from a folder. Returns list of {source, raw_text}."""
    documents = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({"source": filename, "raw_text": text})
            print(f"  Loaded: {filename} ({len(text)} chars)")
    print(f"\nTotal documents loaded: {len(documents)}")
    return documents


# ── 2. CLEAN ─────────────────────────────────────────────────────────────────

def clean_document(text):
    """
    Remove HTML tags, boilerplate, and noise. Keep substantive content.

    Remove: HTML tags, HTML entities, URLs, nav/footer boilerplate markers,
            share buttons text, excess whitespace.
    Keep:   Review text, advice, opinions, ratings, course/professor context.
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode common HTML entities
    html_entities = {
        "&amp;": "&", "&nbsp;": " ", "&lt;": "<", "&gt;": ">",
        "&#39;": "'", "&quot;": '"', "&apos;": "'", "&#x27;": "'",
        "&#x2F;": "/", "&mdash;": "—", "&ndash;": "-", "&hellip;": "...",
    }
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove common boilerplate patterns (nav/footer text)
    boilerplate = [
        r"share\s+this\s+post",
        r"read\s+more",
        r"click\s+here",
        r"sign\s+up\s+for",
        r"subscribe\s+to",
        r"cookie\s+policy",
        r"privacy\s+policy",
        r"all\s+rights\s+reserved",
        r"©\s*\d{4}",
        r"\d+\s+comments?",
        r"posted\s+by\s+u/\S+",  # Reddit username lines
    ]
    for pattern in boilerplate:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

    # Collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)           # collapse spaces/tabs
    text = re.sub(r"\n{3,}", "\n\n", text)         # collapse 3+ newlines → 2
    text = text.strip()

    return text


# ── 3. CHUNK ─────────────────────────────────────────────────────────────────

def chunk_document(text, source, chunk_size=300, overlap=50):
    """
    Split cleaned text into overlapping character-level chunks.

    Args:
        text:       Cleaned document text.
        source:     Filename — attached as metadata to every chunk.
        chunk_size: Characters per chunk (default: 300, per planning.md).
        overlap:    Characters of overlap between consecutive chunks (default: 50).

    Returns:
        List of dicts: {chunk_id, source, text}
    """
    chunks = []
    start = 0
    chunk_index = 0
    step = chunk_size - overlap  # how far to advance each iteration

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if len(chunk_text) > 0:  # skip empty chunks
            source_stem = os.path.splitext(source)[0]  # drop .txt extension
            chunks.append({
                "chunk_id": f"{source_stem}_chunk_{chunk_index:03d}",
                "source": source,
                "text": chunk_text,
            })
            chunk_index += 1

        start += step

    return chunks


# ── 4. INSPECT ───────────────────────────────────────────────────────────────

def inspect_chunks(all_chunks, sample_size=5):
    """Print 5 random chunks and run diagnostics."""
    print(f"\n{'='*60}")
    print(f"TOTAL CHUNKS: {len(all_chunks)}")
    print(f"{'='*60}")

    # Chunks per document
    print("\nChunks per document:")
    counts = Counter(c["source"] for c in all_chunks)
    for source, count in sorted(counts.items()):
        print(f"  {source}: {count} chunks")

    # Diagnostics
    empty_chunks = [c for c in all_chunks if len(c["text"].strip()) == 0]
    html_chunks  = [c for c in all_chunks if re.search(r"<[a-z]|&amp;|&nbsp;", c["text"])]
    short_chunks = [c for c in all_chunks if 0 < len(c["text"]) < 50]

    print(f"\nDiagnostics:")
    print(f"  Empty chunks:         {len(empty_chunks)}  {'✓' if len(empty_chunks) == 0 else '✗ PROBLEM — check load_documents()'}")
    print(f"  HTML artifact chunks: {len(html_chunks)}  {'✓' if len(html_chunks) == 0 else '✗ PROBLEM — clean_document() missed some tags'}")
    print(f"  Very short (<50 chr): {len(short_chunks)}  {'✓' if len(short_chunks) == 0 else '⚠ review — these may be fragments'}")

    # Range check
    print(f"\nChunk count check:")
    if len(all_chunks) < 50:
        print("  ⚠ Fewer than 50 chunks — chunks may be too large, or documents didn't load.")
    elif len(all_chunks) > 2000:
        print("  ⚠ More than 2,000 chunks — chunks may be too small.")
    else:
        print(f"  ✓ {len(all_chunks)} chunks — within the 50–2,000 healthy range.")

    # 5 random sample chunks
    print(f"\n{'='*60}")
    print(f"5 RANDOM CHUNKS FOR INSPECTION")
    print(f"{'='*60}")
    sample = random.sample(all_chunks, min(sample_size, len(all_chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"\nChunk {i} | {chunk['chunk_id']}")
        print(f"Source: {chunk['source']}")
        print("-" * 50)
        print(chunk["text"])
        print("-" * 50)

    # Checklist questions
    print("\nASK YOURSELF ABOUT EACH CHUNK:")
    print("  [ ] Does it make sense on its own?")
    print("  [ ] Could someone answer a question from it alone?")
    print("  [ ] No HTML tags or entities?")
    print("  [ ] Does the source metadata match the right file?")


# ── 5. MAIN ──────────────────────────────────────────────────────────────────

def main():
    # ── CONFIGURE THIS ──────────────────────────────────────────────────────
    DOCS_FOLDER = "documents"   # <-- folder containing your 10 .txt files
    CHUNK_SIZE  = 300           # characters, per planning.md
    OVERLAP     = 50            # characters, per planning.md
    # ────────────────────────────────────────────────────────────────────────

    print("STEP 1: Loading documents...")
    documents = load_documents(DOCS_FOLDER)

    if not documents:
        print(f"\nERROR: No .txt files found in '{DOCS_FOLDER}/'")
        print("Make sure your 10 .txt files are in a folder called 'documents'")
        print("next to this script, then re-run.")
        return

    print("\nSTEP 2: Cleaning and chunking...")
    all_chunks = []
    for doc in documents:
        cleaned = clean_document(doc["raw_text"])
        chunks  = chunk_document(cleaned, source=doc["source"],
                                 chunk_size=CHUNK_SIZE, overlap=OVERLAP)
        all_chunks.extend(chunks)
        print(f"  {doc['source']} → {len(chunks)} chunks")

    print("\nSTEP 3: Inspecting output...")
    inspect_chunks(all_chunks)

    print("\n✓ Pipeline complete. Review the chunks above before moving to Milestone 4.")
    print("  If everything looks good: git add ingest.py && git commit -m 'M3: document pipeline'")


if __name__ == "__main__":
    main()