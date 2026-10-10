"""Render site/sources.html from sources.toml plus each source's fetch manifest."""
import html, json, tomllib
from pathlib import Path

ROOT = Path(__file__).parent
reg = tomllib.loads((ROOT / "sources.toml").read_text())
e = html.escape

def fetched(sid):
    mf = ROOT / "data" / "raw" / sid / "manifest.json"
    if not mf.exists():
        return "not yet fetched"
    items = json.loads(mf.read_text())
    return e(max(i["fetched_at"] for i in items)[:10])

cards = []
for sid, s in reg.items():
    cards.append(f"""<article id="{e(sid)}">
  <h2>{e(s['name'])}</h2>
  <p class="pub">{e(s['publisher'])}</p>
  <dl>
    <dt>Measures</dt><dd>{e(s['measures'])}</dd>
    <dt>Caveat</dt><dd>{e(s['caveat'])}</dd>
    <dt>License</dt><dd>{e(s['license'])}</dd>
    <dt>Retrieved</dt><dd>{fetched(sid)} ({e(s['access'])})</dd>
    <dt>Link</dt><dd><a href="{e(s['url'])}">{e(s['url'])}</a></dd>
  </dl>
</article>""")

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sources</title><link rel="stylesheet" href="assets/style.css"></head>
<body><main><h1>Sources</h1>
<p>Every number on this site comes from one of the sources below. Each chart footer links here.</p>
{''.join(cards)}
</main></body></html>"""
(ROOT / "site").mkdir(exist_ok=True)
(ROOT / "site" / "sources.html").write_text(page)
print(f"wrote site/sources.html ({len(reg)} sources)")
