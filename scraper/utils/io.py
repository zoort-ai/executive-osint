# utils/io.py
import os
import json


def ensure_output_dirs():
    os.makedirs("output/cz", exist_ok=True)
    os.makedirs("output/australia", exist_ok=True)


def save_json(path: str, data: list[dict]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

