"""Challenger, Gray & Christmas monthly job-cuts reports, via the site's RSS feed (full text, 10 posts/page).

Raw feed pages stay in data/raw/challenger/ (git-ignored): we cite and link, we do not redistribute.
Stops once a page reaches back before 2020.
"""
import xml.etree.ElementTree as ET
from common import download

FEED = "https://www.challengergray.com/blog/category/job-cuts-report/feed/"
page = 1
while True:
    url = FEED if page == 1 else f"{FEED}?paged={page}"
    body = download("challenger", f"feed_{page:02d}.xml", url)
    dates = [i.findtext("pubDate") for i in ET.fromstring(body).iter("item")]
    if not dates or int(dates[-1][12:16]) < 2020:
        break
    page += 1
