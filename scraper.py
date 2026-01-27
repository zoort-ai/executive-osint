import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# ------------------------------------------------------------
#  EXECUTIVE & INTERIM KEYWORDS
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

SEARCHES = [
    {
        "name": "Jobs.cz Executive",
        "url": "https://www.jobs.cz/prace/?q%5B%5D=executive&locality%5B%5D=cz",
    }
]

def fetch_jobs_cz(search):
    print(f"Fetching Jobs.cz: {search['name']}")
    response = requests.get(search["url"], headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(".search-list__item, .search-list-item")

    jobs = []

    for item in items:
        title_el = item.select_one("a")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        link = title_el.get("href")

        if link and link.startswith("/"):
            link = "https://www.jobs.cz" + link

        company_el = item.select_one(".search-list__item__company, .search-list-item__company")
        company = company_el.get_text(strip=True) if company_el else ""

        location_el = item.select_one(".search-list__item__info, .search-list-item__info")
        location = location_el.get_text(strip=True) if location_el else ""

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": link,
            "source": "Jobs.cz",
            "fetched_at": datetime.utcnow().isoformat() + "Z"
        })

    return jobs

# ------------------------------------------------------------
#  LINKEDIN SCRAPER
# ------------------------------------------------------------

def scrape_linkedin_jobs():
    print("Fetching LinkedIn Jobs…")

    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    keywords = [
        "executive", "director", "head", "group", "chief",
        "manufacturing", "operations", "plant", "factory"
    ]

    results = []

    for kw in keywords:
        params = {
            "keywords": kw,
            "location": "Czech Republic"
        }

        response = requests.get(base_url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        jobs = soup.find_all("li")

        for job in jobs:
            title_el = job.find("h3")
            company_el = job.find("h4")
            link_el = job.find("a")

            if not title_el or not link_el:
                continue

            title = title_el.get_text(strip=True)
            company = company_el.get_text(strip=True) if company_el else ""
            link = "https://www.linkedin.com" + link_el["href"]

            results.append({
                "title": title,
                "company": company,
                "location": "Czech Republic",
                "url": link,
                "source": "LinkedIn",
                "fetched_at": datetime.utcnow().isoformat() + "Z"
            })

    return results

# ------------------------------------------------------------
#  CLASSIFICATION
# ------------------------------------------------------------

def classify_job(job):
    text = (job["title"] + " " + job.get("company", "")).lower()

    if any(k in text for k in INTERIM_KEYWORDS):
        return "interim"

    if any(k in text for k in EXECUTIVE_KEYWORDS):
        return "executive"

    return None

# ------------------------------------------------------------
#  MAIN PIPELINE
# ------------------------------------------------------------

def main():
    all_jobs = []
    seen_urls = set()

    # Jobs.cz
    for search in SEARCHES:
        try:
            jobs = fetch_jobs_cz(search)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"Error fetching Jobs.cz: {e}")

    # LinkedIn
    try:
        linkedin_jobs = scrape_linkedin_jobs()
        all_jobs.extend(linkedin_jobs)
    except Exception as e:
        print(f"Error fetching LinkedIn: {e}")

    # Deduplication
    unique_jobs = []
    for job in all_jobs:
        if job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            unique_jobs.append(job)

    # Classification
    executive_jobs = []
    interim_jobs = []

    for job in unique_jobs:
        category = classify_job(job)
        if category == "executive":
            executive_jobs.append(job)
        elif category == "interim":
            interim_jobs.append(job)

    # Save output
    with open("output/executive.json", "w", encoding="utf-8") as f:
        json.dump(executive_jobs, f, ensure_ascii=False, indent=2)

    with open("output/interim.json", "w", encoding="utf-8") as f:
        json.dump(interim_jobs, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(executive_jobs)} executive jobs and {len(interim_jobs)} interim jobs.")

if __name__ == "__main__":
    main()
