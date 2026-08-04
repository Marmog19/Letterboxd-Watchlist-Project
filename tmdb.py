import time
import random

import requests

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_DELAY = 0.4


def get_tmdb_titles(title, year, token):
    time.sleep(TMDB_DELAY + random.random() * TMDB_DELAY)
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    params = {"query": title, "language": "it-IT", "include_adult": "false"}
    if year:
        params["year"] = year
    try:
        resp = requests.get(
            f"{TMDB_BASE}/search/movie", params=params, headers=headers, timeout=15
        )
        data = resp.json()
        results = data.get("results") or []
        if not results:
            return None
        best = results[0]
        original = (best.get("original_title") or "").strip()
        localized = (best.get("title") or "").strip()
        return (original, localized)
    except Exception:
        return None