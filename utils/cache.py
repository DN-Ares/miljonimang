import hashlib
import json
import os
import time

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
CACHE_TTL = 3600


def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def make_cache_key(assignment_data):
    content = assignment_data["content"]
    files = assignment_data["solution_files"]
    raw = content + json.dumps(files, sort_keys=True)
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def load_from_cache(assignment_data):
    ensure_cache_dir()
    key = make_cache_key(assignment_data)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    if not os.path.exists(cache_file):
        return None
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if time.time() - cached["cached_at"] > CACHE_TTL:
            os.remove(cache_file)
            return None
        return cached["questions"]
    except (json.JSONDecodeError, IOError, KeyError):
        return None


def save_to_cache(assignment_data, questions):
    ensure_cache_dir()
    key = make_cache_key(assignment_data)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({
                "cached_at": time.time(),
                "questions": questions,
            }, f, indent=2, ensure_ascii=False)
    except IOError:
        pass
