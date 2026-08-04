from dataclasses import dataclass, field


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


def parse_omdb_ratings(data):
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
