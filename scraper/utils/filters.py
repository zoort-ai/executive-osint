# utils/filters.py

# CZ/SK – klasifikace a blacklist
EXECUTIVE_KEYWORDS = [
    "executive", "director", "head", "group", "chief", "ceo", "coo", "cfo",
    "vp", "vice president", "general manager", "plant manager",
    "manufacturing", "operations", "factory", "production"
]

INTERIM_KEYWORDS = [
    "interim", "temporary", "contract"
]

BLACKLIST_CZ = [
    "manufacturing", "vyroba", "výroba",
    "accounting", "production", "automotive"
]


def classify_job(job: dict) -> str | None:
    text = (job.get("title", "") + " " + job.get("company", "")).lower()

    if any(k in text for k in INTERIM_KEYWORDS):
        return "interim"

    if any(k in text for k in EXECUTIVE_KEYWORDS):
        return "executive"

    return None


def is_blacklisted_cz(job: dict) -> bool:
    text = (job.get("title", "") + " " + job.get("company", "")).lower()
    return any(b in text for b in BLACKLIST_CZ)


# AU – role a segmenty
AU_TITLES = [
    "chief operating officer",
    "coo",
    "chief executive officer",
    "ceo",

    "executive director operations",
    "general manager operations",

    "head of supply chain",
    "director of supply chain",
    "general manager supply chain",

    "head of logistics",
    "head of fulfilment",
    "head of fulfillment",
    "head of distribution",

    "director of operations",
    "regional operations director",
    "national operations manager",
    "general manager operations",

    "head of operations excellence",

    "transformation director",
    "head of transformation",
    "director of business transformation",

    "operational excellence director",
    "continuous improvement director",

    "general manager retail operations",
    "head of retail transformation",
    "director of store operations",
]

AU_SEGMENTS = [
    "retail",
    "fmcg",
    "e-commerce",
    "ecommerce"
]


def is_au_title_match(job: dict) -> bool:
    title = job.get("title", "").lower()
    return any(t in title for t in AU_TITLES)


def is_au_segment_match(job: dict) -> bool:
    text = (job.get("title", "") + " " + job.get("company", "")).lower()
    return any(seg in text for seg in AU_SEGMENTS)

