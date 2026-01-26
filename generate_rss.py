import json
from datetime import datetime
from feedgen.feed import FeedGenerator
import os


def create_feed(jobs, title, link, description, output_path):
    fg = FeedGenerator()
    fg.title(title)
    fg.link(href=link, rel='alternate')
    fg.description(description)
    fg.language('en')

    for job in jobs:
        fe = fg.add_entry()
        fe.title(job["title"])
        fe.link(href=job["link"])
        fe.description(f"{job.get('company', '')} – {job.get('location', '')}")
        fe.pubDate(datetime.utcnow())

    fg.rss_str(pretty=True)
    fg.rss_file(output_path)


def main():
    os.makedirs("output", exist_ok=True)

    try:
        with open("output/executive.json", "r", encoding="utf-8") as f:
            executive_jobs = json.load(f)
    except FileNotFoundError:
        executive_jobs = []

    try:
        with open("output/interim.json", "r", encoding="utf-8") as f:
            interim_jobs = json.load(f)
    except FileNotFoundError:
        interim_jobs = []

    create_feed(
        executive_jobs,
        title="Jobs.cz – Executive (CZ/SK)",
        link="https://www.jobs.cz/",
        description="Executive pozice z Jobs.cz (CZ/SK, filtrované).",
        output_path="output/executive.xml"
    )

    create_feed(
        interim_jobs,
        title="Jobs.cz – Interim (CZ/SK)",
        link="https://www.jobs.cz/",
        description="Interim / contract pozice z Jobs.cz (CZ/SK, filtrované).",
        output_path="output/interim.xml"
    )

    print("RSS feeds generated.")


if __name__ == "__main__":
    main()
