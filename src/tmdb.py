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
