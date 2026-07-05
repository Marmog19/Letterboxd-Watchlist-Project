# Letterboxd Better Watchlist

## Run

```bash
python3 main.py https://letterboxd.com/{username}/watchlist/
```

## Dependencies

Use the project venv for pip:
```bash
source ~/venvs/Letterboxd_Watchlist/bin/activate
pip install -r requirements.txt
```

Fallback (apt, if venv unavailable):
```bash
sudo apt install python3-requests python3-bs4 python3-rich
```

## .env

`OMDB_API_KEY` must be set in `.env` (already present). Gitignored.

## Architecture

- `main.py` — entry point: loads .env, orchestrates Letterboxd scrape + OMDb API calls, builds `Movie` dataclass
- `scraper.py` — Letterboxd HTML scraping + OMDb HTTP calls
- `display.py` — rich card output

## Scraping Gotchas

- **Letterboxd watchlist**: films are in `div.react-component[data-component-class="LazyPoster"]` with `data-item-slug`, `data-item-name="Title (Year)"`. Not the old `li.poster-container` structure.
- **Letterboxd film page JSON-LD**: wrapped in `/* <![CDATA[ */` comment — extract substring between `{` and `}` before `json.loads`.
- **IMDb.com**: blocks scrapers with AWS WAF (returns HTTP 202 + JS challenge). Use OMDb API instead for IMDb/RT/Metacritic ratings.
- **Rate limits**: `DELAY=0.8` (Letterboxd fetches), `OMDB_DELAY=0.5` (OMDb calls) — random jitter added.

## Entry Points

- App: `main.py` → `main()`
- Scraper module: `get_watchlist_films()`, `get_letterboxd_rating()`, `get_omdb_details()`
- Display module: `display_movies()`

## No tests, no database
