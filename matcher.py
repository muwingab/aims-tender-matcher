"""
Multilingual Grant & Tender Matcher: aims-tender-matcher
Usage: python matcher.py --profile 02 --topk 5
"""

# import necessary libraries
import argparse
import json
import os
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Language detection: uses langdetect library if available,
# falls back to simple French keyword matching if not installed
try:
    from langdetect import detect as _detect_lang
    def detect_language(text):
        try:
            return _detect_lang(text)
        except Exception:
            return "en"
except ImportError:
    def detect_language(text):
        return "fr" if any(w in text.lower() for w in ["le ", "la ", "les ", "du ", "une ", "des "]) else "en"

BASE = os.path.dirname(os.path.abspath(__file__))
TENDERS_DIR = os.path.join(BASE, "tenders")
DATA_DIR = os.path.join(BASE, "data")
SUMMARIES_DIR = os.path.join(BASE, "summaries")
TODAY = datetime(2026, 4, 23)

os.makedirs(SUMMARIES_DIR, exist_ok=True)



# Helper to extract structured fields from raw tender text
# using regex pattern matching on labels like "Sector:", "Budget:", etc.
def _extract_field(text, *labels):
    for label in labels:
        m = re.search(rf"{label}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return ""


# Parse a single .txt tender file into a structured dict.
# Extracts title, sector, budget, deadline, region, and language.
# Title is taken from the first non-empty line of the file.
def parse_tender(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    tid = os.path.splitext(os.path.basename(path))[0]
    title = _extract_field(raw, "Tender ID.*\nLanguage.*\n.*", "TENDER NOTICE —", "AVIS D'APPEL D'OFFRES —")
    # simpler title extraction: first non-empty line after the notice header
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    title = lines[0].replace("TENDER NOTICE — ", "").replace("AVIS D'APPEL D'OFFRES — ", "").title()

    sector = _extract_field(raw, "Secteur", "Sector")
    budget_str = _extract_field(raw, "Budget")
    deadline_str = _extract_field(raw, "Deadline", "Date limite")
    region = _extract_field(raw, "Région", "Region")
    lang = detect_language(raw)

    budget = 0
    m = re.search(r"[\d,]+", budget_str)
    if m:
        budget = int(m.group().replace(",", ""))

    deadline = None
    if deadline_str:
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%B %d, %Y"):
            try:
                deadline = datetime.strptime(deadline_str[:10], fmt)
                break
            except ValueError:
                pass

    return {
        "id": tid,
        "title": title,
        "sector": sector,
        "budget_usd": budget,
        "deadline": deadline,
        "region": region,
        "language": lang,
        "text": raw,
    }


# Load all .txt tender files from the tenders/ directory.
# Returns a list of parsed tender dicts.
def load_tenders():
    tenders = []
    for fname in sorted(os.listdir(TENDERS_DIR)):
        if fname.endswith(".txt"):
            tenders.append(parse_tender(os.path.join(TENDERS_DIR, fname)))
    return tenders


def load_profiles():
    path = os.path.join(DATA_DIR, "profiles.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)



# Budget fit score: 1.0 for SME-appropriate budgets (<=200k USD),
# 0.5 for large grants that may have stricter eligibility requirements.
def budget_fit(budget_usd):
    return 1.0 if budget_usd <= 200_000 else 0.5


# Deadline fit score: 1.0 if deadline is more than 30 days away,
# 0.5 if deadline is soon (<=30 days), 0.0 if already expired.
def deadline_fit(deadline):
    if deadline is None:
        return 0.5
    days_left = (deadline - TODAY).days
    if days_left <= 0:
        return 0.0
    return 1.0 if days_left > 30 else 0.5


# Build TF-IDF index on all tender text.
# sublinear_tf=True uses log(1+tf) to dampen high-frequency terms.
# Returns fitted vectorizer and the document-term matrix.
def build_tfidf_index(tenders):
    corpus = [t["text"] for t in tenders]
    vectorizer = TfidfVectorizer(max_features=5000, sublinear_tf=True)
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix


""" Core ranking function.
Scoring pipeline:
 1. Cosine similarity between profile needs_text and each tender (TF-IDF)
 2. Budget fit score per tender
 3. Deadline fit score per tender
 4. Combined: 0.6*tfidf + 0.2*budget_fit + 0.2*deadline_fit
 TF-IDF dominates (0.6 weight) because sector relevance is the
 primary filter. Budget and deadline act as tiebreakers"""

def rank(profile, tenders, vectorizer, tfidf_matrix):
    query_vec = vectorizer.transform([profile["needs_text"]])
    tfidf_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    results = []
    for i, tender in enumerate(tenders):
        b_fit = budget_fit(tender["budget_usd"])
        d_fit = deadline_fit(tender["deadline"])
        combined = 0.6 * tfidf_scores[i] + 0.2 * b_fit + 0.2 * d_fit
        results.append({**tender, "tfidf": tfidf_scores[i], "budget_fit": b_fit,
                        "deadline_fit": d_fit, "score": combined})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results



# Summary templates in English and French.
# Slots filled from tender and profile fields.
# Kept template-based (not LLM) to respect CPU-only constraint.
EN_TEMPLATE = (
    "This tender matches your profile because it targets {sector} and offers {budget} USD in funding. "
    "The deadline is {deadline}. Your focus on {needs} and operations in {country} align with the "
    "eligibility criteria. We recommend applying as your {employees}-person team meets the size requirements."
)

FR_TEMPLATE = (
    "Cet appel d'offres correspond à votre profil car il cible le secteur {sector} et offre {budget} USD "
    "de financement. La date limite est le {deadline}. Votre activité dans {country} et votre équipe de "
    "{employees} personnes correspondent aux critères d'éligibilité."
)


def _short_needs(needs_text, max_words=8):
    words = needs_text.split()[:max_words]
    return " ".join(words).rstrip(",. ") + "..."


# Generate an ~80-word summary for a profile-tender match.
# Language selected from profile's preferred language list.
# Falls back to English if no language preference set.
def generate_summary(profile, tender, lang=None):
    if lang is None:
        lang = profile["languages"][0] if profile["languages"] else "en"

    deadline_str = tender["deadline"].strftime("%Y-%m-%d") if tender["deadline"] else "TBD"
    budget_fmt = f"{tender['budget_usd']:,}"

    if lang == "fr":
        text = FR_TEMPLATE.format(
            sector=tender["sector"],
            budget=budget_fmt,
            deadline=deadline_str,
            country=profile["country"],
            employees=profile["employees"],
        )
    else:
        text = EN_TEMPLATE.format(
            sector=tender["sector"],
            budget=budget_fmt,
            deadline=deadline_str,
            needs=_short_needs(profile["needs_text"]),
            country=profile["country"],
            employees=profile["employees"],
        )
    return text


# Save a match summary as a .md file to the summaries/ folder.
# Filename format: profile_[id]_tender_[id].md
def save_summary(profile, tender, summary):
    fname = f"profile_{profile['id']}_tender_{tender['id']}.md"
    path = os.path.join(SUMMARIES_DIR, fname)
    content = f"# Match Summary\n\n**Profile:** {profile['name']}  \n**Tender:** {tender['title']}  \n**Score:** {tender['score']:.4f}\n\n{summary}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path



# Format and print top-k results to terminal as a table.
# Columns: rank, title, score, language, budget, deadline.
def print_results(profile, ranked, topk):
    print(f"\n{'='*60}")
    print(f"Profile: {profile['name']} ({profile['id']}) | {profile['country']} | {profile['sector']}")
    print(f"{'='*60}")
    print(f"{'Rank':<5} {'Title':<35} {'Score':>6} {'Lang':>5} {'Budget':>10} {'Deadline'}")
    print("-" * 80)
    for i, t in enumerate(ranked[:topk], 1):
        dl = t["deadline"].strftime("%Y-%m-%d") if t["deadline"] else "N/A"
        title = t["title"][:33] + ".." if len(t["title"]) > 33 else t["title"]
        print(f"{i:<5} {title:<35} {t['score']:>6.4f} {t['language']:>5} {t['budget_usd']:>10,} {dl}")
    print()


# Run the full pipeline for a single profile:
# load → rank → print → generate summaries → save summaries.
def run_profile(profile_id, topk, tenders, vectorizer, tfidf_matrix, profiles):
    profile = next((p for p in profiles if p["id"] == profile_id), None)
    if profile is None:
        print(f"Profile '{profile_id}' not found.")
        return

    ranked = rank(profile, tenders, vectorizer, tfidf_matrix)
    print_results(profile, ranked, topk)

    lang = profile["languages"][0] if profile["languages"] else "en"
    for tender in ranked[:topk]:
        summary = generate_summary(profile, tender, lang)
        save_summary(profile, tender, summary)


# CLI entry point.
# Supports --profile (single ID or 'all') and --topk flags.
# Loads tenders once, builds index once, then runs per profile.
def main():
    parser = argparse.ArgumentParser(description="Multilingual Grant & Tender Matcher")
    parser.add_argument("--profile", default="all", help="Profile ID (e.g. 01) or 'all'")
    parser.add_argument("--topk", type=int, default=5, help="Number of top matches to return")
    args = parser.parse_args()

    print("Loading tenders...")
    tenders = load_tenders()
    print(f"  {len(tenders)} tenders loaded")

    print("Building TF-IDF index...")
    vectorizer, tfidf_matrix = build_tfidf_index(tenders)

    print("Loading profiles...")
    profiles = load_profiles()
    print(f"  {len(profiles)} profiles loaded")

    if args.profile.lower() == "all":
        for p in profiles:
            run_profile(p["id"], args.topk, tenders, vectorizer, tfidf_matrix, profiles)
    else:
        profile_id = args.profile.zfill(2)
        run_profile(profile_id, args.topk, tenders, vectorizer, tfidf_matrix, profiles)

    print(f"Summaries saved to: {SUMMARIES_DIR}")


if __name__ == "__main__":
    main()
