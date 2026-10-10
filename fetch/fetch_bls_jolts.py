"""JOLTS by industry from the BLS public API (v2, unregistered: 25 queries/day, 10 years)."""
import json
from common import download

# JTS + industry(6) + state(00) + size(0) + dataelement + ratelevel(L = level, R = rate)
SERIES = {
    "JTS510000000000000JOL": "Information: job openings (thousands)",
    "JTS510000000000000HIL": "Information: hires (thousands)",
    "JTS510000000000000LDL": "Information: layoffs and discharges (thousands)",
    "JTS510000000000000QUL": "Information: quits (thousands)",
    "JTS540099000000000JOL": "Professional and business services: job openings (thousands)",
}
body = json.dumps({"seriesid": list(SERIES), "startyear": "2019", "endyear": "2026"}).encode()
download("bls_jolts", "jolts_information.json", "https://api.bls.gov/publicAPI/v2/timeseries/data/",
         data=body, headers={"Content-Type": "application/json"})
