import csv
import os
import sys

from src.config import load_env
from src.display import console, display_movies
from src.matcher import find_tv_match
from src.models import Movie, parse_omdb_ratings
from src.omdb import get_omdb_details
from src.tmdb import get_tmdb_titles
from src.tv import get_tv_listings


def _parse_args(argv):
    refresh = "--refresh" in argv
    positional = [a for a in argv if a != "--refresh"]
    return positional[0] if positional else None, refresh


def _read_rows(csv_path):
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))


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
    if tmdb_token:
        titles = get_tmdb_titles(english_title, year, tmdb_token, refresh=refresh)
        if titles:
            italian_title = titles[1] or ""

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
    )


def main():
    load_env()
    api_key = os.getenv("OMDB_API_KEY")
    if not api_key:
        console.print(
            "[red]Error:[/red] OMDB_API_KEY not found in .env file.\n"
            "Create a .env file with:\n"
            "  OMDB_API_KEY=your_key_here\n"
            "Get a free key at [underline]https://www.omdbapi.com/apikey.aspx[/underline]"
        )
        sys.exit(1)

    tmdb_token = os.getenv("TMDB_READ_TOKEN")
    if tmdb_token:
        console.print("[dim]TMDB translation matching enabled[/dim]")
    else:
        console.print(
            "[yellow]Warning:[/yellow] TMDB_READ_TOKEN not found; matching English titles only. "
            "Add it to .env to match Italian-translated titles."
        )

    csv_path, refresh = _parse_args(sys.argv[1:])
    if not csv_path:
        console.print("[red]Usage:[/red] python main.py <watchlist.csv> [--refresh]")
        sys.exit(1)

    if refresh:
        console.print("[dim]Cache: refresh mode (bypassing cached responses)[/dim]")

    if not os.path.exists(csv_path):
        console.print(f"[red]File not found:[/red] {csv_path}")
        sys.exit(1)

    rows = _read_rows(csv_path)
    if not rows:
        console.print("[yellow]CSV file is empty[/yellow]")
        sys.exit(0)

    console.print(f"Loaded [bold]{len(rows)}[/bold] film(s) from CSV\n")

    console.print("Loading today's TV listings...")
    tv_lookup = get_tv_listings(refresh=refresh)

    movies = []
    for i, row in enumerate(rows, 1):
        if not row.get("Name", "").strip():
            console.print(f"  [dim][{i}/{len(rows)}][/dim] [yellow]Skipping row with no title[/yellow]")
            continue
        console.print(f"  [dim][{i}/{len(rows)}][/dim] {row['Name'].strip()} [dim]{'(' + row.get('Year', '').strip() + ')' if row.get('Year', '').strip() else ''}[/dim]")
        movie = _build_movie(row, api_key, tmdb_token, tv_lookup, refresh)
        if movie:
            movies.append(movie)

    console.print("\n[bold]Results:[/bold]\n")
    display_movies(movies)


if __name__ == "__main__":
    main()
