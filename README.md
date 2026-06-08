# The Unofficial Guide — Project 1

---

## Domain

This system covers **Tech Career Advice** — practical knowledge about coding interview preparation, resume writing, salary negotiation, job searching, referrals, and bootcamp reviews. This knowledge is valuable because it reflects real-world experience from engineers who have gone through hiring processes, not official company documentation. It is hard to find through official channels because it lives scattered across Reddit threads, personal blogs, and community forums rather than any single authoritative source. A recruiter's job description tells you what skills to list; a Reddit post from someone who just passed a Google loop tells you how many LeetCode problems you actually need and what the interviewer cared about. This system makes that distributed, informal knowledge queryable in one place.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | r/cscareerquestions wiki | Reddit wiki | reddit.com/r/cscareerquestions/wiki |
| 2 | interviewing.io blog — interview prep | Blog post | interviewing.io/blog |
| 3 | levels.fyi blog — salary negotiation | Blog post | levels.fyi/blog |
| 4 | Course Report — CodePath bootcamp review | Review site | coursereport.com/schools/codepath |
| 5 | GitHub — system-design-primer | README / guide | github.com/donnemartin/system-design-primer |
| 6 | r/cscareerquestions — how to get a referral | Reddit post | reddit.com/r/cscareerquestions |
| 7 | LinkedIn official blog — profile optimization | Blog post | linkedin.com/blog |
| 8 | Blind app blog — Big Tech vs Startup | Blog post | teamblind.com/blog |
| 9 | interviewing.io — what to do after rejection | Blog post | interviewing.io/blog |
| 10 | r/learnprogramming wiki — beginner to first tech job | Reddit wiki | reddit.com/r/learnprogramming/wiki |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** Tech career advice is typically written as short, dense tips and bullet points rather than long continuous prose. A 300-character window captures roughly one complete tip or advice point, which is the unit of information a user is likely to query for. An overlap of 50 characters ensures that advice spanning two consecutive chunks — for example, a rule followed by its exception — remains retrievable intact. Before chunking, each document was cleaned to remove HTML tags, HTML entities (`&amp;`, `&nbsp;`), URLs, and boilerplate navigation text, keeping only the substantive advice content.

**Final chunk count:** 134 chunks across 10 documents (average ~13 chunks per document).

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`. This model runs fully locally with no API key and no rate limits, produces 384-dimensional normalized vectors, and is fast enough to embed 134 chunks in under 5 seconds on a standard laptop. ChromaDB was configured with cosine distance (`metadata={"hnsw:space": "cosine"}`) to match how the model was trained to measure semantic similarity.

**Production tradeoff reflection:** In a real deployment I would weigh several tradeoffs. OpenAI's `text-embedding-3-small` achieves higher accuracy on domain-specific text but costs money per token and requires sending user queries to an external API, which raises privacy concerns. For a multilingual audience — for example, international students asking career questions — a model like `multilingual-e5-base` would be necessary since `all-MiniLM-L6-v2` was trained primarily on English text. For longer documents such as full salary guides or multi-page Reddit threads, a model with a larger context window (like `text-embedding-3-large` with its 8,191-token limit) would reduce the need for aggressive chunking and preserve more document structure per embedding. Latency also matters at scale: a locally hosted model adds no network round-trip, while API-hosted models add ~100–300ms per query.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt enforces grounding with explicit rules rather than soft suggestions:

```
You are a tech career advisor that answers questions strictly from provided documents.

Rules you must follow without exception:
1. Answer ONLY using information explicitly present in the context documents below.
2. If the context does not contain enough information to answer the question, respond
   with exactly: "I don't have enough information in my documents to answer that."
3. Do NOT draw on your general training knowledge. Do NOT fill gaps with
   plausible-sounding information.
4. Be specific and cite details from the text — vague general advice is a grounding failure.
5. Do NOT mention sources in your answer — they are added separately.
```

The user message passes the retrieved chunks formatted as labeled context blocks (`[Source: filename.txt]` followed by chunk text), separated by `---` dividers, then the question. Temperature is set to 0.2 to minimize creative generation.

**How source attribution is surfaced in the response:** Source filenames are extracted programmatically from chunk metadata after generation — `sources = list(dict.fromkeys(c["source"] for c in chunks))` — and displayed in a separate "Retrieved from" panel in the Gradio interface. The LLM is explicitly instructed not to mention sources in its answer, so attribution is always structurally guaranteed and never left to the model to add on its own.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What should I put on my resume if I have no experience? | Include projects, GitHub links, and relevant coursework | List Education, Technical Skills, Projects (2-3 with descriptions), optional Certifications; keep it one page with projects front and center. Sources: `resume_tips.txt`, `beginner_first_job.txt` | Relevant | Accurate |
| 2 | How do I negotiate a higher salary offer? | Have a competing offer or market data, respond by email not phone | Use a competing offer script; negotiate via email for a paper trail; consider signing bonus, RSU grant size, vesting schedule, remote flexibility, and title/level. Source: `salary_negotiation.txt` | Relevant | Accurate |
| 3 | How many LeetCode problems do I need to solve before interviews? | Around 100-150 focusing on patterns not memorization | "Aim for 30-50 Easy problems before applying for technical interviews." Sources: `interview_prep.txt`, `beginner_first_job.txt` | Partially relevant | Partially accurate |
| 4 | Is a coding bootcamp worth it for getting a tech job? | Depends on quality — CodePath and top bootcamps have good placement | Depends on the bootcamp and your effort; top bootcamps have strong placement; "Don't expect the bootcamp to get you a job — expect it to give you the skills to get yourself a job." Sources: `bootcamp_reviews.txt` | Relevant | Accurate |
| 5 | How do I get a referral at a big tech company? | Connect on LinkedIn, ask former classmates, be specific about the role | Search LinkedIn for alumni using "[Company] [Your School]", connect first, be specific about the role, send your resume and job link; any employee can submit a referral. Source: `getting_referral.txt` | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** "How many LeetCode problems do I need to solve before interviews?"

**What the system returned:** "Aim for 30-50 Easy problems before applying for technical interviews." — a lower, beginner-level benchmark. The expected answer was 100-150 problems with an emphasis on pattern recognition over memorization.

**Root cause (tied to a specific pipeline stage):** The failure originates in the **chunking stage**. The source document (`interview_prep.txt`) contained multiple preparation benchmarks in a single section — "30-50 Easy problems before applying" as an entry-level threshold and "100-150 problems focusing on patterns" as a general readiness target. The character-level splitter at 300 characters divided this section across two chunk boundaries without regard for paragraph or idea structure. The chunk containing the 30-50 figure had cleaner surrounding context (the sentence was complete within the chunk), while the 100-150 figure landed mid-chunk surrounded by text about practice methodology rather than raw counts. When the query "how many LeetCode problems" was embedded, the retrieval returned the chunk whose semantic neighborhood better matched a beginner-level threshold concept — not the one with the more complete answer.

**What you would change to fix it:** Increase chunk size to 500–600 characters to keep more of a document section together, or switch to paragraph-aware splitting (split on double newlines first, then by character count only if a paragraph exceeds the limit). Either approach would reduce the chance that related advice — multiple benchmarks in the same section — gets separated into different chunks where only one is retrieved.

---

## Spec Reflection

**One way the spec helped you during implementation:** The Chunking Strategy section of `planning.md` — written before any pipeline code — specified 300-character chunks with 50-character overlap and explained the reasoning (tech career advice is written in short, dense tips). This gave a concrete, verifiable target to implement against. Instead of guessing at chunk size and iterating based on intuition, I had a clear definition of done: sample chunks should read as complete tips, and the total count should fall between 50 and 2,000. When the pipeline produced 134 chunks and the samples looked like complete advice points, I could confidently call the stage finished rather than continuing to tweak.

**One way your implementation diverged from the spec, and why:** The `planning.md` did not specify a distance metric for ChromaDB — it only said to use ChromaDB. During implementation, the default L2 (Euclidean) distance metric produced scores between 0.7 and 1.1 for all results, which made every retrieval result appear as a "poor match" even when the returned chunks were topically correct and came from the right source files. I switched to cosine distance by adding `metadata={"hnsw:space": "cosine"}` to the `create_collection` call. This change was necessary because `all-MiniLM-L6-v2` produces normalized vectors, and cosine distance is the correct metric for measuring the angle between normalized embeddings — which is what semantic similarity actually represents. After the change, top results scored below 0.5 and the quality flags became meaningful.

---

## AI Usage

**Instance 1**
- *What I gave the AI:* My Documents table and Chunking Strategy section from `planning.md`, along with the requirement that each chunk return `text`, `source`, and `chunk_id`.
- *What it produced:* A complete `ingest.py` with `load_documents()`, `clean_document()`, and `chunk_document()` using character-level splitting at chunk_size=300 and overlap=50, plus a diagnostics block that printed chunk counts per document and flagged empty chunks and HTML artifacts.
- *What I changed or overrode:* I added a `len(chunk) > 0` filter to `chunk_document()` after the diagnostics reported 1 very-short chunk that slipped through. I also reviewed the `clean_document()` regex patterns against an actual raw document printout and confirmed the boilerplate patterns matched my specific files before trusting the output.

**Instance 2**
- *What I gave the AI:* The retrieval output from `embed.py` showing all results flagged as `✗ poor` with distances of 0.7–1.1, and my observation that the retrieved content was topically correct (salary queries returning salary documents) despite the poor flags.
- *What it produced:* An explanation that ChromaDB defaults to L2 (Euclidean) distance with a range of 0–√2 ≈ 1.414 rather than cosine distance with a range of 0–1, and that my quality thresholds were calibrated for cosine distance. It also explained the mathematical relationship between the two metrics for normalized vectors and provided the one-line fix: `metadata={"hnsw:space": "cosine"}` in `create_collection`.
- *What I changed or overrode:* I verified the explanation by checking that a distance of 0.719 in L2 corresponds to a cosine similarity of approximately 0.74 before applying the fix. After re-running with cosine distance, top results scored 0.37–0.45 and the quality flags matched what I could see in the content.
