from rich.console import Console
from rich.panel import Panel

console = Console()


def _bar(value, max_val=5.0, width=24):
    ratio = value / max_val if max_val else 0
    filled = int(ratio * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def _color(val_str):
    if val_str == "N/A":
        return "dim"
    try:
        ratio = float(val_str) / 5.0
    except (ValueError, TypeError):
        return "dim"
    if ratio >= 0.8:
        return "green"
    if ratio >= 0.6:
        return "yellow"
    return "red"


def display_movies(movies):
    for movie in movies:
        lines = []

        title = f"[bold]{movie.title}[/bold]"
        if movie.year:
            title += f"  [dim]({movie.year})[/dim]"
        lines.append(title)

        lines.append(f"Director: [italic]{movie.director or 'N/A'}[/italic]")
        lines.append("")

        val = movie.letterboxd_rating
        if val != "N/A":
            v = float(val)
            b = _bar(v, 5.0)
            c = _color(val)
            lines.append(
                f"  [{c}]\u25cf[/] Letterboxd: [bold]{v}[/] [dim]{v}/5[/dim]  [{c}]{b}[/]"
            )
        else:
            lines.append(f"  [dim]\u25cb Letterboxd: N/A[/dim]")

        content = "\n".join(lines)
        panel = Panel(
            content,
            border_style="blue",
            padding=(0, 1),
        )
        console.print(panel)
        console.print()
