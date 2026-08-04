import sys
import os
import csv
import re
from dataclasses import dataclass, field

from scraper import get_omdb_details
from display import display_movies, console
from tv import get_tv_listings
from tmdb import get_tmdb_titles
from matcher import find_tv_match


@dataclass
class Movie:
    title: str
    year: str
    director: str
    actors: list[str] = field(default_factory=list)
    awards: str = ""
    letterboxd_url: str = ""
    imdb_rating: str = "N/A"
    rotten_tomatoes_rating: str = "N/A"
    metacritic_rating: str = "N/A"
    on_tv: str = ""


def _load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"([\w_]+)\s*=\s*(.*)", line)
            if m:
                key, val = m.group(1), m.group(2).strip().strip("\"'")
                os.environ.setdefault(key, val)


def _parse_args(argv):
    refresh = "--refresh" in argv
    positional = [a for a in argv if a != "--refresh"]
    return positional[0] if positional else None, refresh


def _parse_omdb_ratings(data):
    ratings = data.get("Ratings", [])
    result = {"imdb": "N/A", "rt": "N/A", "metacritic": "N/A"}
    for r in ratings:
        source = r.get("Source", "")
        value = r.get("Value", "")
        if source == "Internet Movie Database":
            result["imdb"] = value.split("/")[0].strip()
        elif source == "Rotten Tomatoes":
            result["rt"] = value.replace("%", "").strip()
        elif source == "Metacritic":
            result["metacritic"] = value.split("/")[0].strip()
    return result


def main():
    _load_env()
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

    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        console.print("[yellow]CSV file is empty[/yellow]")
        sys.exit(0)

    console.print(f"Loaded [bold]{len(rows)}[/bold] film(s) from CSV\n")

    console.print(f"Loading today's TV listings...")
    tv_lookup = get_tv_listings(refresh=refresh)

    movies = []
    for i, row in enumerate(rows, 1):
        title = row.get("Name", "").strip()
        year = row.get("Year", "").strip()
        lbxd_url = row.get("Letterboxd URI", "").strip()

        if not title:
            console.print(f"  [dim][{i}/{len(rows)}][/dim] [yellow]Skipping row with no title[/yellow]")
            continue

        console.print(f"  [dim][{i}/{len(rows)}][/dim] {title} [dim]{'(' + year + ')' if year else ''}[/dim]")

        omdb = get_omdb_details(title.rstrip(".,;:!?"), year, api_key, refresh=refresh)
        omdb_ratings = _parse_omdb_ratings(omdb) if omdb else {}

        english_title = omdb.get("Title", title) if omdb else title
        italian_title = ""
        if tmdb_token:
            titles = get_tmdb_titles(english_title, year, tmdb_token, refresh=refresh)
            if titles:
                italian_title = titles[1] or ""

        on_tv = find_tv_match(english_title, italian_title, tv_lookup)

        movie = Movie(
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
            on_tv=on_tv,
        )
        movies.append(movie)

    console.print("\n[bold]Results:[/bold]\n")
    display_movies(movies)


if __name__ == "__main__":
    main()
