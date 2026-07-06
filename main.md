# Letterboxd Better Watchlist

## Goal

CLI tool that reads a CSV of a Letterboxd watchlist and displays per-film details + ratings in the terminal.

## Data Sources

- **CSV input** — provided by the user, contains film data from a Letterboxd watchlist export (no scraping)
- **OMDb API** — queried by title + year for director, actors, awards, and IMDb/Rotten Tomatoes/Metacritic ratings

## Fields Displayed

- Title, year, director
- First 3 actors (from OMDb)
- Awards (if any, else "None")
- Letterboxd URI (from the CSV)
- 3 ratings: IMDb, Rotten Tomatoes, Metacritic

## Constraints

- No database
- No tests (unless asked)
- No scraping (fully ToS-compliant)
- No other external APIs beyond OMDb
