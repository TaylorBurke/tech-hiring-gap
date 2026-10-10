"""Figure registry: which sources feed which chart. Drives figure footers and the 'used in' lists on the sources page."""

FIGURES = {
    "fig-postings": {"chapter": 1, "title": "Software postings soared, then fell below where they started",
        "sub": "Indeed job postings index, monthly average, February 2020 = 100", "sources": ["indeed_hl"]},
    "fig-turn": {"chapter": 2, "title": "Postings peaked as rates rose and a tax rule changed; employment barely moved",
        "sub": "Three measures on one shared time axis, 2019 to 2026", "sources": ["fred", "indeed_hl", "sec174"]},
    "fig-cuts": {"chapter": 3, "title": "Announced layoffs ran in waves",
        "sub": "Monthly announced U.S. job cuts, all industries, January 2021 onward (2020 omitted for scale)", "sources": ["challenger"]},
    "fig-layoffs": {"chapter": 3, "title": "Information-sector layoffs ran above 2019 levels in early 2026, then eased",
        "sub": "Layoffs and discharges per month, thousands, 3-month average. Hollow point = preliminary", "sources": ["bls_jolts"]},
    "fig-ai": {"chapter": 3, "title": "Cuts that employers attribute to AI, 2026",
        "sub": "Monthly announced job cuts citing artificial intelligence as the reason", "sources": ["challenger"]},
    "fig-gap-levels": {"chapter": 4, "title": "Openings fell much faster than hires",
        "sub": "Information sector, thousands per month, 3-month average. Hollow point = preliminary", "sources": ["bls_jolts"]},
    "fig-gap-ratio": {"chapter": 4, "title": "Openings per hire peaked in 2022 and fell to a multi-year low in 2026",
        "sub": "Job openings divided by hires, 3-month average. Hollow point = preliminary", "sources": ["bls_jolts", "fred"]},
}

CHAPTERS = {1: "The boom", 2: "The turn", 3: "The cuts", 4: "The gap that narrowed"}
