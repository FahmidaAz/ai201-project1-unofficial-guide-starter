# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Tech Career Advice — The Unofficial Guide

This domain covers practical tech career knowledge including coding interview 
preparation, resume tips, salary negotiation, job searching, and bootcamp 
reviews. This knowledge is valuable but hard to find officially — it lives 
scattered across Reddit threads, blogs, and forums rather than any single 
authoritative source.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |r/cscareerquestions wiki |Resume tips & interview advice |reddit.com/r/cscareerquestions/wiki |
| 2 |Interviewing.io blog |Technical interview preparation |interviewing.io/blog |
| 3 |levels.fyi blog |Salary negotiation guide |levels.fyi/blog |
| 4 |Course Report |CodePath bootcamp review |coursereport.com/schools/codepath |
| 5 |GitHub — coding interview |System design prep guide |github.com/donnemartin/system-design-primer |
| 6 |r/cscareerquestions |How to get a referral post |reddit.com/r/cscareerquestions |
| 7 |LinkedIn official blog |LinkedIn profile optimization tips |linkedin.com/blog |
| 8 |Blind app blog |Big Tech vs Startup comparison |teamblind.com/blog |
| 9 |interviewing.io |What to do after rejection |interviewing.io/blog |
| 10 |reddit r/learnprogramming |Beginner to first tech job guide |reddit.com/r/learnprogramming/wiki |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Reasoning:**Tech career advice tends to be written in short, dense tips 
and bullet points. A 300-character window captures roughly one complete 
tip or advice point. Overlap of 50 ensures advice that spans two chunks 
is still retrievable intact.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**all-MiniLM-L6-v2 (via sentence-transformers)

**Top-k:** 5

**Production tradeoff reflection:**In a real production system I would 
consider OpenAI's text-embedding-3-small for higher accuracy, but it 
costs money per token. all-MiniLM-L6-v2 is free, fast, and runs locally. 
For a multilingual audience I'd consider multilingual-e5-base. For longer 
documents, a model with larger context length like text-embedding-3-large 
would reduce chunking issues.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |What should I put on my resume if I have no experience? |Include projects, GitHub links, and relevant coursework |
| 2 |How do I negotiate a higher salary offer? |Have a competing offer or market data, respond by email not phone |
| 3 |How many LeetCode problems do I need to solve before interviews? |Around 100-150 focusing on patterns not memorization |
| 4 |Is a coding bootcamp worth it for getting a tech job? |Depends on quality — CodePath and top bootcamps have good placement |
| 5 |How do I get a referral at a big tech company? |Connect on LinkedIn, ask former classmates, be specific about the role |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.Noisy Reddit text — Reddit posts contain slang, jokes, and off-topic 
   replies that could get embedded and retrieved as if they were real advice, 
   hurting response quality.

2.Chunks splitting key advice — A tip like "Do X, but never do Y" could 
   get split so only "Do X" is retrieved, giving incomplete or misleading 
   answers.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     (os + open())    (ingest.py)  (sentence-transformers   (ChromaDB      (Claude/
                                    + ChromaDB)             .query())      OpenAI API)
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**I'll give Claude my Documents table and Chunking Strategy section and ask
it to implement load_documents() and chunk_document() with chunk_size=300
and overlap=50. Each chunk should return text, source, and chunk_id.
I'll verify by checking total chunk count and printing 3 sample chunks
to confirm source attribution is correct.

**Milestone 4 — Embedding and retrieval:**I'll give Claude my Retrieval Approach section and ask it to implement
embed_and_store() using ChromaDB and retrieve() using _collection.query()
returning text, source, and distance. I'll verify by running a test query
like "how do I negotiate salary" and checking the top 5 results come from
relevant documents.

**Milestone 5 — Generation and interface:**I'll give Claude my Evaluation Plan questions and ask it to implement
generate_response() using only retrieved chunks as context, with source
attribution showing which document each answer came from. I'll verify
using all 5 test questions and confirming answers are grounded in the
documents and not from the model's general knowledge.
