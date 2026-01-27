import os
import time
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

# ------------------------------------------------------------
#  KONFIGURACE KLÍČOVÝCH SLOV
# ------------------------------------------------------------

EXECUTIVE_KEYWORDS = [
    "executive", "director", "head", "group", "chief", "ceo", "coo", "cfo",
    "vp", "vice president", "general manager", "plant manager",
    "manufacturing", "operations", "factory", "production"
]

INTERIM_KEYWORDS = [
    "interim", "temporary", "contract"
]

# ------------------------------------------------------------
#  JOBS.CZ SCRAPER
# ------------------------------------------------------------

JOBS_CZ_SEARCHES = [
    {
        "name": "Jobs.cz – executive",
        "url": "https://www.jobs.cz/prace/?q%5B%5D=executive&locality%5B%5D=cz",
    },
    {
        "name": "Jobs.cz – director",
        "url": "https://www.jobs.cz/prace/?q%5B%5D=director&locality%5B%5D=cz",
    },
]

def fetch_jobs_cz(search):
    print(f"[Jobs.cz] Fetching: {search['name']}")
    response = requests.get(search["url"], headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Novější layout – články s výsledky
    items = soup.select("article[data-test='job-list-item']")
    # Fallback na starší layout
    if not items:
        items = soup.select("article.search-result, .search-list__item, .search-list-item")

    jobs = []

    for item in items:
        # Titulek + odkaz
        link_el = item.select_one("a[href*='/rpd/'], a[href*='detail-prace'], a")
        if not link_el:
            continue

        title = link_el.get_text(strip=True)
        link = link_el.get("href")

        if link and link.startswith("/"):
            link = "https://www.jobs.cz" + link

        # Firma
        company_el = item.select_one(
            "[data-test='job-company-name'], .search-result__company, .search-list__item__company, .search-list-item__company"
        )
        company = company_el.get_text(strip=True) if company_el else ""

        # Lokace
        location_el = item.select_one(
            "[data-test='job-location'], .search-result__info, .search-list__item__info, .search-list-item__info"
        )
        location = location_el.get_text(strip=True) if location_el else ""

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": link,
            "source": "Jobs.cz",
            "fetched_at": datetime.now(timezone.utc).isoformat()
        })

    print(f"[Jobs.cz] Found {len(jobs)} jobs for search '{search['name']}'")
    return jobs

# ------------------------------------------------------------
#  LINKEDIN SCRAPER (CZ + SK)
# ------------------------------------------------------------

LINKEDIN_BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

LINKEDIN_KEYWORDS = [
    "executive",
    "director",
    "head",
    "group head",
    "manufacturing",
    "operations",
    "plant",
    "factory"
]

LINKEDIN_LOCATIONS = [
    "Czech Republic",
    "Slovakia",
]

def fetch_linkedin_jobs():
    print("[LinkedIn] Fetching jobs for CZ + SK…")

    results = []

    for location in LINKEDIN_LOCATIONS:
        for kw in LINKEDIN_KEYWORDS:
            start = 0
            pages = 2  # lehký limit, ať to není moc agresivní

            for _ in range(pages):
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
                    print(f"[LinkedIn] {location} / '{kw}' → HTTP {response.status_code}, stopping this combo.")
                    break

                html = response.text.strip()
                if not html:
                    # Žádné další výsledky
                    break

                soup = BeautifulSoup(html, "html.parser")
                items = soup.find_all("li")
                if not items:
                    break

                for job in items:
                    title_el = job.find("h3")
                    company_el = job.find("h4")
                    link_el = job.find("a", href=True)

                    if not title_el or not link_el:
                        continue

                    title = title_el.get_text(strip=True)
                    company = company_el.get_text(strip=True) if company_el else ""
                    link = link_el["href"]

                    if link.startswith("/"):
                        link = "https://www.linkedin.com" + link

                    # Lokace – LinkedIn ji má často v samostatném elementu, ale když ji nemáme, použijeme location z dotazu
                    location_text = location

                    results.append({
                        "title": title,
                        "company": company,
                        "location": location_text,
                        "url": link,
                        "source": "LinkedIn",
                        "fetched_at": datetime.now(timezone.utc).isoformat()
                    })

                start += len(items)
                time.sleep(1)  # malá pauza, ať nejsme agresivní

    print(f"[LinkedIn] Total jobs fetched: {len(results)}")
    return results

# ------------------------------------------------------------
#  KLASIFIKACE
# ------------------------------------------------------------

def classify_job(job):
    text = (job.get("title", "") + " " + job.get("company", "")).lower()

    if any(k in text for k in INTERIM_KEYWORDS):
        return "interim"

    if any(k in text for k in EXECUTIVE_KEYWORDS):
        return "executive"

    return None

# ------------------------------------------------------------
#  MAIN PIPELINE
# ------------------------------------------------------------

def main():
    os.makedirs("output", exist_ok=True)

    all_jobs = []
    seen_urls = set()

    # Jobs.cz
    jobs_cz_total = 0
    for search in JOBS_CZ_SEARCHES:
        try:
            jobs = fetch_jobs_cz(search)
            jobs_cz_total += len(jobs)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"[Jobs.cz] Error fetching '{search['name']}': {e}")

    # LinkedIn
    try:
        linkedin_jobs = fetch_linkedin_jobs()
        all_jobs.extend(linkedin_jobs)
    except Exception as e:
        print(f"[LinkedIn] Error: {e}")
        linkedin_jobs = []

    print(f"[Summary] Jobs.cz total: {jobs_cz_total}")
    print(f"[Summary] LinkedIn total: {len(linkedin_jobs)}")
    print(f"[Summary] Combined before dedup: {len(all_jobs)}")

    # Dedup podle URL
    unique_jobs = []
    for job in all_jobs:
        url = job.get("url")
        if not url:
            continue
        if url not in seen_urls:
            seen_urls.add(url)
            unique_jobs.append(job)

    print(f"[Summary] Unique jobs after dedup: {len(unique_jobs)}")

    # Klasifikace
    executive_jobs = []
    interim_jobs = []

    for job in unique_jobs:
        category = classify_job(job)
        if category == "executive":
            executive_jobs.append(job)
        elif category == "interim":
            interim_jobs.append(job)

    # Uložení – vždy vytvoří soubory, i když jsou prázdné
    with open("output/executive.json", "w", encoding="utf-8") as f:
        json.dump(executive_jobs, f, ensure_ascii=False, indent=2)

    with open("output/interim.json", "w", encoding="utf-8") as f:
        json.dump(interim_jobs, f, ensure_ascii=False, indent=2)

    print(f"[Result] Saved {len(executive_jobs)} executive jobs and {len(interim_jobs)} interim jobs.")

if __name__ == "__main__":
    main()
