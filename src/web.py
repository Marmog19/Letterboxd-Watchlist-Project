import os
import tempfile

from flask import Flask, flash, redirect, render_template, request, url_for

from src.config import ROOT, load_env
from src.service import (
    build_tv_movies,
    build_watchlist_movies,
    get_watchlist_csvs,
)

load_env()

app = Flask(
    __name__,
    template_folder=str(ROOT / "templates"),
    static_folder=str(ROOT / "static"),
)
app.secret_key = os.urandom(16)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

ALLOWED_EXT = (".csv",)


def _env_status():
    return {
        "api_key": bool(os.getenv("OMDB_API_KEY")),
        "tmdb_token": bool(os.getenv("TMDB_READ_TOKEN")),
    }


def _error_movies():
    return render_template(
        "tv.html",
        movies=[],
        error="OMDB_API_KEY missing in .env — set it before using this app.",
    )


@app.route("/")
def tv():
    status = _env_status()
    if not status["api_key"]:
        return _error_movies()
    refresh = request.args.get("refresh") == "1"
    try:
        movies = build_tv_movies(
            os.getenv("OMDB_API_KEY"),
            os.getenv("TMDB_READ_TOKEN"),
            refresh=refresh,
        )
    except Exception as exc:
        return render_template("tv.html", movies=[], error=str(exc))
    return render_template("tv.html", movies=movies, refresh=refresh)


@app.route("/watchlist", methods=["GET", "POST"])
def watchlist():
    status = _env_status()
    csvs = get_watchlist_csvs()
    movies = None
    selected = None

    if request.method == "POST":
        if not status["api_key"]:
            return render_template(
                "watchlist.html",
                csvs=csvs,
                movies=None,
                selected=None,
                error="OMDB_API_KEY missing in .env — set it before using this app.",
            )
        refresh = request.form.get("refresh") == "1"
        csv_path = None
        uploaded = request.files.get("csv_file")
        if uploaded and uploaded.filename:
            if not uploaded.filename.lower().endswith(ALLOWED_EXT):
                return render_template(
                    "watchlist.html",
                    csvs=csvs,
                    movies=None,
                    selected=None,
                    error=f"Only CSV files allowed (got {uploaded.filename}).",
                )
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                uploaded.save(tmp.name)
                csv_path = tmp.name
                selected = uploaded.filename
        else:
            picked = request.form.get("csv_pick") or ""
            candidate = (ROOT / picked).resolve()
            if picked and candidate.is_file() and candidate.is_relative_to(ROOT):
                csv_path = candidate
                selected = candidate.name

        if not csv_path:
            return render_template(
                "watchlist.html",
                csvs=csvs,
                movies=None,
                selected=None,
                error="No CSV selected or uploaded.",
            )

        try:
            movies = build_watchlist_movies(
                csv_path,
                os.getenv("OMDB_API_KEY"),
                os.getenv("TMDB_READ_TOKEN"),
                refresh=refresh,
            )
        except Exception as exc:
            return render_template(
                "watchlist.html",
                csvs=csvs,
                movies=None,
                selected=selected,
                error=str(exc),
            )

    return render_template(
        "watchlist.html",
        csvs=csvs,
        movies=movies,
        selected=selected,
        error=None,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
