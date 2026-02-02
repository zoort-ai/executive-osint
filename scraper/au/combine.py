# au/combine.py
from utils.dedup import dedup_by_url


def combine_au_sources(*sources: list[list[dict]]) -> list[dict]:
    combined: list[dict] = []
    for src in sources:
        combined.extend(src)
    combined = dedup_by_url(combined)
    return combined

