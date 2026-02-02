# au/sixdegrees.py
import time
from datetime import datetime, timezone
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from utils.filters import is_au_title_match, is_au_segment_match
from utils.dedup import dedup_by_url

BASE_URL = "https://www.sixdegreesexecutive.com.au/jobs"


def fetch_sixdegrees_au() -> list[dict]:
    print("[Six Degrees AU] Fetching…")
    results: list[dict] = []

    from utils.filters import AU_TITLES

    for title in AU_TITLES:
        query = quote_plus(title)
        url = f"{BASE_URL}?keywords={query}"

        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.find_all("article")
        for item in items:
            title_el = item.find("a")
            link_el = title_el
            company_el = item.find("p", class_="job__company")
            location_el = item.find("p", class_="job__location")

            if not title_el or not link_el:
                continue

            job_title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else ""

            link = link_el.get("href")
            if link and link.startswith("/"):
                link = "https://www.sixdegreesexecutive.com.au" + link

            job_obj = {
                "title": job_title,
                "company": company,
                "location": location,
                "url": link,
                "source": "Six Degrees AU",
                "fetched_at": datetime.now(timezone.utc).isoformat()
            }

            if not is_au_title_match(job_obj):
                continue
            if not is_au_segment_match(job_obj):
                continue

            results.append(job_obj)

        time.sleep(1)

    results = dedup_by_url(results)
    print(f"[Six Degrees AU] Total jobs fetched: {len(results)}")
    return results

