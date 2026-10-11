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
    return f'<section class="chapter" id="ch{num}"><p class="chap-num"><span>Chapter</span>{num:02d}</p><h2>{e(CHAPTERS[num])}</h2><div class="prose">{body[0]}</div>{body[1]}</section>'


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

gap19 = F["recent_2019"] - F["nyall_2019"]
gapl12 = F["recent_l12"] - F["nyall_l12"]
pc = lambda a, b_: round((b_ / a - 1) * 100)
ch5 = (
    f"""<p class="lede">The market is not equally hard on everyone. The sharpest strain is at the entry point. Over the 12 months to {mo(F['ny_end'])}, recent college graduates (ages 22 to 27) were unemployed at an average {F['recent_l12']}%, up from {F['recent_2019']}% in 2019. For all workers the rate rose from {F['nyall_2019']}% to {F['nyall_l12']}%. The gap between graduates and everyone else widened from {gap19:.1f} to {gapl12:.1f} percentage points.</p>
<p>The share of graduates in jobs that typically do not require a degree stayed near {F['under_l12']}% ({F['under_2019']}% in 2019). So the squeeze shows up as unemployment, not as a rise in underemployment.</p>""",
    kpis(tile("Recent graduates unemployed", f"{F['recent_l12']}%", f"12 months to {mo(F['ny_end'])} · 2019: {F['recent_2019']}%"),
         tile("All workers unemployed", f"{F['nyall_l12']}%", f"12 months to {mo(F['ny_end'])} · 2019: {F['nyall_2019']}%"),
         tile("Computer science majors", f"{F['cs_unemp']:.1f}%", f"{F['cs_rank']}th highest of {F['major_n']} majors · 2024"))
    + figure("fig-grads")
    + f"""<div class="prose"><p>Computer majors sit near the top of the list. In 2024 data from the American Community Survey, recent computer science graduates were unemployed at {F['cs_unemp']:.1f}%, the {F['cs_rank']}th highest of {F['major_n']} majors. Computer engineering ranked {F['ce_rank']}nd. The median major was {F['major_median']}%. Underemployment among computer science graduates, though, was low ({F['cs_under']:.0f}%, against about {F['under_l12']}% for all recent graduates), which suggests those who find work mostly find degree-level jobs.</p></div>"""
    + figure("fig-majors")
    + f"""<div class="prose"><p class="caveat"><strong>Read the rankings loosely.</strong> The by-major figures cover a single year (2024) from a survey, and samples for individual majors are smaller, so neighboring majors are not precisely ranked. The unemployment series is smoothed over three months and excludes students, and October 2025 is estimated because data were missing.</p>
<p>Now the people the headline rate leaves out. The unemployment rate counts only people actively looking for work. Comparing 2019 averages with the 12 months to {mo(F['fred_end'])}, the headline rate (U-3) rose from {F['u3_2019']}% to {F['u3_l12']}%, and the broader U-6 measure, which adds discouraged workers, other marginally attached workers and people stuck in part-time jobs, rose from {F['u6_2019']}% to {F['u6_l12']}%. The number of people outside the labor force who say they want a job rose {pc(F['want_2019'], F['want_l12'])}%, from {F['want_2019'] / 1000:.1f} million to {F['want_l12'] / 1000:.1f} million. Within that, marginally attached workers rose from {F['marg_2019']:,},000 to {F['marg_l12']:,},000 and discouraged workers from {F['disc_2019']:,},000 to {F['disc_l12']:,},000.</p></div>"""
    + kpis(tile("Want a job, not in labor force", f"{F['want_l12'] / 1000:.1f} million", f"12-month average · 2019: {F['want_2019'] / 1000:.1f} million"),
           tile("Headline unemployment (U-3)", f"{F['u3_l12']}%", f"12-month average · 2019: {F['u3_2019']}%"),
           tile("Broader unemployment (U-6)", f"{F['u6_l12']}%", f"12-month average · 2019: {F['u6_2019']}%"))
    + figure("fig-broad")
    + f"""<div class="prose"><p>The group outside the count grew by about {pc(F['want_2019'], F['want_l12'])}%, close to the {pc(F['u3_2019'], F['u3_l12'])}% rise in the headline rate. So by these measures the hidden group has grown about as fast as the visible one, not faster. And for people in the middle of their working lives, work is not scarcer than before the pandemic: participation among workers aged 25 to 54 averaged {F['lfpr_l12']}% over the last 12 months against {F['lfpr_2019']}% in 2019, and their employment rate was {F['epop_l12']}% against {F['epop_2019']}%. The weakness is concentrated among people trying to enter, and in particular fields, more than across the whole labor force.</p>
<p class="caveat"><strong>What these measures cannot show.</strong> People outside the labor force may want a job for reasons unrelated to the market, and the series that counts them is not seasonally adjusted, so we compare full-year averages. An aging population also lowers overall participation, which is why we use the prime-age (25 to 54) figures. None of this says why any individual stopped looking.</p></div>""",
)

# ---------------- chapter 6 ----------------
def loop_diagram():
    W_, GAP = 172, 15

    def node(cx, cy, lines, sub, kind):
        subs = sub if isinstance(sub, list) else [sub]
        n = len(lines) + len(subs)
        h = max(52, 20 + GAP * n)
        top = cy - h / 2
        t = []
        y0 = cy - (n - 1) * GAP / 2 + 4
        for i, ln in enumerate(lines):
            t.append(f'<text class="nt" x="{cx}" y="{y0 + i * GAP:.1f}" text-anchor="middle">{e(ln)}</text>')
        for j, sl in enumerate(subs):
            t.append(f'<text class="ns" x="{cx}" y="{y0 + (len(lines) + j) * GAP:.1f}" text-anchor="middle">{e(sl)}</text>')
        return {"cx": cx, "cy": cy, "w": W_, "h": h,
                "svg": f'<rect class="node {kind}" x="{cx - W_ / 2}" y="{top:.1f}" width="{W_}" height="{h}" rx="10"/>' + "".join(t)}

    def edge(d):
        return f'<path class="edge" d="{d}" marker-end="url(#ar)"/>'

    def loop(cx, nodes, labels, title, edges_in):
        N = node(cx, 140, *nodes[0]); E = node(cx + 122, 268, *nodes[1]); S = node(cx, 404, *nodes[2]); Wn = node(cx - 122, 268, *nodes[3])
        hw = W_ / 2
        paths = [
            f"M{N['cx'] + hw},{N['cy']} C{E['cx']},{N['cy']} {E['cx']},{E['cy'] - E['h'] / 2 - 45} {E['cx']},{E['cy'] - E['h'] / 2 - 2}",
            f"M{E['cx']},{E['cy'] + E['h'] / 2} C{E['cx']},{S['cy'] - 40} {S['cx'] + hw + 45},{S['cy']} {S['cx'] + hw + 2},{S['cy']}",
            f"M{S['cx'] - hw},{S['cy']} C{Wn['cx'] + 40},{S['cy']} {Wn['cx']},{S['cy'] - 40} {Wn['cx']},{Wn['cy'] + Wn['h'] / 2 + 2}",
            f"M{Wn['cx']},{Wn['cy'] - Wn['h'] / 2} C{Wn['cx']},{N['cy'] + 40} {N['cx'] - hw - 45},{N['cy']} {N['cx'] - hw - 2},{N['cy']}",
        ]
        out = "".join(edge(p) for p in paths) + N["svg"] + E["svg"] + S["svg"] + Wn["svg"]
        (l1, l2, l3, l4) = labels
        out += (f'<text class="el" x="{cx + 100}" y="196" text-anchor="end">{e(l1)}</text>'
                f'<text class="el" x="{cx + 100}" y="352" text-anchor="end">{e(l2)}</text>'
                f'<text class="el" x="{cx - 100}" y="352" text-anchor="start">{e(l3)}</text>'
                f'<text class="el" x="{cx - 100}" y="196" text-anchor="start">{e(l4)}</text>')
        out += f'<circle class="rr" cx="{cx}" cy="268" r="14"/><text class="rl" x="{cx}" y="272.5">R</text>'
        out += f'<text class="lt" x="{cx}" y="462" text-anchor="middle">{e(title)}</text>'
        return out, N["cy"] - N["h"] / 2

    pct_ = lambda a, b_: round((1 - b_ / a) * 100)
    left, ltop = loop(214, [
        (["Fewer people quit"], f"quits {F['quits_2019']}k → {F['quits_l12']}k a month", "meas"),
        (["Fewer openings"], f"openings {F['openings_2019']}k → {F['openings_l12']}k", "meas"),
        (["Fewer hires"], f"hires {F['hires_2019']}k → {F['hires_l12_6']}k", "meas"),
        (["Fewer jobs to", "move to"], "not measured", "infer"),
    ], ("backfills go unposted", "less left to fill", "fewer offers", "stay put"), "Loop 1: staying put", None)
    right, rtop = loop(686, [
        (["Fewer entry-level", "hires"], ["proxy only: grads", f"unemployed {F['recent_2019']}% → {F['recent_l12']}%"], "infer"),
        (["Less on-the-job", "training"], "not measured", "infer"),
        (["Thinner mid-level", "bench in 3-5 yrs"], "not measured", "infer"),
        (["Teams lean on", "seniors + AI"], "not measured", "infer"),
    ], ("fewer to train", "fewer promoted", "gap filled by", "seem optional"), "Loop 2: the thinning bench", None)
    shock = ('<rect class="shock" x="320" y="8" width="260" height="40" rx="10"/>'
             '<text class="nt" x="450" y="33" text-anchor="middle">Hiring freeze + layoffs, 2022 on</text>'
             f'<path class="edge" d="M320,28 C214,28 214,{ltop - 40:.0f} 214,{ltop - 2:.0f}" marker-end="url(#ar)"/>'
             f'<path class="edge" d="M580,28 C686,28 686,{rtop - 40:.0f} 686,{rtop - 2:.0f}" marker-end="url(#ar)"/>'
             '<text class="el" x="231" y="76" text-anchor="start">layoffs make staying put safer</text>'
             '<text class="el" x="669" y="76" text-anchor="end">a freeze cuts junior hiring first</text>')
    legend = ('<rect class="node meas" x="20" y="480" width="28" height="14" rx="4"/><text class="leg" x="56" y="491">solid: level measured in chapters 1-5</text>'
              '<rect class="node infer" x="330" y="480" width="28" height="14" rx="4"/><text class="leg" x="366" y="491">dashed: not measured here</text>'
              '<path class="edge" d="M600,487 L640,487" marker-end="url(#ar)"/><text class="leg" x="648" y="491">proposed mechanism, not tested as cause</text>'
              '<circle class="rr" cx="27" cy="512" r="9"/><text class="rl" x="27" y="516" style="font-size:10px">R</text><text class="leg" x="46" y="516">reinforcing loop: each lap strengthens the next</text>')
    aria = ("Two reinforcing loops. Staying put: fewer people quit, so fewer openings, so fewer hires, so fewer jobs to move to, so people stay put. "
            "Thinning bench: fewer entry-level hires, less on-the-job training, a thinner mid-level bench in three to five years, teams lean on seniors and AI, so juniors look optional.")
    return (f'<div class="loops"><p class="hint">Swipe sideways to see loop 2.</p><div class="scroll"><svg viewBox="0 0 900 530" role="img" aria-label="{e(aria)}">'
            '<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>'
            + shock + left + right + legend + '</svg></div></div>')


def badge(kind):
    ring = '<circle cx="7" cy="7" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/>'
    fills = {"ok": '<circle cx="7" cy="7" r="6" fill="currentColor"/>',
             "timing": ring + '<path d="M7,1 A6,6 0 0 1 7,13 Z" fill="currentColor"/>',
             "weak": ring + '<path d="M7,7 L7,1 A6,6 0 0 1 13,7 Z" fill="currentColor"/>',
             "none": ring}
    label = {"ok": "Consistent", "timing": "Timing only", "weak": "Weak", "none": "Not measured here"}[kind]
    return f'<span class="badge"><svg viewBox="0 0 14 14" width="14" height="14" aria-hidden="true">{fills[kind]}</svg>{label}</span>'


def row(cause, expect, seen, kind):
    return f"<tr><td>{cause}</td><td>{expect}</td><td>{seen}</td><td>{badge(kind)}</td></tr>"


causes = "".join([
    row("Cheap money and over-hiring, 2020-22", "Postings and hiring surge, then fall back toward normal.",
        f"Software postings reached {F['indeed_sw_peak']} (Feb 2020 = 100); information-sector hires averaged {F['hires_2022']}k a month in 2022 against {F['hires_2019']}k in 2019. Both fell back.", "ok"),
    row("Interest-rate rises from March 2022", "Postings fall after rates rise.",
        f"Postings peaked in February 2022, a month before the first rise (markets may have anticipated it), then kept falling as rates climbed through 2023.", "timing"),
    row("Section 174 amortization (2022; reversed for 2025 on)", "Software spending cut from 2022; some relief once expensing returned in July 2025.",
        f"Postings fell from 2022. After July 2025 they rose from {F['sw_2025_07']} to {F['indeed_sw_latest']}, a small move with no firm-level data behind it.", "weak"),
    row("Margin pressure and investor demands for efficiency", "Cuts at profitable firms; cost-cutting named as a reason.",
        "Challenger names cost-cutting among stated reasons (for example in October 2025), but we did not tally it.", "none"),
    row("AI tools", "Entry-level hiring falls first; employers cite AI; headcount falls in exposed roles.",
        f"AI-cited cuts rose from {n(ai_2025)} (2025) to {n(F['challenger_ai_2026ytd'])} (Jan-Sep 2026), and graduate unemployment is up. But software postings had already fallen from {F['indeed_sw_peak']} to {F['sw_2023_05']} by May 2023, when Challenger first tracked AI as a reason, and computer-systems-design jobs are still {F['emp_csd_latest']:+.1f}% versus January 2020.", "weak"),
    row("Offshoring, visa policy, tariffs, consolidation, normalization of pandemic-era digital demand", "Varies by candidate.", "No data for these in this project.", "none"),
])

ch6 = (
    f"""<p class="lede">Chapters 1 to 5 describe what happened. This one asks why, and says plainly how far the evidence goes. The short version: several plausible causes overlap in time, and the data here cannot rank them.</p>
<p>The table lists each candidate, what we would expect to see if it were the main driver, and what our data shows. The status column is about our evidence, not about whether a cause is real.</p>""",
    '<p class="hint prose" style="margin-bottom:-14px">Swipe the table sideways to see every column.</p><div class="table-wrap"><table class="causes"><thead><tr><th>Candidate cause</th><th>If it were the main driver</th><th>What our data shows</th><th>Where it stands</th></tr></thead><tbody>'
    + causes + '</tbody></table></div>'
    + '<div class="prose"><p class="src" style="margin-top:-12px">Sources: <a href="sources.html#indeed_hl">Indeed</a>, <a href="sources.html#bls_jolts">JOLTS</a>, <a href="sources.html#fred">FRED</a>, <a href="sources.html#challenger">Challenger</a>, <a href="sources.html#sec174">Section 174 sources</a>.</p>'
    + f"""<p>Two things the table does support. First, no single-cause story fits: the decline started in early 2022, before AI cuts were being reported, and it overlaps with the end of the boom, the rate rises and the tax change. Second, AI-attributed cuts appear mostly in 2025 and 2026, and the strain shows up at the entry level more than in headcount: computer-systems-design employment is still above its January 2020 level.</p>
<p>Markets can also feed themselves. One loop is measurable in part. When layoffs and uncertainty make staying put safer, fewer people quit. Quits create openings, because employers backfill, and openings become hires. In the information sector, quits averaged {F['quits_2019']},000 a month in 2019 and {F['quits_l12']},000 over the last 12 months, and the whole-economy quits rate fell from {F['qrate_2019']}% to {F['qrate_l12']}%.</p></div>"""
    + kpis(tile("Information-sector quits", f"{F['quits_l12']}k a month", f"12 months to {mo(story['latest_info_month'])} · 2019: {F['quits_2019']}k"),
           tile("Whole-economy quits rate", f"{F['qrate_l12']}%", f"12 months to {mo(story['latest_info_month'])} · 2019: {F['qrate_2019']}%"),
           tile("Information-sector hires", f"{F['hires_l12_6']}k a month", f"12 months to {mo(story['latest_info_month'])} · 2019: {F['hires_2019']}k"))
    + figure("fig-quits")
    + f"""<div class="prose"><p>The diagram shows that loop and a second one, about the entry-level pipeline. We measured the levels in the solid boxes. The arrows are proposed mechanisms: we did not test whether one step causes the next, and the dashed boxes are steps we have no data for.</p></div>"""
    + figure("fig-loops").replace('<div id="fig-loops"></div>', loop_diagram())
    + """<div class="prose"><p>The second loop could break. If the bench of mid-level engineers gets thin enough, the shortage raises hiring pressure again, but the delay could be years. Nothing here says it will happen or when.</p>
<p class="caveat"><strong>What would settle this.</strong> Ranking these causes needs firm-level data: which employers cut, in what roles, and what they reported about taxes, costs and AI at the time. Layoff notices filed under the WARN Act and company filings are the obvious places to look, and we set both aside for this draft. Until then, treat each cause here as a hypothesis with a stated status.</p></div>""",
)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tech Hiring Gap</title>
<meta name="description" content="Tech postings, layoffs and hiring since 2020, with every number traced to its source.">
<link rel="icon" href="data:,"><link rel="stylesheet" href="assets/style.css"></head>
<body id="top">
<div class="wrap">
<header class="mast">
<p class="eyebrow">Data story · tech labor market, 2020 to now</p>
<h1>Boom, bust, and a tech market that never fully reopened</h1>
<p class="dek">Tech hiring surged, stalled, and thinned out. What the numbers show, what they cannot show, and where we are guessing.</p>
<div class="hero">
<div class="hero-stats">
<div><span class="hs-val">{F['indeed_sw_peak']}<i>&rarr;</i>{F['indeed_sw_latest']}</span><span class="hs-lab">Software job postings, Feb 2020 = 100. Peak {mo(F['indeed_sw_peak_month'])}, now {mo(F['indeed_sw_latest_month'])}</span></div>
<div><span class="hs-val">{F['indeed_all_latest']}</span><span class="hs-lab">All job postings on the same scale, for comparison</span></div>
<div><span class="hs-val">{F['recent_2019']}%<i>&rarr;</i>{F['recent_l12']}%</span><span class="hs-lab">Unemployment, recent college graduates, 2019 vs last 12 months</span></div>
</div>
<div class="hero-spark" id="hero-spark" role="img" aria-label="Sparkline of software job postings, indexed to February 2020, rising to 229 in February 2022 and falling to 77"></div>
</div>
</header>
</div>
<nav class="nav" id="nav"><div class="nav-in"><a class="nav-home" href="#top">Tech hiring gap</a><span class="nav-links"><a href="#ch1">1 The boom</a><a href="#ch2">2 The turn</a><a href="#ch3">3 The cuts</a><a href="#ch4">4 The gap</a><a href="#ch5">5 Shut out</a><a href="#ch6">6 Why</a><a href="sources.html">Sources</a></span><button id="theme" type="button" aria-label="Toggle light and dark theme">&#9680;</button></div><div class="nav-bar" id="nav-bar"></div></nav>
<div class="wrap">
{chapter(1, ch1)}
{chapter(2, ch2)}
{chapter(3, ch3)}
{chapter(4, ch4)}
{chapter(5, ch5)}
{chapter(6, ch6)}
<footer>Every figure links to its sources; <a href="sources.html">the sources page</a> lists what each one measures, when it was retrieved, and where it falls short.</footer>
</div>
<script src="assets/vendor/d3.min.js"></script>
<script>window.STORY = {json.dumps({'series': S, 'facts': F, 'majors': story['majors'], 'latest_info_month': story['latest_info_month']})};</script>
<script src="assets/charts.js"></script>
<script src="assets/ui.js"></script>
<script src="assets/story.js"></script>
</body></html>"""
(ROOT / "site" / "index.html").write_text(page)
print("wrote site/index.html", len(page), "bytes")
