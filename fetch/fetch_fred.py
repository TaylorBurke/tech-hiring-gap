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
    "LNS11300060": "Labor force participation, prime age 25-54",
    "PAYEMS": "Total nonfarm employment",
    "CES6054150001": "Computer systems design and related services employment",
    "CES5051800001": "Computing infrastructure, data processing, web hosting employment",
    "CES6054000001": "Professional, scientific and technical services employment",
    "LNS14000036": "Unemployment rate, ages 20-24",
    "NILFWJN": "Not in labor force, want a job now",
    "LNU05026642": "Marginally attached to labor force",
    "LNU05026645": "Discouraged workers",
    "LNS12032194": "Part-time for economic reasons",
    "DGS10": "10-year Treasury yield",
}

for sid in SERIES:
    download("fred", f"{sid}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}")
