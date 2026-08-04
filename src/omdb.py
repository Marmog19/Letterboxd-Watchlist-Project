from src.cache import cached_session, rate_limited_get

OMDB_DELAY = 0.5

session = cached_session("omdb")


def _query(params, api_key, refresh):
    params["apikey"] = api_key
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


def get_omdb_details(title, year, api_key, refresh=False):
    params = {"t": title, "plot": "short", "type": "movie"}
    if year:
        params["y"] = year
    return _query(params, api_key, refresh)


def get_omdb_by_id(imdb_id, api_key, refresh=False):
    return _query({"i": imdb_id, "plot": "short"}, api_key, refresh)
