import sys
from dataclasses import dataclass
from urllib.parse import urlparse

from scraper import get_watchlist_films, get_film_details
from display import display_movies, console


@dataclass
class Movie:
    title: str
    year: str
    director: str | None
    letterboxd_rating: str


def extract_username(url):
    parts = urlparse(url).path.strip("/").split("/")
    if not parts or parts[0] in ("watchlist", "list"):
        return None
    return parts[0]


def main():
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

        details = get_film_details(film["slug"])

        movie = Movie(
            title=film["title"],
            year=film.get("year") or "",
            director=details.get("director") if details else None,
            letterboxd_rating=details.get("rating", "N/A") if details else "N/A",
        )
        movies.append(movie)

    console.print("\n[bold]Results:[/bold]\n")
    display_movies(movies)


if __name__ == "__main__":
    main()
