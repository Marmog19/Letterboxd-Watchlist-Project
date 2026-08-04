import random
import time

from requests_cache import CachedSession

from src.config import CACHE_DIR


def _strip_vary(resp, **kwargs):
    resp.headers.pop("Vary", None)
    return resp


def cached_session(name, expire_after=-1):
    CACHE_DIR.mkdir(exist_ok=True)
    session = CachedSession(
        str(CACHE_DIR / f"{name}.sqlite"),
        backend="sqlite",
        expire_after=expire_after,
    )
    session.hooks["response"].append(_strip_vary)
    return session


def rate_limited_get(session, delay, *args, **kwargs):
    resp = session.get(*args, **kwargs)
    if not resp.from_cache:
        time.sleep(delay + random.random() * delay)
    return resp
