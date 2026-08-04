from src.cache import cached_session, rate_limited_get

OMDB_DELAY = 0.5

session = cached_session("omdb")


def get_omdb_details(title, year, api_key, refresh=False):
    params = {"t": title, "apikey": api_key, "plot": "short", "type": "movie"}
    if year:
        params["y"] = year
    try:
        resp = rate_limited_get(
            session,
            OMDB_DELAY,
            "https://www.omdbapi.com/",
            params=params,
            timeout=15,
            force_refresh=refresh,
        )
        data = resp.json()
        if data.get("Response") == "False":
            return None
        return data
    except Exception:
        return None
