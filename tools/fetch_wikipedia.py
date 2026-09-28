"""One-time, online-only helper: download Wikipedia articles into vault/raw/.

Saves each article's plain-text extract unchanged and records provenance
(URL, revision id, retrieval date, license) in sources.json.
Not part of the offline harness.
"""
import datetime
import json
import pathlib
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "vault" / "raw"
CATALOG = ROOT / "sources.json"

# source_id -> Wikipedia title
ARTICLES = {
    "wiki-robotaxi": "Robotaxi",
    "wiki-waymo": "Waymo",
    "wiki-zoox": "Zoox (company)",
    "wiki-h1b": "H-1B visa",
    "wiki-opt": "Optional Practical Training",
}

API = "https://en.wikipedia.org/w/api.php"
UA = "personal-wiki-class-assignment/1.0"


def fetch(title: str) -> dict:
    params = {
        "action": "query", "prop": "extracts|revisions", "rvprop": "ids",
        "explaintext": 1, "redirects": 1, "format": "json", "titles": title,
    }
    req = urllib.request.Request(f"{API}?{urllib.parse.urlencode(params)}",
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        page = next(iter(json.load(r)["query"]["pages"].values()))
    return {"title": page["title"], "text": page["extract"],
            "revid": page["revisions"][0]["revid"]}


def main() -> None:
    catalog = json.loads(CATALOG.read_text()) if CATALOG.exists() else {}
    today = datetime.date.today().isoformat()
    for sid, title in ARTICLES.items():
        page = fetch(title)
        filename = f"{page['title']} - Wikipedia.md"
        (RAW / filename).write_text(page["text"], encoding="utf-8")
        catalog[sid] = {
            "file": f"raw/{filename}",
            "title": page["title"],
            "kind": "wikipedia",
            "url": f"https://en.wikipedia.org/w/index.php?oldid={page['revid']}",
            "revision": page["revid"],
            "retrieved": today,
            "license": "CC BY-SA 4.0",
        }
        print(f"saved {filename} ({len(page['text'])} chars)")
    CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
