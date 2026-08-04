from rapidfuzz import fuzz

from src.cache import cached_session, rate_limited_get

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_DELAY = 0.4

session = cached_session("tmdb")


def get_tmdb_titles(title, year, token, refresh=False):
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    params = {"query": title, "language": "it-IT", "include_adult": "false"}
    if year:
        params["year"] = year
    try:
        resp = rate_limited_get(
            session,
            TMDB_DELAY,
            f"{TMDB_BASE}/search/movie",
            params=params,
            headers=headers,
            timeout=15,
            force_refresh=refresh,
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


def get_tmdb_movie(title, token, refresh=False, min_score=85):
    """Return the best title-matching TMDB movie as
    (original, localized, runtime_min, imdb_id) or None. Used to confirm
    whether an unsure listing is really a film and to resolve IMDb IDs."""
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    params = {"query": title, "language": "it-IT", "include_adult": "false"}
    try:
        resp = rate_limited_get(
            session,
            TMDB_DELAY,
            f"{TMDB_BASE}/search/movie",
            params=params,
            headers=headers,
            timeout=15,
            force_refresh=refresh,
        )
        results = resp.json().get("results") or []
        if not results:
            return None

        def score(r):
            return max(
                fuzz.token_sort_ratio(title.lower(), (r.get("title") or "").lower()),
                fuzz.token_sort_ratio(title.lower(), (r.get("original_title") or "").lower()),
            )

        best = max(results, key=score)
        if score(best) < min_score:
            return None

        detail = rate_limited_get(
            session,
            TMDB_DELAY,
            f"{TMDB_BASE}/movie/{best['id']}",
            params={"language": "it-IT"},
            headers=headers,
            timeout=15,
            force_refresh=refresh,
        ).json()
        return (
            (best.get("original_title") or "").strip(),
            (best.get("title") or "").strip(),
            detail.get("runtime") or 0,
            (detail.get("imdb_id") or "").strip() or None,
        )
    except Exception:
        return None
