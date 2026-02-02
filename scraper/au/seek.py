# au/seek.py
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from utils.filters import is_au_title_match, is_au_segment_match
from utils.dedup import dedup_by_url


BASE_URL = "https://www.seek.com.au"


def fetch_seek_au() -> list[dict]:
    print("[Seek AU] Fetching…")
    results: list[dict] = []

    # Budeme používat stejné AU_TITLES jako dotazy
    from utils.filters import AU_TITLES

    for title in AU_TITLES:
        query = quote_plus(title)
        url = f"{BASE_URL}/{query}-jobs"

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Seek používá article job-card
        items = soup.find_all("article")
        for item in items:
            link_el = item.find("a", href=True)
            title_el = item.find("a", attrs={"data-automation": "jobTitle"})
            company_el = item.find(attrs={"data-automation": "jobCompany"})
            location_el = item.find(attrs={"data-automation": "jobLocation"})

            if not link_el or not title_el:
                continue

            job_title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else ""

            link = link_el["href"]
            if link.startswith("/"):
                link = BASE_URL + link

            job_obj = {
                "title": job_title,
                "company": company,
                "location": location,
                "url": link,
                "source": "Seek AU",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

            if not is_au_title_match(job_obj):
                continue
            if not is_au_segment_match(job_obj):
                continue

            results.append(job_obj)

        time.sleep(1)

    results = dedup_by_url(results)
    print(f"[Seek AU] Total jobs fetched: {len(results)}")
    return results

