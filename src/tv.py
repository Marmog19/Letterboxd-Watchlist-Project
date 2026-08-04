import gzip
import io
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.cache import cached_session

XMLTV_URL = "https://epgshare01.online/epgshare01/epg_ripper_IT1.xml.gz"
ROME_TZ = ZoneInfo("Europe/Rome")
TV_TTL = timedelta(hours=12)

session = cached_session("tv")


def _format_time(start):
    try:
        dt = datetime.strptime(start.strip(), "%Y%m%d%H%M%S %z")
    except ValueError:
        return "?"
    return dt.astimezone(ROME_TZ).strftime("%H:%M")


def fetch_xmltv(url=XMLTV_URL, timeout=30, refresh=False):
    resp = session.get(
        url, timeout=timeout, expire_after=TV_TTL, force_refresh=refresh
    )
    with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as f:
        return f.read()


def get_tv_listings(url=XMLTV_URL, today=None, refresh=False):
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

    listings = {}
    for prog in root.findall("programme"):
        start = prog.get("start", "")
        if not start.startswith(today):
            continue

        categories = [c.text or "" for c in prog.findall("category")]
        if not any("film" in c.lower() for c in categories):
            continue

        title_el = prog.find("title")
        if title_el is None:
            continue
        title = (title_el.text or "").strip()
        if not title:
            continue

        cid = prog.get("channel", "")
        channel = channels.get(cid, cid)
        listings[title.lower()] = f"{_format_time(start)} on {channel}"

    return listings
