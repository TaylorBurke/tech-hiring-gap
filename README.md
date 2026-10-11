# tech-hiring-gap

**Live:** https://taylorburke.github.io/tech-hiring-gap/ (sources page: `/sources.html`)

Why have tech layoffs, job openings, and actual hiring drifted apart since 2020, and how much of it is AI?
The working thesis ("cut, but not hired") is tested against a map of causes and feedback loops:
2020-22 over-hiring, interest rates, the 2022 Section 174 R&D tax rule, margin pressure, AI tooling,
offshoring, and a shrinking junior pipeline. Tech is compared against the whole labor market.

## Rules
- Every number carries a source id from `sources.toml`; charts cite ids; `build_sources.py` renders the public sources page.
- Misleading headline numbers (U-3, openings, layoff trackers) are always shown with their caveat or a companion measure (U-6, employment-population, hires).
- Challenger is cited and linked, not redistributed (`redistribute = false`): raw reports stay git-ignored, and the derived CSV keeps only the figure, the quoted sentence and the report link. Layoffs.fyi is deliberately not used.

## The story
Six chapters on one page: the boom, the turn, the cuts, the gap that narrowed, who is shut out, and why (a causes table with an evidence status for each candidate, plus two feedback-loop diagrams that separate measured steps from proposed ones). It never claims one cause. Where the data cannot settle a question, the page says so.

## Sources
| id | what it supplies |
|---|---|
| `fred` | Fed funds, 10-year Treasury, U-3, U-6, employment-population, participation, payrolls by industry, people who want a job but are not looking |
| `bls_jolts` | information-sector openings, hires, layoffs and quits |
| `indeed_hl` | Indeed postings indexed to Feb 2020 (software development and all) |
| `challenger` | announced job cuts, total and AI-cited (AI tracked as its own reason only since May 2023) |
| `nyfed_college` | recent-graduate vs all-worker unemployment, and rates by major (2024 ACS) |
| `sec174` | Section 174 dates (IRS Notice 2023-63; the 2025 restoration still cites a law-firm summary) |

Not used on purpose: Layoffs.fyi and state WARN notices (WARN would be the next step for firm-level causes). The `Information` sector is only a rough proxy for tech.

## Pipeline
```
fetch/fetch_fred.py                  FRED CSVs        -> data/raw/fred/
fetch/fetch_bls_jolts.py             BLS JOLTS API    -> data/raw/bls_jolts/   (unregistered: 25 queries/day)
fetch/fetch_indeed.py                Indeed postings  -> data/raw/indeed_hl/
fetch/fetch_nyfed.py                 NY Fed CSVs      -> data/raw/nyfed_college/
fetch/fetch_challenger.py            Challenger RSS   -> data/raw/challenger/
fetch/extract_challenger.py          reports -> data/challenger_monthly.csv (value + verbatim quote + URL)
fetch/build_challenger_overrides.py  hand-entered gap values, each verified against report text
build_data.py                        everything above -> data/derived/story.json
build_site.py                        story.json + figures.py -> site/index.html (prose is built from the facts, so numbers cannot drift)
build_sources.py                     sources.toml + manifests -> site/sources.html
```
Rebuild after fetching: `python3 build_data.py && python3 build_site.py && python3 build_sources.py`, then preview with `cd site && python3 -m http.server`.

Raw downloads are git-ignored; each source has a `manifest.json` (url, sha256, fetch time). Python stdlib only. Charts are hand-written SVG (`site/assets/charts.js`, per-figure specs in `story.js`) with D3 v7 vendored for scales and shapes. Colors come from a validated categorical palette, with light and dark themes. Each chart has a crosshair tooltip, keyboard focus and a table view.

## Adding a figure
1. Add the series to `build_data.py` and the figure to `figures.py` with its source ids.
2. Add the chart spec to `site/assets/story.js` and the markup to a chapter in `build_site.py`.
3. Rebuild. The sources page lists the new figure under each source it names.

## Hosting
`.github/workflows/pages.yml` publishes `site/` to GitHub Pages on every push to `main`.
