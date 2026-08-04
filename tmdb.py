import os
import random
import time

from requests_cache import CachedSession

CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_DELAY = 0.4

session = CachedSession(
    os.path.join(CACHE_DIR, "tmdb"),
    backend="sqlite",
    expire_after=-1,
)


def _strip_vary(resp, **kwargs):
    resp.headers.pop("Vary", None)
    return resp


session.hooks["response"].append(_strip_vary)


def get_tmdb_titles(title, year, token, refresh=False):
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    params = {"query": title, "language": "it-IT", "include_adult": "false"}
    if year:
        params["year"] = year
    try:
        resp = session.get(
            f"{TMDB_BASE}/search/movie",
            params=params,
            headers=headers,
            timeout=15,
            force_refresh=refresh,
        )
        if not resp.from_cache:
            time.sleep(TMDB_DELAY + random.random() * TMDB_DELAY)
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