import gzip
import io
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.cache import cached_session
from src.config import ROOT
from src.models import TVProgramme

XMLTV_URL = "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz"
ROME_TZ = ZoneInfo("Europe/Rome")
TV_TTL = timedelta(hours=12)
CHANNELS_FILE = ROOT / "channels.txt"
MIN_FILM_RUNTIME = 75.0

FILM_GENRES = {
    "drammatico", "commedia", "azione", "crime", "sentimentale", "avventura",
    "poliziesco", "commedia romantica", "azione & avventura", "giallo and crime",
    "horror", "commedia brillante", "romantico", "fantastico", "biografico",
    "cinema italiano", "thriller", "guerra", "storico", "western", "comico",
    "cinema autore", "restaurato", "paranormale", "poliziottesco", "passionale",
}
NON_FILM_CATEGORIES = {
    "soap opera", "sit-com", "sit com", "intrattenimento", "informazione",
    "notiziario", "news", "telegiornale", "varietà", "magazine", "talk show",
    "attualita", "attualità", "lifestyle", "scienza & natura", "scienza e tecnologia",
    "documentario", "arte e cultura", "approfondimento", "quiz", "natura", "storia",
    "viaggi", "storia miti e religioni", "talent show", "il regno animale",
    "religioso", "musica", "musica & ballo", "mondo e tendenze", "anime", "show",
    "reality show", "viaggi & avventure", "per famiglie & ragazzi", "altro",
    "fiction", "gossip",
}
SERIES_MARKER = re.compile(
    r"stag\.?\s*\d+|ep\.?\s*\d+|s\d+e\d+|\bstagione\s*\d+|\bsp\b|\bpuntata\b|\bepisodio\b",
    re.I,
)

session = cached_session("tv")

_TIME_FMT = "%Y%m%d%H%M%S %z"


def _parse_time(stamp):
    try:
        return datetime.strptime(stamp.strip(), _TIME_FMT).astimezone(ROME_TZ)
    except ValueError:
        return None


def _load_channels():
    whitelist = set()
    if CHANNELS_FILE.exists():
        with open(CHANNELS_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    whitelist.add(line)
    return whitelist


def _classify(prog, duration_min):
    cats = [c.lower().strip() for c in prog.categories]
    if any(c in NON_FILM_CATEGORIES for c in cats):
        return None
    if prog.has_episode or SERIES_MARKER.search(prog.title):
        return None
    if "film" in cats:
        return "high"
    if any(c in FILM_GENRES for c in cats):
        if duration_min is not None and duration_min >= MIN_FILM_RUNTIME:
            return "high"
        return None
    if prog.director and duration_min is not None and duration_min >= MIN_FILM_RUNTIME:
        return "medium"
    if duration_min is not None and duration_min >= MIN_FILM_RUNTIME:
        return "unsure"
    return None


def fetch_xmltv(url=XMLTV_URL, timeout=30, refresh=False):
    resp = session.get(
        url, timeout=timeout, expire_after=TV_TTL, force_refresh=refresh
    )
    with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as f:
        return f.read()


def get_tv_listings(url=XMLTV_URL, today=None, refresh=False, tmdb_token=None):
    today = today or datetime.now(ROME_TZ).strftime("%Y%m%d")
    xml_bytes = fetch_xmltv(url, refresh=refresh)
    root = ET.fromstring(xml_bytes)

    channels = {}
    for ch in root.findall("channel"):
        cid = ch.get("id", "")
        name_el = ch.find("display-name")
        if name_el is not None and name_el.text:
            name = name_el.text.strip()
            clean = re.sub(r"\s+\d+$", "", name).strip() or name
            channels[cid] = clean

    whitelist = _load_channels()

    listings = {}
    for prog in root.findall("programme"):
        start = prog.get("start", "")
        if not start.startswith(today):
            continue

        cid = prog.get("channel", "")
        if whitelist and cid not in whitelist:
            continue

        title_el = prog.find("title")
        if title_el is None:
            continue
        title = (title_el.text or "").strip()
        if not title:
            continue

        categories = [c.text or "" for c in prog.findall("category")]
        credits = prog.find("credits")
        director = ""
        if credits is not None:
            dir_el = credits.find("director")
            if dir_el is not None and dir_el.text:
                director = dir_el.text.strip()
        has_episode = bool(prog.findall("episode-num"))

        start_dt = _parse_time(start)
        stop_dt = _parse_time(prog.get("stop", ""))
        if start_dt is None or stop_dt is None:
            continue
        duration_min = (stop_dt - start_dt).total_seconds() / 60

        programme = TVProgramme(
            title=title,
            channel=channels.get(cid, cid),
            start=start_dt,
            stop=stop_dt,
            categories=categories,
            director=director,
            has_episode=has_episode,
        )

        level = _classify(programme, duration_min)
        if level is None:
            continue
        if level == "unsure":
            if not tmdb_token or not _is_tmdb_movie(title, tmdb_token, refresh):
                continue

        listings.setdefault(title.lower(), []).append(programme)

    return listings


def _is_tmdb_movie(title, tmdb_token, refresh):
    try:
        from src.tmdb import get_tmdb_movie

        movie = get_tmdb_movie(title, tmdb_token, refresh=refresh)
        return bool(movie and movie[2] >= MIN_FILM_RUNTIME)
    except Exception:
        return False