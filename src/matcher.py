import re
import unicodedata

from rapidfuzz import fuzz

MATCH_THRESHOLD = 85.0


def normalize(title):
    if not title:
        return ""
    text = unicodedata.normalize("NFKD", title.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_tv_match(english_title, italian_title, listings):
    if not listings:
        return ""

    exact = listings.get(english_title.lower()) if english_title else None
    if exact is None and italian_title:
        exact = listings.get(italian_title.lower())
    if exact:
        return exact

    normalized_listings = {
        normalize(key): value for key, value in listings.items()
    }

    candidates = set()
    if english_title:
        candidates.add(normalize(english_title))
    if italian_title:
        candidates.add(normalize(italian_title))

    best_key = None
    best_score = MATCH_THRESHOLD
    for cand in candidates:
        if not cand:
            continue
        for norm_key, value in normalized_listings.items():
            if not norm_key:
                continue
            score = fuzz.token_sort_ratio(cand, norm_key)
            if score > best_score:
                best_score = score
                best_key = norm_key

    return normalized_listings.get(best_key, "") if best_key else ""