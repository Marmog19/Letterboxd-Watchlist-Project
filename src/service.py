import csv
from pathlib import Path

from src.config import ROOT
from src.matcher import find_tv_match
from src.models import Movie, parse_omdb_ratings
from src.omdb import get_omdb_by_id, get_omdb_details
from src.tmdb import get_tmdb_movie, get_tmdb_titles
from src.tv import get_tv_listings


def _poster_url(poster_path):
    if not poster_path:
        return ""
    return f"https://image.tmdb.org/t/p/w500{poster_path}"


def _build_movie(row, api_key, tmdb_token, tv_lookup, refresh):
    title = row.get("Name", "").strip()
    year = row.get("Year", "").strip()
    lbxd_url = row.get("Letterboxd URI", "").strip()
    if not title:
        return None

    omdb = get_omdb_details(title.rstrip(".,;:!?"), year, api_key, refresh=refresh)
    omdb_ratings = parse_omdb_ratings(omdb) if omdb else {}

    english_title = omdb.get("Title", title) if omdb else title
    italian_title = ""
    poster_url = ""
    if tmdb_token:
        titles = get_tmdb_titles(english_title, year, tmdb_token, refresh=refresh)
        if titles:
            italian_title = titles[1] or ""
            poster_url = _poster_url(titles[2])

    return Movie(
        title=english_title,
        year=(omdb.get("Year", year) if omdb else year),
        director=(omdb.get("Director", "N/A") if omdb else "N/A"),
        actors=(
            [a.strip() for a in omdb.get("Actors", "").split(",") if a.strip()][:3]
            if omdb
            else []
        ),
        awards=(omdb.get("Awards", "N/A") if omdb else "N/A"),
        letterboxd_url=lbxd_url,
        imdb_rating=omdb_ratings.get("imdb", "N/A"),
        rotten_tomatoes_rating=omdb_ratings.get("rt", "N/A"),
        metacritic_rating=omdb_ratings.get("metacritic", "N/A"),
        on_tv=find_tv_match(english_title, italian_title, tv_lookup),
        poster_url=poster_url,
        imdb_id=(omdb.get("imdbID", "") if omdb else ""),
        imdb_votes=(omdb.get("imdbVotes", "N/A") if omdb else "N/A"),
    )


def _build_tv_movie(programme_list, api_key, tmdb_token, refresh):
    italian_title = programme_list[0].title
    english_title = italian_title
    omdb = None
    poster_url = ""
    tmdb_imdb_id = ""

    if tmdb_token:
        movie = get_tmdb_movie(italian_title, tmdb_token, refresh=refresh)
        if movie is None:
            movie = get_tmdb_movie(italian_title, tmdb_token, refresh=refresh, min_score=0)
        if movie:
            _, localized, _, imdb_id, poster_path = movie
            if localized:
                english_title = localized
            poster_url = _poster_url(poster_path)
            tmdb_imdb_id = imdb_id or ""
            if imdb_id:
                omdb = get_omdb_by_id(imdb_id, api_key, refresh=refresh)

    if omdb is None:
        omdb = get_omdb_details(english_title, "", api_key, refresh=refresh)
    omdb_ratings = parse_omdb_ratings(omdb) if omdb else {}

    return Movie(
        title=omdb.get("Title", english_title) if omdb else english_title,
        year=(omdb.get("Year", "") if omdb else ""),
        director=(omdb.get("Director", "N/A") if omdb else "N/A"),
        actors=(
            [a.strip() for a in omdb.get("Actors", "").split(",") if a.strip()][:3]
            if omdb
            else []
        ),
        awards=(omdb.get("Awards", "N/A") if omdb else "N/A"),
        imdb_rating=omdb_ratings.get("imdb", "N/A"),
        rotten_tomatoes_rating=omdb_ratings.get("rt", "N/A"),
        metacritic_rating=omdb_ratings.get("metacritic", "N/A"),
        on_tv=programme_list,
        poster_url=poster_url,
        imdb_id=(omdb.get("imdbID", "") if omdb else "") or tmdb_imdb_id,
        imdb_votes=(omdb.get("imdbVotes", "N/A") if omdb else "N/A"),
    )


def read_rows(csv_path):
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))


def build_tv_movies(api_key, tmdb_token, refresh=False):
    tv_lookup = get_tv_listings(refresh=refresh, tmdb_token=tmdb_token)
    movies = [_build_tv_movie(progs, api_key, tmdb_token, refresh)
              for progs in tv_lookup.values()]
    movies.sort(key=lambda m: min(p.start for p in m.on_tv))
    return movies


def build_watchlist_movies(csv_path, api_key, tmdb_token, refresh=False, on_row=None):
    rows = read_rows(csv_path)
    tv_lookup = get_tv_listings(refresh=refresh, tmdb_token=tmdb_token)
    movies = []
    for i, row in enumerate(rows, 1):
        if not row.get("Name", "").strip():
            continue
        if on_row:
            on_row(row, i, len(rows))
        movie = _build_movie(row, api_key, tmdb_token, tv_lookup, refresh)
        if movie:
            movies.append(movie)
    return movies


def get_watchlist_csvs():
    return sorted(ROOT.glob("*.csv"))
