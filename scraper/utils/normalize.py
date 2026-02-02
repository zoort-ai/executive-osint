# utils/normalize.py
CZECH_ALIASES = [
    "czech republic", "cesko", "czechia",
    "česko", "česká republika", "ceska republika",
    "prague", "praha"
]


def normalize_location(loc: str) -> str:
    if not loc:
        return loc

    l = loc.lower()

    # Czech variants
    if any(alias in l for alias in CZECH_ALIASES):
        return "Czech Republic"

    # Dominican Republic – explicit, aby se to nepletlo s CZE
    if "dominican republic" in l or "punta cana" in l:
        return "Dominican Republic"

    return loc

