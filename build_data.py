"""Turn the raw downloads into data/derived/story.json: every series carries its source ids.

Run after the fetch scripts. Stdlib only. Months are 'YYYY-MM' strings.
"""
import csv, json, statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw"
START = "2020-01"


def ym(y, m):
    return f"{y:04d}-{m:02d}"


def fred(sid):
    """FRED csv -> {'YYYY-MM': float} (daily series averaged by month)."""
    by = defaultdict(list)
    for r in csv.DictReader((RAW / "fred" / f"{sid}.csv").open()):
        v = r[sid]
        if v not in ("", "."):
            by[r["observation_date"][:7]].append(float(v))
    return {k: sum(v) / len(v) for k, v in sorted(by.items())}


def rolling(d, n=3):
    """Trailing n-month mean; needs n consecutive months."""
    keys = sorted(d)
    return {k: sum(d[keys[i - j]] for j in range(n)) / n for i, k in enumerate(keys) if i >= n - 1}


def pts(d, start=START, end=None):
    return [[k, round(v, 3)] for k, v in sorted(d.items()) if k >= start and (end is None or k <= end)]


def indeed(path, variable, sector=None):
    by = defaultdict(list)
    for r in csv.DictReader(open(path)):
        if r["variable"] != variable or (sector and r["display_name"] != sector):
            continue
        col = "indeed_job_postings_index_SA" if "indeed_job_postings_index_SA" in r else "indeed_job_postings_index"
        by[r["date"][:7]].append(float(r[col]))
    last = max(by)
    return {k: sum(v) / len(v) for k, v in by.items() if k != last}  # drop the incomplete current month


def jolts_info():
    out = {}
    for s in json.load(open(RAW / "bls_jolts" / "jolts_information.json"))["Results"]["series"]:
        if not s["seriesID"].startswith("JTS51"):  # information sector only
            continue
        out[s["seriesID"][-3:]] = {ym(int(x["year"]), int(x["period"][1:])): float(x["value"]) for x in s["data"] if x["period"].startswith("M")}
    return out


def pct_change(d, base="2020-01"):
    b = d[base]
    return {k: (v / b - 1) * 100 for k, v in d.items()}


def ratio(a, b):
    return {k: a[k] / b[k] for k in a if k in b}


J = jolts_info()
info_open, info_hire, info_lay = J["JOL"], J["HIL"], J["LDL"]
all_open, all_hire = fred("JTSJOL"), fred("JTSHIL")

sw = indeed(RAW / "indeed_hl" / "by_sector_US.csv", "total postings", "Software Development")
allp = indeed(RAW / "indeed_hl" / "aggregate_US.csv", "total postings")

ch = {}
for r in csv.DictReader((ROOT / "data" / "challenger_monthly.csv").open()):
    ch[ym(int(r["year"]), int(r["month"]))] = r

latest_info = max(info_open)  # preliminary month
ch_tot = {k: int(r["total_cuts"]) for k, r in ch.items()}
ch_ai = {k: int(r["ai_cuts"]) for k, r in ch.items() if r["ai_cuts"] and k >= "2026-01"}

peak_sw = max(sw, key=sw.get)
csd, alle = pct_change(fred("CES6054150001")), pct_change(fred("PAYEMS"))
ratio_info = ratio(rolling(info_open), rolling(info_hire))
ratio_all = ratio(rolling(all_open), rolling(all_hire))

def avg(d, a, b):
    v = [x for k, x in d.items() if a <= k <= b]
    return sum(v) / len(v)

story = {
    "generated_from": "data/raw/* (see manifests for fetch dates)",
    "latest_info_month": latest_info,
    "series": {
        "indeed_software": {"sources": ["indeed_hl"], "unit": "index, Feb 2020 = 100", "monthly": pts(sw)},
        "indeed_all": {"sources": ["indeed_hl"], "unit": "index, Feb 2020 = 100", "monthly": pts(allp)},
        "info_openings": {"sources": ["bls_jolts"], "unit": "thousands", "monthly": pts(info_open, "2019-01")},
        "info_hires": {"sources": ["bls_jolts"], "unit": "thousands", "monthly": pts(info_hire, "2019-01")},
        "info_layoffs": {"sources": ["bls_jolts"], "unit": "thousands", "monthly": pts(info_lay, "2019-01")},
        "info_openings_3m": {"sources": ["bls_jolts"], "unit": "thousands, 3-month average", "monthly": pts(rolling(info_open), "2019-03")},
        "info_hires_3m": {"sources": ["bls_jolts"], "unit": "thousands, 3-month average", "monthly": pts(rolling(info_hire), "2019-03")},
        "info_layoffs_3m": {"sources": ["bls_jolts"], "unit": "thousands, 3-month average", "monthly": pts(rolling(info_lay), "2019-03")},
        "ratio_info": {"sources": ["bls_jolts"], "unit": "openings per hire, 3-month average", "monthly": pts(ratio_info, "2019-03")},
        "ratio_all": {"sources": ["fred", "bls_jolts"], "unit": "openings per hire, 3-month average (total nonfarm)", "monthly": pts(ratio_all, "2019-03", latest_info)},
        "fedfunds": {"sources": ["fred"], "unit": "percent", "monthly": pts(fred("FEDFUNDS"), "2019-01")},
        "treasury10": {"sources": ["fred"], "unit": "percent", "monthly": pts(fred("DGS10"), "2019-01")},
        "emp_csd": {"sources": ["fred"], "unit": "percent change from Jan 2020", "monthly": pts(pct_change(fred("CES6054150001")), "2019-01")},
        "emp_all": {"sources": ["fred"], "unit": "percent change from Jan 2020", "monthly": pts(pct_change(fred("PAYEMS")), "2019-01")},
        "challenger_total": {"sources": ["challenger"], "unit": "announced job cuts", "monthly": [[k, v] for k, v in sorted(ch_tot.items())]},
        "challenger_ai": {"sources": ["challenger"], "unit": "cuts citing AI", "monthly": [[k, v] for k, v in sorted(ch_ai.items())]},
    },
    "facts": {
        "indeed_sw_peak_month": peak_sw,
        "indeed_sw_peak": round(sw[peak_sw]),
        "indeed_sw_latest_month": max(sw),
        "indeed_sw_latest": round(sw[max(sw)]),
        "indeed_all_latest": round(allp[max(allp)]),
        "indeed_all_peak_month": max(allp, key=allp.get),
        "indeed_all_peak": round(max(allp.values())),
        "emp_csd_peak_month": max(csd, key=csd.get),
        "emp_csd_peak": round(max(csd.values()), 1),
        "emp_csd_latest": round(csd[max(csd)], 1),
        "emp_all_latest": round(alle[max(alle)], 1),
        "ratio_info_peak_month": max(ratio_info, key=ratio_info.get),
        "ratio_info_peak": round(max(ratio_info.values()), 2),
        "ratio_info_latest": round(ratio_info[max(ratio_info)], 2),
        "ratio_all_latest": round(ratio_all[max(ratio_all)], 2),
        "ratio_all_2019": round(avg(ratio_all, "2019-03", "2019-12"), 2),
        "ratio_info_2019": round(avg(ratio_info, "2019-03", "2019-12"), 2),
        "hires_2019": round(avg(info_hire, "2019-01", "2019-12")),
        "hires_2022": round(avg(info_hire, "2022-01", "2022-12")),
        "hires_last12": round(avg(info_hire, "2025-09", latest_info)) if latest_info >= "2026-08" else None,
        "layoffs_2019": round(avg(info_lay, "2019-01", "2019-12")),
        "layoffs_2026": round(avg(info_lay, "2026-01", latest_info)),
        "challenger_2020": sum(v for k, v in ch_tot.items() if k.startswith("2020")),
        "challenger_2023": sum(v for k, v in ch_tot.items() if k.startswith("2023")),
        "challenger_2024": sum(v for k, v in ch_tot.items() if k.startswith("2024")),
        "challenger_2025": sum(v for k, v in ch_tot.items() if k.startswith("2025")),
        "challenger_2026ytd": sum(v for k, v in ch_tot.items() if k.startswith("2026")),
        "challenger_2026_last": max(ch_tot),
        "challenger_ai_2026ytd": sum(ch_ai.values()),
    },
}
out = ROOT / "data" / "derived"
out.mkdir(exist_ok=True)
(out / "story.json").write_text(json.dumps(story, indent=1))
print(json.dumps(story["facts"], indent=1))

# ---------------- chapter 5: entry-level and the people the headline rate leaves out ----------------
def nyfed(name, col):
    out = {}
    for r in csv.DictReader((RAW / "nyfed_college" / name).open()):
        m, _, y = r["Date"].split("/")
        out[f"{int(y):04d}-{int(m):02d}"] = float(r[col])
    return out

ny_recent = nyfed("college-labor-unemployment-data.csv", "Recent graduates")
ny_all = nyfed("college-labor-unemployment-data.csv", "All workers")
ny_young = nyfed("college-labor-unemployment-data.csv", "Young workers")
ny_under = nyfed("college-labor-underemployment-data.csv", "Recent graduates")
ny_under_all = nyfed("college-labor-underemployment-data.csv", "College graduates")
u3, u6 = fred("UNRATE"), fred("U6RATE")
want = fred("NILFWJN")
marg, disc = fred("LNU05026642"), fred("LNU05026645")
lfpr, epop = fred("LNS11300060"), fred("LNS12300060")
majors = [{"name": r["Major"], "unemp": float(r["Unemployment Rate"]), "under": float(r["Underemployment Rate"])}
          for r in csv.DictReader((RAW / "nyfed_college" / "college-labor-outcomes-by-major-data.csv").open())]
rank = sorted(majors, key=lambda m: -m["unemp"])
fred_end = max(u3)
ny_end = max(ny_recent)
def ym_back(ym, n):
    y, m = int(ym[:4]), int(ym[5:])
    t = y * 12 + (m - 1) - n
    return f"{t // 12:04d}-{t % 12 + 1:02d}"
f12, n12 = ym_back(fred_end, 11), ym_back(ny_end, 11)

story["series"].update({
    "ny_recent": {"sources": ["nyfed_college"], "unit": "percent unemployed", "monthly": pts(ny_recent, "2019-01")},
    "ny_all": {"sources": ["nyfed_college"], "unit": "percent unemployed", "monthly": pts(ny_all, "2019-01")},
    "u3": {"sources": ["fred"], "unit": "percent", "monthly": pts(u3, "2019-01")},
    "u6": {"sources": ["fred"], "unit": "percent", "monthly": pts(u6, "2019-01")},
    "want_job_12m": {"sources": ["fred"], "unit": "thousands, 12-month average", "monthly": pts(rolling(want, 12), "2019-12")},
})
story["majors"] = {"sources": ["nyfed_college"], "year": 2024, "list": majors}
story["facts"].update({
    "ny_end": ny_end, "fred_end": fred_end, "f12_start": f12, "n12_start": n12,
    "recent_2019": round(avg(ny_recent, "2019-01", "2019-12"), 1), "recent_l12": round(avg(ny_recent, n12, ny_end), 1),
    "nyall_2019": round(avg(ny_all, "2019-01", "2019-12"), 1), "nyall_l12": round(avg(ny_all, n12, ny_end), 1),
    "under_2019": round(avg(ny_under, "2019-01", "2019-12")), "under_l12": round(avg(ny_under, n12, ny_end)),
    "u3_2019": round(avg(u3, "2019-01", "2019-12"), 1), "u3_l12": round(avg(u3, f12, fred_end), 1),
    "u6_2019": round(avg(u6, "2019-01", "2019-12"), 1), "u6_l12": round(avg(u6, f12, fred_end), 1),
    "want_2019": round(avg(want, "2019-01", "2019-12")), "want_l12": round(avg(want, f12, fred_end)),
    "marg_2019": round(avg(marg, "2019-01", "2019-12")), "marg_l12": round(avg(marg, f12, fred_end)),
    "disc_2019": round(avg(disc, "2019-01", "2019-12")), "disc_l12": round(avg(disc, f12, fred_end)),
    "lfpr_2019": round(avg(lfpr, "2019-01", "2019-12"), 1), "lfpr_l12": round(avg(lfpr, f12, fred_end), 1),
    "epop_2019": round(avg(epop, "2019-01", "2019-12"), 1), "epop_l12": round(avg(epop, f12, fred_end), 1),
    "cs_unemp": next(m["unemp"] for m in majors if m["name"] == "Computer Science"),
    "cs_under": next(m["under"] for m in majors if m["name"] == "Computer Science"),
    "cs_rank": 1 + [m["name"] for m in rank].index("Computer Science"),
    "ce_rank": 1 + [m["name"] for m in rank].index("Computer Engineering"),
    "major_n": len(majors), "major_median": round(statistics.median(m["unemp"] for m in majors), 1),
})
(out / "story.json").write_text(json.dumps(story, indent=1))
print({k: v for k, v in story["facts"].items() if k.startswith(("recent", "nyall", "u3", "u6", "want", "marg", "disc", "lfpr", "epop", "cs_", "ce_", "major", "under"))})

# ---------------- chapter 6: the quits link in the "staying put" loop ----------------
quits_all_rate = fred("JTSQUR")
info_quits = J["QUL"]
story["series"]["info_quits_3m"] = {"sources": ["bls_jolts"], "unit": "thousands, 3-month average", "monthly": pts(rolling(info_quits), "2019-03")}
lat = story["latest_info_month"]
l12 = ym_back(lat, 11)
story["facts"].update({
    "quits_2019": round(avg(info_quits, "2019-01", "2019-12")), "quits_l12": round(avg(info_quits, l12, lat)),
    "qrate_2019": round(avg(quits_all_rate, "2019-01", "2019-12"), 2), "qrate_l12": round(avg(quits_all_rate, l12, lat), 2),
    "openings_2019": round(avg(info_open, "2019-01", "2019-12")), "openings_l12": round(avg(info_open, l12, lat)),
    "hires_l12_6": round(avg(info_hire, l12, lat)), "l12_start6": l12,
    "sw_2023_05": round(sw["2023-05"]), "sw_2025_07": round(sw["2025-07"]),
})
(out / "story.json").write_text(json.dumps(story, indent=1))
print({k: story["facts"][k] for k in ("quits_2019", "quits_l12", "qrate_2019", "qrate_l12", "openings_2019", "openings_l12", "hires_2019", "hires_l12_6", "sw_2023_05")})
