# utils/dedup.py

def dedup_by_url(jobs: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for job in jobs:
        url = job.get("url")
        if not url:
            continue
        if url in seen:
            continue
        seen.add(url)
        unique.append(job)
    return unique

