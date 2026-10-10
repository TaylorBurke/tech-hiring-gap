"""Helpers to read the saved Challenger feed pages as plain text per post."""
import glob, html, re
import xml.etree.ElementTree as ET
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw" / "challenger"
NS = "{http://purl.org/rss/1.0/modules/content/}encoded"

def posts():
    seen = {}
    for f in sorted(glob.glob(str(RAW / "feed_*.xml"))):
        for it in ET.parse(f).getroot().iter("item"):
            link = it.findtext("link")
            body = re.sub(r"<[^>]+>", " ", it.findtext(NS) or "")
            seen[link] = {"title": it.findtext("title"), "date": it.findtext("pubDate"), "link": link,
                          "text": html.unescape(re.sub(r"\s+", " ", body))}
    return list(seen.values())
