import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / ".cache"
ENV_FILE = ROOT / ".env"


def load_env(path=None):
    path = Path(path) if path else ENV_FILE
    if not path.exists():
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
