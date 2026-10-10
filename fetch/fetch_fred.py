"""FRED series as CSV (no API key needed)."""
from common import download

START = "2019-01-01"  # one year of pre-2020 baseline
SERIES = {
    "FEDFUNDS": "Effective federal funds rate",
    "U6RATE": "U-6 unemployment + underemployment",
    "UNRATE": "U-3 headline unemployment rate",
    "USINFO": "Information-sector employment",
    "JTSJOL": "JOLTS total nonfarm openings",
    "JTSHIL": "JOLTS total nonfarm hires",
    "JTSLDL": "JOLTS total nonfarm layoffs and discharges",
    "EMRATIO": "Employment-population ratio, 16+",
    "LNS12300060": "Employment-population ratio, prime age 25-54",
}

for sid in SERIES:
    download("fred", f"{sid}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}")
