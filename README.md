# tech-hiring-gap

Why have tech layoffs, job openings, and actual hiring drifted apart since 2020, and how much of it is AI?
The working thesis ("cut, but not hired") is tested against a map of causes and feedback loops:
2020-22 over-hiring, interest rates, the 2022 Section 174 R&D tax rule, margin pressure, AI tooling,
offshoring, and a shrinking junior pipeline. Tech is compared against the whole labor market.

## Rules
- Every number carries a source id from `sources.toml`; charts cite ids; `build_sources.py` renders the public sources page.
- Misleading headline numbers (U-3, openings, layoff trackers) are always shown with their caveat or a companion measure (U-6, employment-population, hires).
- Challenger and Layoffs.fyi are cited and linked, not redistributed (`redistribute = false`).

## Pipeline
```
fetch/fetch_fred.py        FRED CSVs        -> data/raw/fred/
fetch/fetch_bls_jolts.py   BLS JOLTS API    -> data/raw/bls_jolts/
fetch/fetch_indeed.py      Indeed postings  -> data/raw/indeed_hl/
build_sources.py           sources.toml + manifests -> site/sources.html
```
Raw downloads are git-ignored; each source has a `manifest.json` (url, sha256, fetch time). Python stdlib only.
