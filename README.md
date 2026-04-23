# Multilingual Grant & Tender Matcher: AIMS KTT Hackathon T2.2

## Problem
African Union and regional bodies publish thousands of grants and tenders
in EN/FR in dense bureaucratic language. African entrepreneurs miss the
right ones. This matcher ranks the most relevant tenders for each business
profile and writes a short summary explaining why they match, in the
profile's preferred language.

## Quick Start (2 commands)

    pip install -r requirements.txt
    python data/generate_data.py && python matcher.py --profile 02 --topk 5

## Project Structure

    aims-tender-matcher/
    ├── matcher.py              # main matcher + CLI
    ├── evall.ipynb             # evaluation notebook
    ├── summaries/              # one .md per profile-tender match
    ├── data/
    │   ├── generate_data.py    # synthetic data generator
    │   ├── profiles.json       # 10 business profiles
    │   ├── gold_matches.csv    # 30 gold matches (3 per profile)
    │   └── tenders/            # 40 tender .txt files (24 EN, 16 FR)
    ├── village_agent.md        # product & business artifact
    ├── process_log.md          # LLM use log
    ├── SIGNED.md               # honour code
    └── requirements.txt

## How It Works

### 1. Tender Parsing
All 40 tenders parsed from .txt files. Fields extracted: title, sector,
budget_usd, deadline, region. Language detected automatically via langdetect.

### 2. TF-IDF Index
Tender text indexed using TF-IDF (max 5,000 features, sublinear_tf).
Profile needs_text is the query.

### 3. Scoring Formula

    combined = 0.6 * tfidf_cosine + 0.2 * budget_fit + 0.2 * deadline_fit

- budget_fit: 1.0 if budget <= 200k USD, 0.5 if larger
- deadline_fit: 1.0 if deadline > 30 days away, 0.5 if <= 30 days, 0.0 if expired

### 4. Summary Generation
80-word summary per match generated in profile's preferred language (EN or FR)
using a template citing sector, budget, deadline, and eligibility fit.
Saved to summaries/profile_[id]_tender_[id].md

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| --profile | all | Profile ID e.g. 02, or 'all' |
| --topk | 5 | Number of top matches to return |

**Examples:**

    # Single profile, top 5
    python matcher.py --profile 02 --topk 5

    # All profiles, top 3
    python matcher.py --profile all --topk 3

    # All profiles, default top 5
    python matcher.py --profile all

## Key Results

| Metric | Value |
|--------|-------|
| MRR@5 | 0.495 |
| Recall@5 | 0.400 |
| Language detection EN | 24/40 |
| Language detection FR | 16/40 |
| End-to-end runtime (10 profiles) | < 3 min CPU |

## Known Limitations & Next Steps
- TF-IDF struggles with cross-lingual queries, multilingual sentence
  embeddings (paraphrase-multilingual-MiniLM-L12-v2) would fix this
  once CPU latency constraints are relaxed
- Budget/deadline fit can inflate off-sector tenders, a sector-weighted
  boost would improve precision
- Template summaries are functional but not fluent, LLM generation
  would improve quality at cost of API dependency

## Model & Dataset
TF-IDF vectorizer fitted at runtime — no pretrained weights to download.
Dataset: [LINK TO BE ADDED]

## Video
[LINK TO BE ADDED]

## License
MIT