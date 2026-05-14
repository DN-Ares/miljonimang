import json
import os
import time

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def save_result(assignment_id, assignment_title, score, total, won, questions_count):
    ensure_data_dir()
    results = load_all_results()
    results.append({
        "id": len(results) + 1,
        "assignment_id": assignment_id,
        "assignment_title": assignment_title,
        "score": score,
        "total": total,
        "won": won,
        "questions_count": questions_count,
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "timestamp": time.time(),
    })
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return results[-1]


def load_all_results():
    ensure_data_dir()
    if not os.path.exists(RESULTS_FILE):
        return []
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
