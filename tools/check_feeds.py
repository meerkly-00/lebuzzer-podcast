#!/usr/bin/env python3
"""Diagnostic de santé des flux RSS du Buzzer.

Lit config/sources_buzzer.yaml et teste chaque flux : code HTTP + nombre
d'items. À lancer depuis un environnement avec accès réseau ouvert
(la prod ou ta machine) — l'environnement Claude Code web bloque les
domaines externes via sa politique réseau.

Usage:
    python3 tools/check_feeds.py
"""

import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parent.parent / "config" / "sources_buzzer.yaml"
UA = "Mozilla/5.0 (compatible; BuzzerFeedCheck/1.0)"
TIMEOUT = 20


def check(url: str) -> tuple[bool, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            text = r.read().decode("utf-8", "ignore")
            nitems = text.count("<item") + text.count("<entry")
            return nitems > 0, f"HTTP {r.getcode()}, {nitems} items"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def main() -> int:
    feeds = yaml.safe_load(CONFIG.read_text())["feeds"]
    dead = []
    for fd in feeds:
        ok, status = check(fd["url"])
        flag = "OK  " if ok else "MORT"
        print(f"{flag} | {fd.get('source','?'):32} | {status}")
        if not ok:
            dead.append((fd.get("source", "?"), status, fd["url"]))
        time.sleep(0.3)

    print(f"\n{len(dead)} flux mort(s)/vide(s) sur {len(feeds)}")
    for name, status, url in dead:
        print(f"  - {name:32} {status}\n      {url}")
    return 1 if dead else 0


if __name__ == "__main__":
    sys.exit(main())
