"""NY Fed "Labor Market for Recent College Graduates": the CSVs behind its interactive chart."""
from common import download

BASE = "https://www.newyorkfed.org/medialibrary/research/interactives/data/college-labor-market"
for name in ("college-labor-outcomes-by-major-data", "college-labor-unemployment-data", "college-labor-underemployment-data"):
    download("nyfed_college", f"{name}.csv", f"{BASE}/{name}.csv")
