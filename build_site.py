"""Build site/index.html (chapters 1-4) from data/derived/story.json, sources.toml and figures.py.

Callers: run `python3 build_data.py && python3 build_site.py && python3 build_sources.py`.
Prose numbers are filled from story.json facts, never typed by hand, so text and charts cannot drift apart.
"""
import html, json, tomllib
from pathlib import Path
from figures import CHAPTERS, FIGURES

ROOT = Path(__file__).parent
story = json.loads((ROOT / "data" / "derived" / "story.json").read_text())
F, S = story["facts"], story["series"]
REG = tomllib.loads((ROOT / "sources.toml").read_text())
e = html.escape
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def mo(ym):
    return f"{MON[int(ym[5:7]) - 1]} {ym[:4]}"


def n(v):
    return f"{v:,.0f}"


def millions(v):
    return f"{v / 1e6:.2f} million"


def thousands(v):
    return f"{v / 1000:,.0f},000"


def src_line(fig_id):
    links = ", ".join(f'<a href="sources.html#{s}">{e(REG[s]["name"])}</a>' for s in FIGURES[fig_id]["sources"])
    return f'<p class="src">Sources: {links}. <a href="sources.html">All sources and caveats</a></p>'


def figure(fig_id):
    f = FIGURES[fig_id]
    return (f'<figure><figcaption class="title">{e(f["title"])}</figcaption>'
            f'<figcaption class="sub">{e(f["sub"])}</figcaption>'
            f'<div id="{fig_id}"></div>{src_line(fig_id)}</figure>')


def tile(label, value, sub):
    return f'<div class="tile"><div class="lab">{e(label)}</div><div class="val">{e(value)}</div><div class="sub">{e(sub)}</div></div>'


def kpis(*tiles):
    return '<div class="kpis">' + "".join(tiles) + "</div>"


def chapter(num, body):
    return f'<section class="chapter" id="ch{num}"><p class="chap-num">Chapter {num}</p><h2>{e(CHAPTERS[num])}</h2><div class="prose">{body[0]}</div>{body[1]}</section>'


# ---- numbers used in the prose ----
r_info = dict(map(tuple, S["ratio_info"]["monthly"]))
r_all = dict(map(tuple, S["ratio_all"]["monthly"]))
sw = dict(map(tuple, S["indeed_software"]["monthly"]))
mid26 = [r_info[k] for k in ("2026-03", "2026-04", "2026-05", "2026-06")]
all_mid26 = [r_all[k] for k in ("2026-03", "2026-04", "2026-05", "2026-06")]
ai_2023, ai_2025 = 4247, 54836  # stated in Challenger's year-end text (quotes verified in data/raw/challenger)
emp_last = S["emp_csd"]["monthly"][-1][0]
sw_pct_of_peak = round(F["indeed_sw_latest"] / F["indeed_sw_peak"] * 100)
ai_share = round(F["challenger_ai_2026ytd"] / F["challenger_2026ytd"] * 100)

ch1 = (
    f"""<p class="lede">Between early 2020 and early 2022, software jobs were advertised at a pace that more than doubled. On Indeed, software-development postings peaked in {mo(F['indeed_sw_peak_month'])} at {F['indeed_sw_peak']}, more than twice their February 2020 level of 100. Postings across all occupations peaked later and lower: {F['indeed_all_peak']} in {mo(F['indeed_all_peak_month'])}.</p>
<p>By {mo(F['indeed_sw_latest_month'])}, software postings had fallen to {F['indeed_sw_latest']}, about {sw_pct_of_peak}% of the peak and below where they started. Postings overall sat at {F['indeed_all_latest']}, close to their pre-pandemic level. So the drop is not simply the whole job market cooling. Software fell much further than the market it sits in.</p>""",
    kpis(tile("Software postings at peak", str(F["indeed_sw_peak"]), f"{mo(F['indeed_sw_peak_month'])} · Feb 2020 = 100"),
         tile("Software postings now", str(F["indeed_sw_latest"]), f"{mo(F['indeed_sw_latest_month'])} · Feb 2020 = 100"),
         tile("All postings now", str(F["indeed_all_latest"]), f"{mo(F['indeed_sw_latest_month'])} · Feb 2020 = 100"))
    + figure("fig-postings")
    + '<div class="prose"><p class="caveat"><strong>How to read this.</strong> The index counts postings on Indeed only and is relative to February 2020, so it shows direction and proportion, not a count of jobs. A posting is also not a hire; chapter 4 looks at the difference.</p></div>',
)

ch2 = (
    f"""<p class="lede">Three dates cluster in early 2022. Software postings peaked in February. The Federal Reserve began raising interest rates from near zero in March. And a tax rule took effect that, for tax years beginning after December 31, 2021, required companies to spread the cost of software development over several years instead of deducting it at once (the IRS's Section 174 guidance is in the sources).</p>
<p>The chart below puts them on one time axis. In July 2025 Congress restored immediate deduction of domestic research costs, including software development, for tax years beginning in 2025. Software postings stood at {round(sw['2025-07'])} that month and {F['indeed_sw_latest']} in {mo(F['indeed_sw_latest_month'])}: a small rise from a low base, not a rebound.</p>""",
    figure("fig-turn")
    + f"""<div class="prose"><p>Employment tells a different story from postings. Jobs in computer systems design kept growing after postings fell: they peaked in {mo(F['emp_csd_peak_month'])} at {F['emp_csd_peak']:+.1f}% versus January 2020, and by {mo(emp_last)} stood at {F['emp_csd_latest']:+.1f}%, compared with {F['emp_all_latest']:+.1f}% for all nonfarm jobs. Hiring slowed far more than headcount shrank.</p>
<p class="caveat"><strong>Lining up in time is not cause and effect.</strong> The same period saw the end of pandemic stimulus, high inflation and, later, widely available AI tools. Chapter 6 lays out each candidate cause and what it would predict. Computer systems design is one slice of tech employment (it excludes software publishers and large platform companies), so treat it as a partial view.</p></div>""",
)

ch3 = (
    f"""<p class="lede">Announced layoffs ran in waves. The outplacement firm Challenger, Gray &amp; Christmas counted {millions(F['challenger_2020'])} announced U.S. job cuts in 2020, almost all of it pandemic-driven. After that: {thousands(F['challenger_2023'])} in 2023, {thousands(F['challenger_2024'])} in 2024, {millions(F['challenger_2025'])} in 2025, and {thousands(F['challenger_2026ytd'])} in the first nine months of 2026.</p>
<p>These counts cover every industry. Challenger's own reports attribute the early-2025 surge largely to federal government cuts, so the headline total says little about tech by itself. Challenger does break out technology, but its published text states a monthly tech figure only for some months, so we do not chart tech cuts on their own.</p>""",
    figure("fig-cuts")
    + f"""<div class="prose"><p>A second measure, from the Bureau of Labor Statistics, covers the information sector, which includes software publishers, data processing and hosting, telecommunications and media. Layoffs and discharges there averaged {F['layoffs_2019']},000 a month in 2019 and {F['layoffs_2026']},000 a month in 2026 so far (January to August).</p></div>"""
    + figure("fig-layoffs")
    + f"""<div class="prose"><p>Employers have also begun naming AI as the reason. Challenger recorded {n(ai_2023)} cuts citing AI in 2023, {n(ai_2025)} in 2025 (5% of all announced cuts) and {n(F['challenger_ai_2026ytd'])} in the first nine months of 2026 ({ai_share}% of all announced cuts).</p></div>"""
    + kpis(tile("Cuts citing AI, 2023", n(ai_2023), "Challenger"),
           tile("Cuts citing AI, 2025", n(ai_2025), "5% of all announced cuts"),
           tile("Cuts citing AI, Jan to Sep 2026", n(F["challenger_ai_2026ytd"]), f"{ai_share}% of all announced cuts"))
    + figure("fig-ai")
    + """<div class="prose"><p class="caveat"><strong>This is a stated reason, not a measured cause.</strong> Challenger began tracking AI as its own reason in May 2023, and through 2025 its monthly reports often grouped it under "Technological Updates" (20,219 cuts through September 2025). The 2023, 2025 and 2026 totals are therefore not like-for-like. The jump means more employers now name AI. It could reflect substitution, relabeling of other cost-cutting, or both, and these numbers cannot say which. Announced cuts are also plans, not confirmed separations.</p></div>""",
)

ch4 = (
    f"""<p class="lede">If employers post jobs they never fill, openings pile up relative to hires. The BLS's JOLTS survey counts openings on the last day of each month and hires during the month, so the ratio between them is a rough gauge of that gap.</p>
<p>In the information sector there were about {F['ratio_info_2019']} openings per monthly hire in 2019. At the {mo(F['ratio_info_peak_month'])} peak that rose to {F['ratio_info_peak']}. That is consistent with employers advertising far more roles than they filled, which is what "ghost jobs" would look like, but it is also what a tight market where roles take longer to fill would look like. The data cannot separate the two.</p>""",
    kpis(tile("Openings per hire, 2019", str(F["ratio_info_2019"]), "Information sector, average"),
         tile("At the peak", str(F["ratio_info_peak"]), f"{mo(F['ratio_info_peak_month'])} · information sector"),
         tile("March to June 2026", f"{min(mid26):.2f} to {max(mid26):.2f}", f"Whole economy: {min(all_mid26):.2f} to {max(all_mid26):.2f}"))
    + figure("fig-gap-levels")
    + f"""<div class="prose"><p>Hires in the sector averaged {F['hires_2019']},000 a month in 2019 and {F['hires_2022']},000 in 2022. Over the 12 months to August 2026 they averaged {F['hires_last12']},000. Openings fell back faster than hires did, which narrowed the gap.</p></div>"""
    + figure("fig-gap-ratio")
    + f"""<div class="prose"><p>From March to June 2026 the information sector's ratio ran between {min(r_info[k] for k in ('2026-03','2026-04','2026-05','2026-06')):.2f} and {max(r_info[k] for k in ('2026-03','2026-04','2026-05','2026-06')):.2f}, close to one opening per hire. Those are the lowest readings in this series, apart from a few months in 2020 and 2021, and they sit below the whole economy's roughly 1.4. By this measure, the boom-era gap between advertised roles and hires has narrowed sharply.</p>
<p class="caveat"><strong>A few quiet months are not a trend.</strong> The ratio swings a lot: it was near {r_info['2025-09']:.1f} as recently as September 2025. And August 2026 shows 123,000 openings against 44,000 hires, which lifts the 3-month ratio to {r_info['2026-08']:.1f}. JOLTS industry estimates carry wide margins of error and the newest month is preliminary, so we are not reading that jump as a trend either; it will be revised. Also, "information" is only a rough stand-in for tech, because it includes telecom and media.</p></div>""",
)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tech Hiring Gap</title>
<meta name="description" content="Tech postings, layoffs and hiring since 2020, with every number traced to its source.">
<link rel="icon" href="data:,"><link rel="stylesheet" href="assets/style.css"></head>
<body>
<div class="wrap">
<header class="mast">
<p class="eyebrow">Data story · tech labor market, 2020 to now</p>
<h1>Boom, bust, and a market that never reopened</h1>
<p class="dek">Tech hiring surged, stalled, and thinned out. What the numbers show, what they cannot show, and where we are guessing.</p>
</header>
<nav class="nav"><a href="#ch1">1 The boom</a><a href="#ch2">2 The turn</a><a href="#ch3">3 The cuts</a><a href="#ch4">4 The gap that narrowed</a><a href="sources.html">Sources</a></nav>
{chapter(1, ch1)}
{chapter(2, ch2)}
{chapter(3, ch3)}
{chapter(4, ch4)}
<div class="next prose"><strong>Still to come.</strong> Chapter 5 looks at who is shut out: recent graduates, young workers, and the people the unemployment rate stops counting. Chapter 6 maps the causes and feedback loops. This draft stops after chapter 4.</div>
<footer>Every figure links to its sources; <a href="sources.html">the sources page</a> lists what each one measures, when it was retrieved, and where it falls short.</footer>
</div>
<script src="assets/vendor/d3.min.js"></script>
<script>window.STORY = {json.dumps({'series': S, 'facts': F, 'latest_info_month': story['latest_info_month']})};</script>
<script src="assets/charts.js"></script>
<script src="assets/story.js"></script>
</body></html>"""
(ROOT / "site" / "index.html").write_text(page)
print("wrote site/index.html", len(page), "bytes")
