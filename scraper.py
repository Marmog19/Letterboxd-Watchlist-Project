import os
import random
import time

from requests_cache import CachedSession

CACHE_DIR = ".cache"
os.makedirs(CACHE_DIR, exist_ok=True)

OMDB_DELAY = 0.5

session = CachedSession(
    os.path.join(CACHE_DIR, "omdb"),
    backend="sqlite",
    expire_after=-1,
)


def _strip_vary(resp, **kwargs):
    resp.headers.pop("Vary", None)
    return resp


session.hooks["response"].append(_strip_vary)


def get_omdb_details(title, year, api_key, refresh=False):
    params = {"t": title, "apikey": api_key, "plot": "short", "type": "movie"}
    if year:
        params["y"] = year
    try:
        resp = session.get(
            "https://www.omdbapi.com/",
            params=params,
            timeout=15,
            force_refresh=refresh,
        )
        if not resp.from_cache:
            time.sleep(OMDB_DELAY + random.random() * OMDB_DELAY)
        data = resp.json()
        if data.get("Response") == "False":
            return None
        return data
    except Exception:
        return None
