# cz/linkedin.py
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from utils.normalize import normalize_location
from utils.filters import is_blacklisted_cz

LINKEDIN_BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

LINKEDIN_KEYWORDS_CZ = [
    "executive", "director", "head", "group head",
    "manufacturing", "operations", "plant", "factory"
]

LINKEDIN_LOCATIONS_CZ = [
    "Czech Republic",
    "Slovakia",
]


def fetch_linkedin_cz_sk() -> list[dict]:
    print("[LinkedIn CZ/SK] Fetching…")
    results: list[dict] = []

    for location in LINKEDIN_LOCATIONS_CZ:
        for kw in LINKEDIN_KEYWORDS_CZ:
            start = 0

            for _ in range(2):  # 2 pages per keyword
                params = {
                    "keywords": kw,
                    "location": location,
                    "start": start
                }

                response = requests.get(
                    LINKEDIN_BASE_URL,
                    params=params,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                if response.status_code != 200:
                    break

                html = response.text.strip()
                if not html:
                    break

                soup = BeautifulSoup(html, "html.parser")
                items = soup.find_all("li")
                if not items:
                    break

                for job in items:
                    title_el = job.find("h3")
                    company_el = job.find("h4")
                    link_el = job.find("a", href=lambda x: x and "/jobs/view/" in x)
                    location_el = job.find("span", class_="job-search-card__location")

                    if not title_el or not link_el:
                        continue

                    title = title_el.get_text(strip=True)
                    company = company_el.get_text(strip=True) if company_el else ""
                    raw_location = location_el.get_text(strip=True) if location_el else ""
                    norm_location = normalize_location(raw_location)

                    link = link_el["href"]
                    if link.startswith("/"):
                        link = "https://www.linkedin.com" + link

                    job_obj = {
                        "title": title,
                        "company": company,
                        "location": norm_location,
                        "url": link,
                        "source": "LinkedIn CZ/SK",
                        "fetched_at": datetime.now(timezone.utc).isoformat()
                    }

                    if is_blacklisted_cz(job_obj):
                        continue

                    results.append(job_obj)

                start += len(items)
                time.sleep(1)

    print(f"[LinkedIn CZ/SK] Total jobs fetched: {len(results)}")
    return results

