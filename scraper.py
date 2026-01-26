import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

BASE_URL = "https://www.jobs.cz/hledani/"

EXECUTIVE_KEYWORDS = [
    "ceo", "coo", "executive", "head of", "director",
    "ředitel", "vedoucí", "manažer", "global", "group"
]

INTERIM_KEYWORDS = [
    "interim", "contract", "temporary", "dočasný",
    "projektový", "fractional"
]

SEARCHES = [
    {
        "name": "executive_cz",
        "params": {
            "q": "ceo coo executive \"head of\" director operations logistics \"supply chain\" global group",
            "region[0]": "cz"
        }
    },
    {
        "name": "executive_sk",
        "params": {
            "q": "ceo coo executive \"head of\" director operations logistics \"supply chain\" global group",
            "region[0]": "sk"
        }
    },
    {
        "name": "interim_cz",
        "params": {
            "q": "interim contract temporary fractional project",
            "region[0]": "cz"
        }
    },
    {
        "name": "interim_sk",
        "params": {
            "q": "interim contract temporary fractional project",
            "region[0]": "sk"
        }
    }
]


def fetch_jobs(search):
    resp = requests.get(BASE_URL, params=search["params"], timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    jobs = []
    for item in soup.select("article, div.search-list__item, div.search-list-item"):
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
            "link": link,
            "company": company,
            "location": location,
            "source": search["name"],
            "fetched_at": datetime.utcnow().isoformat() + "Z"
        })

    return jobs


def classify_job(job):
    text = (job["title"] + " " + job.get("company", "")).lower()

    if any(k in text for k in INTERIM_KEYWORDS):
        return "interim"
    if any(k in text for k in EXECUTIVE_KEYWORDS):
        return "executive"
    return None


def main():
    executive_jobs = []
    interim_jobs = []
    seen_links = set()

    for search in SEARCHES:
        try:
            jobs = fetch_jobs(search)
        except Exception as e:
            print(f"Error fetching {search['name']}: {e}")
            continue

        for job in jobs:
            if not job["link"] or job["link"] in seen_links:
                continue

            seen_links.add(job["link"])
            category = classify_job(job)

            if category == "executive":
                executive_jobs.append(job)
            elif category == "interim":
                interim_jobs.append(job)

    with open("output/executive.json", "w", encoding="utf-8") as f:
        json.dump(executive_jobs, f, ensure_ascii=False, indent=2)

    with open("output/interim.json", "w", encoding="utf-8") as f:
        json.dump(interim_jobs, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(executive_jobs)} executive jobs and {len(interim_jobs)} interim jobs.")


if __name__ == "__main__":
    main()
