import os
import sys

from src.config import load_env
from src.display import console, display_movies
from src.service import build_tv_movies, build_watchlist_movies, read_rows


def _parse_args(argv):
    refresh = "--refresh" in argv
    positional = [a for a in argv if a != "--refresh"]
    return positional[0] if positional else None, refresh


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

    if refresh:
        console.print("[dim]Cache: refresh mode (bypassing cached responses)[/dim]")

    if not csv_path:
        console.print("Loading today's TV listings...")
        movies = build_tv_movies(api_key, tmdb_token, refresh)
        console.print(f"\n[bold]Today's films on TV ({len(movies)}):[/bold]\n")
        display_movies(movies)
        return

    if not os.path.exists(csv_path):
        console.print(f"[red]File not found:[/red] {csv_path}")
        sys.exit(1)

    rows = read_rows(csv_path)
    if not rows:
        console.print("[yellow]CSV file is empty[/yellow]")
        sys.exit(0)

    console.print(f"Loaded [bold]{len(rows)}[/bold] film(s) from CSV\n")

    console.print("Loading today's TV listings...")

    def print_row(row, i, total):
        name = row.get("Name", "").strip()
        year = row.get("Year", "").strip()
        console.print(f"  [dim][{i}/{total}][/dim] {name} [dim]{'(' + year + ')' if year else ''}[/dim]")

    movies = build_watchlist_movies(csv_path, api_key, tmdb_token, refresh, on_row=print_row)

    console.print("\n[bold]Results:[/bold]\n")
    display_movies(movies)


if __name__ == "__main__":
    main()
