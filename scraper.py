import time
import random
import re
import json

import requests
from bs4 import BeautifulSoup

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

DELAY = 0.8
OMDB_DELAY = 0.5


def _fetch(url, retries=2):
    for attempt in range(retries):
        try:
            time.sleep(DELAY + random.random() * DELAY)
            headers = {
                "User-Agent": random.choice(_USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            resp = requests.get(url, headers=headers, timeout=20)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except Exception:
            if attempt == retries - 1:
                return None
            time.sleep(2)
    return None


def _jsonld(soup):
    for script in soup.find_all("script", type="application/ld+json"):
        content = script.string
        if not content:
            continue
        start = content.find("{")
        end = content.rfind("}")
        if start < 0 or end <= start:
            continue
        try:
            data = json.loads(content[start : end + 1])
            if isinstance(data, dict):
                return data
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and item.get("@type") == "Movie":
                        return item
        except Exception:
            continue
    return None


def get_watchlist_films(username):
    base_url = f"https://letterboxd.com/{username}/watchlist/"
    films, page = [], 1

    while True:
        url = base_url if page == 1 else f"{base_url}page/{page}/"
        soup = _fetch(url)
        if soup is None:
            break

        items = soup.select('div.react-component[data-component-class="LazyPoster"]')
        if not items:
            break

        for item in items:
            slug = item.get("data-item-slug") or ""
            item_name = item.get("data-item-name") or ""

            title = item_name
            year = ""
            if item_name:
                m = re.search(r"\((\d{4})\)$", item_name)
                if m:
                    title = item_name[: m.start()].strip()
                    year = m.group(1)

            if slug:
                films.append(
                    {
                        "slug": slug,
                        "title": title or slug.replace("-", " ").title(),
                        "year": year,
                    }
                )

        pag = soup.select_one("div.pagination")
        if not pag or not pag.find("a", class_="next"):
            break
        page += 1

    return films


def get_letterboxd_rating(slug):
    url = f"https://letterboxd.com/film/{slug}/"
    soup = _fetch(url)
    if soup is None:
        return "N/A"

    ld = _jsonld(soup)
    if ld:
        ar = ld.get("aggregateRating") or {}
        if ar.get("ratingValue") is not None:
            return str(ar["ratingValue"])

    return "N/A"


def get_omdb_details(title, year, api_key):
    time.sleep(OMDB_DELAY + random.random() * OMDB_DELAY)
    params = {"t": title, "apikey": api_key, "plot": "short"}
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
