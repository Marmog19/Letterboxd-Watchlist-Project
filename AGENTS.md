# Letterboxd Better Watchlist

## Run

```bash
python3 main.py watchlist.csv
```

## Dependencies

Use the project venv for pip:
```bash
source ~/venvs/Letterboxd_Watchlist/bin/activate
pip install -r requirements.txt
```

Fallback (apt, if venv unavailable):
```bash
sudo apt install python3-requests python3-rich
```

## .env

`OMDB_API_KEY` must be set in `.env` (already present). Gitignored.

## Architecture

- `main.py` — entry point: loads .env, reads CSV, queries OMDb API, builds `Movie` dataclass
- `scraper.py` — OMDb HTTP calls only
- `display.py` — rich card output

## CSV Format

Expected columns: `Name`, `Year`, `Letterboxd URI` (only `Name` required).

## OMDb Rate Limit

`OMDB_DELAY=0.5` (random jitter added). Free tier: 1,000 requests/day.

## No tests, no database
