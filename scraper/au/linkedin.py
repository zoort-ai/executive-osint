# au/linkedin.py
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from utils.filters import is_au_title_match, is_au_segment_match

LINKEDIN_BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


def fetch_linkedin_au() -> list[dict]:
    print("[LinkedIn AU] Fetching…")
    results: list[dict] = []

    # Použijeme širší keyword a pak filtrujeme tituly
    KEYWORDS_AU = [
        "chief operating officer",
        "chief executive officer",
        "operations director",
        "supply chain director",
        "logistics director",
        "transformation director",
    ]

    for kw in KEYWORDS_AU:
        start = 0

        for _ in range(2):  # 2 pages per keyword
            params = {
                "keywords": kw,
                "location": "Australia",
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
                location = location_el.get_text(strip=True) if location_el else ""

                link = link_el["href"]
                if link.startswith("/"):
                    link = "https://www.linkedin.com" + link

                job_obj = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": link,
                    "source": "LinkedIn AU",
                    "fetched_at": datetime.now(timezone.utc).isoformat()
                }

                if not is_au_title_match(job_obj):
                    continue
                if not is_au_segment_match(job_obj):
                    continue

                results.append(job_obj)

            start += len(items)
            time.sleep(1)

    print(f"[LinkedIn AU] Total jobs fetched: {len(results)}")
    return results

