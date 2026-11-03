"""
Smart Matching Engine for Campus Lost & Found.
Uses Scikit-Learn TF-IDF Vectorization and Cosine Similarity to compare
lost and found item reports based on textual features, descriptions, categories, and attributes.
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    """Normalize and clean text input."""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build_item_text(item):
    """
    Constructs a weighted enriched textual representation of an item.
    Crucial attributes like name, category, colour, and location are repeated to give
    appropriate weight during TF-IDF vectorization relative to the long description.
    """
    name = clean_text(item.get("name", ""))
    category = clean_text(item.get("category", ""))
    colour = clean_text(item.get("colour", ""))
    location = clean_text(item.get("location", ""))
    description = clean_text(item.get("description", ""))

    # Repeat name, category, colour for term weighting
    tokens = [
        name, name,
        category, category,
        colour, colour,
        location,
        description
    ]
    return " ".join([t for t in tokens if t])

def calculate_similarity_matrix(source_items, target_items):
    """
    Computes a 2D cosine similarity matrix between source_items and target_items
    using a fitted TF-IDF vectorizer.
    Returns:
        matrix: 2D numpy array of similarity scores (0.0 to 1.0)
    """
    if not source_items or not target_items:
        return None

    source_texts = [build_item_text(item) for item in source_items]
    target_texts = [build_item_text(item) for item in target_items]
    corpus = source_texts + target_texts

    # Check if there are meaningful words across the corpus
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    try:
        vectorizer.fit(corpus)
        source_tfidf = vectorizer.transform(source_texts)
        target_tfidf = vectorizer.transform(target_texts)
        sim_matrix = cosine_similarity(source_tfidf, target_tfidf)
        return sim_matrix
    except ValueError:
        # Fallback if vocabulary is completely empty or empty strings
        return None

def find_matches_for_item(target_item, candidate_items, min_threshold=0.10, top_k=10):
    """
    Finds and ranks the top matches for a single item against candidate items.

    Parameters:
        target_item (dict): The item to find matches for (lost or found).
        candidate_items (list[dict]): The pool of candidate opposite items.
        min_threshold (float): Minimum cosine similarity to consider as match (e.g. 0.10 = 10%).
        top_k (int): Maximum number of matches to return.

    Returns:
        list[dict]: List of matches sorted descending by similarity percentage.
                    Each dict contains candidate item data + 'similarity_score' (0-1) and 'match_percentage' (0-100%).
    """
    if not candidate_items:
        return []

    # Filter candidates to only consider active items or different type if specified
    valid_candidates = [
        c for c in candidate_items
        if c.get("id") != target_item.get("id")
    ]
    if not valid_candidates:
        return []

    matrix = calculate_similarity_matrix([target_item], valid_candidates)
    if matrix is None:
        return []

    scores = matrix[0]
    matches = []

    for idx, candidate in enumerate(valid_candidates):
        raw_score = float(scores[idx])

        # Boost score slightly if category exactly matches to reward taxonomic agreement
        boosted_score = raw_score
        target_cat = str(target_item.get("category", "")).strip().lower()
        cand_cat = str(candidate.get("category", "")).strip().lower()
        if target_cat and cand_cat and target_cat == cand_cat:
            boosted_score = min(1.0, boosted_score * 1.15 + 0.05)

        # Scale to percentage
        match_percentage = round(min(1.0, max(0.0, boosted_score)) * 100, 1)

        if boosted_score >= min_threshold or raw_score >= min_threshold:
            match_data = dict(candidate)
            match_data["similarity_score"] = round(boosted_score, 4)
            match_data["match_percentage"] = match_percentage
            match_data["raw_score"] = round(raw_score, 4)
            matches.append(match_data)

    matches.sort(key=lambda m: m["similarity_score"], reverse=True)
    return matches[:top_k]

def find_all_campus_matches(lost_items, found_items, min_threshold=0.15, top_per_pair=5):
    """
    Computes global smart matches between all lost items and found items for the campus matrix.
    Returns:
        list[dict]: Pairings with lost item, found item, and match score.
    """
    if not lost_items or not found_items:
        return []

    sim_matrix = calculate_similarity_matrix(lost_items, found_items)
    if sim_matrix is None:
        return []

    pairings = []
    for l_idx, lost in enumerate(lost_items):
        for f_idx, found in enumerate(found_items):
            raw_score = float(sim_matrix[l_idx][f_idx])
            boosted_score = raw_score
            if lost.get("category") and found.get("category") and lost.get("category") == found.get("category"):
                boosted_score = min(1.0, boosted_score * 1.15 + 0.05)

            if boosted_score >= min_threshold or raw_score >= min_threshold:
                match_percentage = round(min(1.0, max(0.0, boosted_score)) * 100, 1)
                pairings.append({
                    "lost_item": lost,
                    "found_item": found,
                    "similarity_score": round(boosted_score, 4),
                    "match_percentage": match_percentage
                })

    pairings.sort(key=lambda p: p["similarity_score"], reverse=True)
    return pairings
