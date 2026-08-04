from rich.console import Console
from rich.panel import Panel

console = Console()

_RATINGS = [
    ("IMDb", 10.0),
    ("Rotten Tomatoes", 100.0),
    ("Metacritic", 100.0),
]


def _bar(value, max_val, width=22):
    ratio = value / max_val if max_val else 0
    filled = int(ratio * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def _color(val_str, max_val):
    if val_str == "N/A":
        return "dim"
    try:
        ratio = float(val_str) / max_val
    except (ValueError, TypeError):
        return "dim"
    if ratio >= 0.8:
        return "green"
    if ratio >= 0.6:
        return "yellow"
    return "red"


def _fmt(val_str, max_val):
    if val_str == "N/A":
        return "N/A"
    if max_val == 10.0:
        return f"{val_str}/10"
    return f"{val_str}%"


def display_movies(movies):
    for movie in movies:
        lines = []

        title = f"[bold]{movie.title}[/bold]"
        if movie.year:
            title += f"  [dim]({movie.year})[/dim]"
        lines.append(title)

        lines.append(f"Director: [italic]{movie.director or 'N/A'}[/italic]")
        lines.append(
            f"Actors: [italic]{', '.join(movie.actors) if movie.actors else 'N/A'}[/italic]"
        )
        awards = movie.awards or "None"
        if awards in ("", "N/A"):
            awards = "None"
        lines.append(f"Awards: {awards}")

        if movie.letterboxd_url:
            lines.append(f"Letterboxd: [dim]{movie.letterboxd_url}[/dim]")

        if movie.on_tv:
            lines.append("📺 On TV today:")
            for prog in movie.on_tv:
                times = f"{prog.start:%H:%M}–{prog.stop:%H:%M}"
                lines.append(f"  [bold green]{prog.channel} — {times}[/bold green]")

        lines.append("")

        vals = [
            movie.imdb_rating,
            movie.rotten_tomatoes_rating,
            movie.metacritic_rating,
        ]

        for (name, max_val), val in zip(_RATINGS, vals):
            if val != "N/A":
                v = float(val)
                b = _bar(v, max_val)
                c = _color(val, max_val)
                display_name = name if name != "Rotten Tomatoes" else "RT"
                lines.append(
                    f"  [{c}]\u25cf[/] {display_name}: [bold]{v}[/] [dim]{_fmt(val, max_val)}[/]  [{c}]{b}[/]"
                )
            else:
                display_name = name if name != "Rotten Tomatoes" else "RT"
                lines.append(f"  [dim]\u25cb {display_name}: N/A[/dim]")

        content = "\n".join(lines)
        panel = Panel(content, border_style="blue", padding=(0, 1))
        console.print(panel)
        console.print()
