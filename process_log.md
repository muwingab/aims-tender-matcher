# process_log.md — AIMS KTT Hackathon T2.2
## Candidate: Marie Alice Uwingabire
## Date: 23 April 2026

---

## Hour-by-Hour Timeline

| Time | Activity |
|------|----------|
| 00:00–00:30 | Read challenge brief end-to-end. Decided on TF-IDF over multilingual embeddings based on CPU and 3-minute runtime constraints. Designed scoring formula: 0.6*tfidf + 0.2*budget_fit + 0.2*deadline_fit. Set up GitHub repo. |
| 00:30–01:30 | Built generate_data.py, 40 unique synthetic tenders (24 EN, 16 FR), 10 business profiles across Rwanda/Kenya/Uganda/Senegal/DRC/Ethiopia, gold_matches.csv with 3 matches per profile. Fixed duplicate tender titles. Fixed profile 07 country mismatch (Uganda not Kenya). |
| 01:30–02:30 | Built matcher.py tender parsing, language detection via langdetect, TF-IDF index, budget_fit and deadline_fit scoring functions, rank() combining all three signals, template-based summary generation in EN and FR, CLI with --profile and --topk flags. |
| 02:30–03:00 | Diagnosed confusion cases: language boilerplate dominating sector signal (profile 02), budget/deadline fit inflating wrong tenders (profile 03), vocabulary sparsity on short needs_text (profile 04). Documented all three in eval notebook. |
| 03:00–03:30 | Built evall.ipynb  MRR@5, Recall@5, confusion cases analysis, language detection breakdown, score distribution plots, summary table. Results: MRR@5=0.495, Recall@5=0.400, language split 24EN/16FR exactly matching 60/40 target. |
| 03:30–04:00 | Wrote village_agent.md  voice call center workflow for illiterate cooperative leaders, language matrix (Rwanda→Kinyarwanda, Kenya→Swahili, Senegal→Wolof, DRC→Lingala, Ethiopia→Amharic), RWF cost math at 500 cooperatives. Finalized README. Recorded video. |

---

## LLM / Tool Use Declaration

| Tool | Version | Purpose |
|------|---------|---------|
| Claude (Anthropic) | claude-sonnet-4-20250514 | Code scaffolding and boilerplate generation based on my specifications |

---

### 3 Sample Prompts I Actually Sent

**Prompt 1 (used):**

    Build matcher.py with TF-IDF index on tender text, language detection
    via langdetect, and a rank() function combining cosine similarity with
    budget_fit and deadline_fit signals. Combined score:
    0.6*tfidf + 0.2*budget_fit + 0.2*deadline_fit. CLI: 
    python matcher.py --profile 02 --topk 5. CPU-only, 
    all 10 profiles under 3 minutes.

*Why: I designed the scoring formula myself, the 0.6/0.2/0.2 weights
were my decision based on TF-IDF being the dominant signal with budget
and deadline as tiebreakers. I used Claude to implement the boilerplate.*

**Prompt 2 (used):**

    Fix generate_data.py to produce exactly 40 unique tender titles,
    no duplicates. Keep 60/40 EN/FR split. Fix profile 07 country 
    from Kenya to Uganda.

*Why: I identified the duplicate problem and country mismatch 
from inspecting the terminal output. I knew exactly what needed fixing.*

**Prompt 3 (used):**

    Create evall.ipynb computing MRR@5 and Recall@5 against 
    gold_matches.csv. Show 3 confusion cases for the profiles 
    with lowest RR. Include language detection breakdown and 
    score distribution plots.

*Why: The brief specifically requires Recall@5 and 3 confusion cases.
I wanted different failure modes for each confusion case to show
analytical depth, not just three profiles that failed the same way.*

---

### 1 Prompt I Discarded

    Replace TF-IDF with paraphrase-multilingual-MiniLM-L12-v2 
    for better cross-lingual matching between EN/FR tenders 
    and profile needs_text.

*Why discarded: The brief requires end-to-end run under 3 minutes on
CPU. A multilingual sentence transformer adds model download time and
inference overhead that likely violates this constraint. TF-IDF with
langdetect-based language routing is the right pragmatic choice here.
Multilingual embeddings are the correct next step once the latency
constraint is relaxed, documented in README as a stretch goal.*

---

## Hardest Decision

The hardest decision was the scoring formula weights: 0.6 for TF-IDF,
0.2 for budget fit, and 0.2 for deadline fit.

Higher TF-IDF weight risks ignoring practical constraints, a perfect
sector match with an expired deadline is useless. Lower TF-IDF weight
risks surfacing off-sector tenders that happen to have good budgets and
deadlines. The confusion case analysis confirmed this tension: profile
03 (CleanGrid Kenya) failed precisely because budget and deadline fit
inflated wrong tenders above the correct sector matches.

The 0.6/0.2/0.2 split was chosen after reasoning that sector relevance
is the primary filter, an entrepreneur should not see an edtech grant
if they work in cleantech, regardless of budget. Budget and deadline
serve as tiebreakers between equally relevant sector matches. A
sector-weighted boost (similar to the local-boost in Day 1) would be
the right next step to fix the profile 03 failure mode.