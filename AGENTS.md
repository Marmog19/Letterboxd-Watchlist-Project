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
`TMDB_READ_TOKEN` (API Read Access Token) enables Italian-title translation matching. Optional — without it, matching falls back to English only.

## Architecture

- `main.py` — entry point: loads .env, reads CSV, queries OMDb API, builds `Movie` dataclass
- `scraper.py` — OMDb HTTP calls only
- `display.py` — rich card output
- `tv.py` — fetches Italian XMLTV feed (epgshare01), parses today's Film programmes → `{lowercase_title: "HH:MM on Channel"}`
- `tmdb.py` — TMDB search for localized (Italian) title; uses `Authorization: Bearer <TMDB_READ_TOKEN>` header
- `matcher.py` — title matching: exact case-insensitive first, then RapidFuzz `token_sort_ratio` (threshold ≥ 85) against English + Italian titles

## Cache

- `requests-cache` with one sqlite backend per API in `.cache/` (gitignored): `omdb.sqlite`, `tmdb.sqlite`, `tv.sqlite`.
- OMDb/TMDB responses cached indefinitely (`expire_after=-1`); XMLTV feed refreshes every 12h.
- Rate-limit sleeps only apply on real network calls (`not response.from_cache`).
- `python main.py watchlist.csv --refresh` bypasses cached responses and rewrites them. Delete `.cache/` to clear everything.

## Matching behavior

- Exact match (case-insensitive) on either English or Italian title wins first.
- Otherwise RapidFuzz fuzzy match across listing titles (handles punctuation/word-order like `Kill Bill: Volume 1` vs `kill bill - volume 1`).
- Italian translations (e.g. `The Godfather` → `Il padrino`) work only when `TMDB_READ_TOKEN` is set.

## CSV Format

Expected columns: `Name`, `Year`, `Letterboxd URI` (only `Name` required).

## OMDb Rate Limit

`OMDB_DELAY=0.5` (random jitter added). Free tier: 1,000 requests/day.

## Git workflow

- Base branch: `dev`. Feature branches branch off `dev` and merge back into `dev`.
- Start of every task:
  ```bash
  git checkout dev && git pull
  git checkout -b feat/<short-slug>
  ```
- Branch naming: `feat/` feature · `fix/` bug · `chore/` housekeeping · `docs/` docs.
- Conventional Commits: `feat: ...`, `fix: ...`, `chore: ...`. Commit at logical milestones, not once at the end.
- Before each commit run `git status` + `git diff`, stage only intended files, never `.env` (gitignored).
- At task end: merge feature branch into `dev` and delete it. Push/PR only when the user asks.

## No tests, no database
