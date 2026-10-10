"""Hand-entered Challenger values for months the regexes miss.

Each entry is (year, month, field, value). The value must appear verbatim (with thousands commas)
in a saved report posted in the following two months, or this script fails: nothing unverified is saved.
The quote stored is the sentence that contains it.
"""
import csv, re
from pathlib import Path
from _challenger_text import posts

ROOT = Path(__file__).resolve().parent.parent
MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

TOTALS = {(2020,1):67735,(2020,2):56660,(2020,3):222288,(2020,4):671129,(2020,5):397016,(2020,6):170219,
    (2020,7):262649,(2020,8):115762,(2020,9):118804,(2020,10):80666,(2020,11):64797,(2020,12):77030,
    (2021,1):79552,(2021,2):34531,(2021,3):30603,(2021,4):22913,(2021,5):24586,(2021,6):20476,
    (2021,9):17895,(2021,10):22822,(2021,11):14875,(2021,12):19052,(2022,1):19064}
TECH = {(2020,2):10218,(2021,9):1546,(2021,11):1980,(2023,1):41829,(2023,2):21387,(2023,7):4738,
    (2023,11):5049,(2024,2):12412,(2025,11):12377}

def report_window(y, m):
    """Posts dated in the month after (y, m) or the one after that."""
    ny, nm = (y + (m == 12), m % 12 + 1)
    nny, nnm = (ny + (nm == 12), nm % 12 + 1)
    want = {(ny, nm), (nny, nnm)}
    return [p for p in posts() if (int(p["date"][12:16]), MON.index(p["date"][8:11]) + 1) in want]

rows = {}
for field, table in (("total_cuts", TOTALS), ("tech_cuts", TECH)):
    for (y, m), v in table.items():
        s = f"{v:,}"
        for p in report_window(y, m):
            hit = re.search(rf"[^.]*\b{s}\b[^.]*\.", p["text"])
            if hit:
                r = rows.setdefault((y, m), {"year": y, "month": m, "report_url": p["link"], "report_date": p["date"][5:16]})
                r[field] = v
                r[field.split("_")[0] + "_quote"] = hit.group(0).strip()[:300]
                break
        else:
            raise SystemExit(f"UNVERIFIED {field} {y}-{m:02d} = {s}: not found in any following report")

fields = ["year","month","total_cuts","tech_cuts","ai_cuts","report_date","report_url","total_quote","tech_quote","ai_quote"]
with (ROOT / "data" / "challenger_overrides.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fields, restval="")
    w.writeheader()
    for k in sorted(rows):
        w.writerow(rows[k])
print(f"{len(rows)} months verified and written")
