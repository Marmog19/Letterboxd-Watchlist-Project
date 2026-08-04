# Letterboxd Better Watchlist

CLI tool that reads a CSV of a Letterboxd watchlist and displays per-film details + ratings in the terminal. It also checks whether any film from your watchlist airs on Italian free-to-air TV today.

## Usage

```bash
python main.py watchlist.csv
python main.py watchlist.csv --refresh   # bypass cache and re-fetch from APIs
```

## Data Sources

- **CSV input** — provided by the user, a Letterboxd watchlist export (`Name`, `Year`, `Letterboxd URI`)
- **OMDb API** — queried by title + year for director, actors, awards, and IMDb/Rotten Tomatoes/Metacritic ratings
- **TMDB API** (optional) — looks up each film's Italian title so Italian-translated listings can be matched (requires `TMDB_READ_TOKEN` in `.env`)
- **XMLTV feed (epgshare01)** — today's Film programmes on Italian free-to-air channels, shown as `HH:MM on Channel`

## Fields Displayed

- Title, year, director
- First 3 actors (from OMDb)
- Awards (if any, else "None")
- Letterboxd URI (from the CSV)
- 3 ratings: IMDb, Rotten Tomatoes, Metacritic
- 📺 On TV today (when a match is found)

## Project Structure

```
main.py          thin launcher
src/
  main.py        orchestration: env, args, CSV read, movie building, display
  config.py      project root, .env loading, cache dir
  cache.py       requests-cache session factory + rate-limit helper
  models.py      Movie dataclass + ratings parsing
  omdb.py        OMDb API client
  tmdb.py        TMDB API client (Italian titles)
  tv.py          XMLTV client + listings parsing
  matcher.py     exact + fuzzy title matching
  display.py     rich card output
```

Cached API responses live in `.cache/` (gitignored). Delete it to clear all caches.
