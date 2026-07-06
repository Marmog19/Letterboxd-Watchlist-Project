import time
import random

import requests

OMDB_DELAY = 0.5


def get_omdb_details(title, year, api_key):
    time.sleep(OMDB_DELAY + random.random() * OMDB_DELAY)
    params = {"t": title, "apikey": api_key, "plot": "short", "type": "movie"}
    if year:
        params["y"] = year
    try:
        resp = requests.get("https://www.omdbapi.com/", params=params, timeout=15)
        data = resp.json()
        if data.get("Response") == "False":
            return None
        return data
    except Exception:
        return None
