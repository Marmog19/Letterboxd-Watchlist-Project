# Letterboxd Better Watchlist

CLI tool that reads a CSV of a Letterboxd watchlist and displays per-film details + ratings in the terminal. It also checks whether any film from your watchlist airs on Italian free-to-air TV today — or, run with no arguments, shows rich cards for every film on today's schedule.

A companion local web app (`python web.py`) shows the same cards in the browser: today's TV schedule and any watchlist CSV from the project folder (or uploaded).

## Usage

```bash
python main.py watchlist.csv
python main.py watchlist.csv --refresh   # bypass cache and re-fetch from APIs
python main.py                          # TV-only: every film on today's schedule
python web.py                           # local web app at http://127.0.0.1:5000
```

## Data Sources

- **CSV input** — provided by the user, a Letterboxd watchlist export (`Name`, `Year`, `Letterboxd URI`)
- **OMDb API** — queried by title + year for director, actors, awards, and IMDb/Rotten Tomatoes/Metacritic ratings
- **TMDB API** — looks up each film's Italian title so Italian-translated listings can be matched; also resolves Italian schedule titles back to English for the TV-only cards (requires `TMDB_READ_TOKEN` in `.env`)
- **XMLTV feed (epgshare01)** — today's Film programmes on the free-to-air channels listed in `channels.txt`, shown as channel + start–end time for each airing today

Posters and translated titles come from TMDB; the web app attributes TMDB in its footer, as required by their API terms.

## Fields Displayed

- Title, year, director
- First 3 actors (from OMDb)
- Awards (if any, else "None")
- Letterboxd URI (from the CSV)
- 3 ratings: IMDb, Rotten Tomatoes, Metacritic
- 📺 On TV today (channel + start–end time, all airings, when matched)

## Project Structure

```
main.py          thin CLI launcher
web.py           thin web launcher (Flask, 127.0.0.1:5000)
channels.txt     free-to-air channels to scan for films
templates/       Jinja templates for the web app
static/          CSS for the web app
src/
  main.py        orchestration: env, args, CSV read, movie building, display
  web.py         Flask routes: TV schedule + watchlist views
  service.py     shared movie-building layer used by CLI and web
  config.py      project root, .env loading, cache dir
  cache.py       requests-cache session factory + rate-limit helper
  models.py      Movie/TVProgramme dataclasses + ratings parsing
  omdb.py        OMDb API client
  tmdb.py        TMDB API client (Italian/English title resolution)
  tv.py          XMLTV client + film detection + listings parsing
  matcher.py     exact + fuzzy title matching
  display.py     rich card output
```

Cached API responses live in `.cache/` (gitignored). Delete it to clear all caches.
