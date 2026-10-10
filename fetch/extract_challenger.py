"""Pull monthly figures out of the saved Challenger reports into data/challenger_monthly.csv.

Every value keeps the verbatim sentence it came from plus the report URL, so the sources page
can show exactly where a number came from. Blanks mean the report did not state the figure in a form
the patterns match; fill them in data/challenger_overrides.csv (same columns) after reading the report.
"""
import csv, re
from pathlib import Path
from _challenger_text import posts

ROOT = Path(__file__).resolve().parent.parent
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
MRE = "|".join(MONTHS)
NUM = r"(\d{1,3}(?:,\d{3})+|\d{3,})"

TOTAL = re.compile(rf"[^.]*?-based (?:employers|companies) announced {NUM} (?:job )?cuts in ({MRE})[^.]*\.")
AI = re.compile(rf"[^.]*(?:Artificial Intelligence|\bAI\b)[^.]*?(?:cited for|led all reasons for job cuts, with|with) {NUM}[^.]*? (?:job )?cuts? in ({MRE})[^.]*\.|[^.]*In ({MRE}), Artificial Intelligence[^.]*?(?:with|for) {NUM}[^.]*\.")
TECH = re.compile(rf"[^.]*Technology[^.]*?(?:announced|led)[^.]*?{NUM} (?:job )?cuts in ({MRE})[^.]*\.")

def month_year(name, post_date):
    """Report month name -> (year, month); January releases cover December, so roll back if needed."""
    m = MONTHS.index(name) + 1
    y = int(post_date[12:16])
    pm = MONTHS.index({"Jan":"January","Feb":"February","Mar":"March","Apr":"April","May":"May","Jun":"June","Jul":"July","Aug":"August","Sep":"September","Oct":"October","Nov":"November","Dec":"December"}[post_date[8:11]]) + 1
    return (y - 1 if m > pm else y, m)

rows = {}
for p in posts():
    t = p["text"]
    m = TOTAL.search(t)
    if not m:
        continue
    key = month_year(m.group(2), p["date"])
    r = rows.setdefault(key, {"year": key[0], "month": key[1], "report_url": p["link"], "report_date": p["date"][5:16]})
    r["total_cuts"], r["total_quote"] = m.group(1).replace(",", ""), m.group(0).strip()[:300]
    a = AI.search(t)
    if a:
        g = a.groups(); num = g[0] or g[3]; mon = g[1] or g[2]
        if month_year(mon, p["date"]) == key:
            r["ai_cuts"], r["ai_quote"] = num.replace(",", ""), a.group(0).strip()[:300]
    k = TECH.search(t)
    if k and month_year(k.group(2), p["date"]) == key:
        r["tech_cuts"], r["tech_quote"] = k.group(1).replace(",", ""), k.group(0).strip()[:300]

FIELDS = ["year","month","total_cuts","tech_cuts","ai_cuts","report_date","report_url","total_quote","tech_quote","ai_quote"]
out = ROOT / "data" / "challenger_monthly.csv"
out.parent.mkdir(exist_ok=True)
ov = ROOT / "data" / "challenger_overrides.csv"
if ov.exists():
    for o in csv.DictReader(ov.open()):
        rows.setdefault((int(o["year"]), int(o["month"])), {}).update({k: v for k, v in o.items() if v})
with out.open("w", newline="") as f:
    w = csv.DictWriter(f, FIELDS, restval="")
    w.writeheader()
    for k in sorted(rows):
        w.writerow(rows[k])
n = len(rows)
print(f"{n} months; total {sum('total_cuts' in r for r in rows.values())}, tech {sum('tech_cuts' in r for r in rows.values())}, ai {sum('ai_cuts' in r for r in rows.values())}")
