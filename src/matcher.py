import re
import unicodedata

from rapidfuzz import fuzz

MATCH_THRESHOLD = 85.0

_ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
          "xi", "xii"}
_SEQUEL_TOKENS = {"part", "vol", "volume", "episodio", "episode", "capitolo"}


def _is_sequel_extra(tokens):
    """True when extra tokens between two titles are all sequel markers
    (digits, Roman numerals, part/volume words). E.g. 'storia infinita'
    vs 'storia infinita 2' -> {'2'}; but 'never ending story' vs
    'the never ending story' -> {'the'} -> False."""
    return all(t.isdigit() or t in _ROMAN or t in _SEQUEL_TOKENS for t in tokens)


def normalize(title):
    if not title:
        return ""
    text = unicodedata.normalize("NFKD", title.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_tv_match(english_title, italian_title, listings):
    if not listings:
        return []

    exact = listings.get(english_title.lower()) if english_title else None
    if exact is None and italian_title:
        exact = listings.get(italian_title.lower())
    if exact:
        return exact

    normalized_listings = {
        normalize(key): key for key in listings
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
        cand_tokens = set(cand.split())
        for norm_key, raw_key in normalized_listings.items():
            if not norm_key:
                continue
            extra = cand_tokens.symmetric_difference(norm_key.split())
            if extra and _is_sequel_extra(extra):
                continue
            score = fuzz.token_sort_ratio(cand, norm_key)
            if score > best_score:
                best_score = score
                best_key = raw_key

    return listings.get(best_key, []) if best_key else []