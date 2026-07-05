import sys
import os
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

from scraper import (
    get_watchlist_films,
    get_letterboxd_rating,
    get_omdb_details,
)
from display import display_movies, console


@dataclass
class Movie:
    title: str
    year: str
    director: str
    actors: list[str] = field(default_factory=list)
    awards: str = ""
    letterboxd_rating: str = "N/A"
    imdb_rating: str = "N/A"
    rotten_tomatoes_rating: str = "N/A"
    metacritic_rating: str = "N/A"


def extract_username(url):
    parts = urlparse(url).path.strip("/").split("/")
    if not parts or parts[0] in ("watchlist", "list"):
        return None
    return parts[0]


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

    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Letterboxd watchlist URL: ").strip()

    if "letterboxd.com" not in url:
        console.print("[red]Not a valid Letterboxd URL[/red]")
        sys.exit(1)

    username = extract_username(url)
    if not username:
        console.print("[red]Could not extract username from URL[/red]")
        sys.exit(1)

    console.print(f"[bold]Scraping watchlist for[/bold] [cyan]{username}[/cyan] ...")

    films = get_watchlist_films(username)
    if not films:
        console.print("[yellow]No films found in watchlist[/yellow]")
        sys.exit(0)

    console.print(f"Found [bold]{len(films)}[/bold] film(s)\n")

    movies = []
    for i, film in enumerate(films, 1):
        console.print(
            f"  [dim][{i}/{len(films)}][/dim] "
            f"{film['title']} [dim]{'(' + film['year'] + ')' if film['year'] else ''}[/dim]"
        )

        lbxd_rating = get_letterboxd_rating(film["slug"])
        title_lookup = film["title"].rstrip(".,;:!?")
        omdb = get_omdb_details(title_lookup, film["year"], api_key)

        omdb_ratings = _parse_omdb_ratings(omdb) if omdb else {}
        movie = Movie(
            title=(omdb.get("Title", film["title"]) if omdb else film["title"]),
            year=(omdb.get("Year", film["year"]) if omdb else film["year"]),
            director=(omdb.get("Director", "N/A") if omdb else "N/A"),
            actors=(
                [a.strip() for a in omdb.get("Actors", "").split(",") if a.strip()][:3]
                if omdb
                else []
            ),
            awards=(omdb.get("Awards", "N/A") if omdb else "N/A"),
            letterboxd_rating=lbxd_rating,
            imdb_rating=omdb_ratings.get("imdb", "N/A"),
            rotten_tomatoes_rating=omdb_ratings.get("rt", "N/A"),
            metacritic_rating=omdb_ratings.get("metacritic", "N/A"),
        )
        movies.append(movie)

    console.print("\n[bold]Results:[/bold]\n")
    display_movies(movies)


if __name__ == "__main__":
    main()
