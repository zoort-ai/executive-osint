# main.py
from utils.io import ensure_output_dirs, save_json
from utils.dedup import dedup_by_url
from utils.filters import classify_job

from cz.jobs_cz import fetch_jobs_cz
from cz.linkedin import fetch_linkedin_cz_sk

from au.linkedin import fetch_linkedin_au
from au.seek import fetch_seek_au
from au.sixdegrees import fetch_sixdegrees_au
from au.sharpcarter import fetch_sharpcarter_au
from au.combine import combine_au_sources


def run_cz_sk():
    print("=== CZ/SK ===")
    jobs_cz = fetch_jobs_cz()
    jobs_linkedin = fetch_linkedin_cz_sk()

    all_jobs = jobs_cz + jobs_linkedin
    all_jobs = dedup_by_url(all_jobs)

    executive = []
    interim = []

    for job in all_jobs:
        category = classify_job(job)
        if category == "executive":
            executive.append(job)
        elif category == "interim":
            interim.append(job)

    save_json("output/cz/executive.json", executive)
    save_json("output/cz/interim.json", interim)

    print(f"[CZ/SK] Saved {len(executive)} executive and {len(interim)} interim jobs.")


def run_au():
    print("=== AUSTRALIA ===")
    linkedin_au = fetch_linkedin_au()
    seek_au = fetch_seek_au()
    sixdegrees_au = fetch_sixdegrees_au()
    sharpcarter_au = fetch_sharpcarter_au()

    save_json("output/australia/linkedin.json", dedup_by_url(linkedin_au))
    save_json("output/australia/seek.json", dedup_by_url(seek_au))
    save_json("output/australia/sixdegrees.json", dedup_by_url(sixdegrees_au))
    save_json("output/australia/sharpcarter.json", dedup_by_url(sharpcarter_au))

    combined = combine_au_sources(
        linkedin_au,
        seek_au,
        sixdegrees_au,
        sharpcarter_au
    )
    save_json("output/australia/combined.json", combined)

    print(f"[AU] Saved {len(combined)} combined AU executive jobs.")


def main():
    ensure_output_dirs()
    run_cz_sk()
    run_au()


if __name__ == "__main__":
    main()

