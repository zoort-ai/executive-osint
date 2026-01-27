import json
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator

def create_feed(input_file, output_file, title, description):
    with open(input_file, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    fg = FeedGenerator()
    fg.title(title)
    fg.description(description)
    fg.link(href="https://zoort-ai.github.io/executive-osint/", rel="alternate")
    fg.language("en")

    for job in jobs:
        fe = fg.add_entry()
        fe.title(job["title"])
        fe.link(href=job["url"])
        fe.description(f"{job.get('company', '')} — {job.get('location', '')}")
        fe.pubDate(datetime.now(timezone.utc))

    fg.rss_file(output_file)
    print(f"RSS saved: {output_file}")

def main():
    create_feed(
        "output/executive.json",
        "output/executive.xml",
        "Executive Jobs Feed",
        "Latest executive-level job postings"
    )

    create_feed(
        "output/interim.json",
        "output/interim.xml",
        "Interim Jobs Feed",
        "Latest interim job postings"
    )

if __name__ == "__main__":
    main()
