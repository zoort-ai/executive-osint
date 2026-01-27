import requests
from bs4 import BeautifulSoup

def scrape_linkedin_jobs():
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    keywords = [
        "executive", "director", "head", "group", "chief", "vp", "vice president",
        "manufacturing", "operations", "plant", "factory"
    ]

    executive_keywords = [
        "executive", "director", "head", "group", "chief", "vp", "vice president",
        "manufacturing", "operations"
    ]

    results = []

    for kw in keywords:
        params = {
            "keywords": kw,
            "location": "Czech Republic",
        }

        response = requests.get(base_url, params=params, headers={
            "User-Agent": "Mozilla/5.0"
        })

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

            text = f"{title} {company}".lower()

            if any(k in text for k in executive_keywords):
                results.append({
                    "title": title,
                    "company": company,
                    "url": link,
                    "source": "LinkedIn"
                })

    return results
