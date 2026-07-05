# Letterboxd Better Watchlist

## Goal

CLI tool that scrapes a Letterboxd watchlist and displays per-film details + ratings in the terminal.

## Data Sources

- **Letterboxd watchlist** — scraped via BeautifulSoup for film slugs/titles/years
- **Letterboxd film page** — scraped via BeautifulSoup for Letterboxd rating
- **OMDb API** — queried by title + year for director, actors, awards, and IMDb/Rotten Tomatoes/Metacritic ratings

## Fields Displayed

- Title, year, director
- First 3 actors (from OMDb)
- Awards (if any, else "None")
- 4 ratings: Letterboxd, IMDb, Rotten Tomatoes, Metacritic

## Constraints

- No database
- No tests (unless asked)
- No other external APIs beyond OMDb
