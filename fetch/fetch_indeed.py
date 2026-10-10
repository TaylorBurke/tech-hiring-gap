"""Indeed Hiring Lab postings index (sector file is large; ~12 MB)."""
from common import download

BASE = "https://raw.githubusercontent.com/hiring-lab/job_postings_tracker/master/US"
download("indeed_hl", "aggregate_US.csv", f"{BASE}/aggregate_job_postings_US.csv")
download("indeed_hl", "by_sector_US.csv", f"{BASE}/job_postings_by_sector_US.csv")
