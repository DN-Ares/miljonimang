POINTS = [
    100, 200, 300, 500, 1000,
    2000, 4000, 8000, 16000, 32000,
    64000, 125000, 250000, 500000, 1000000,
]

SAFE_LEVELS = {4: 1000, 9: 32000, 14: 1000000}

LIFELINES = {
    "fifty_fifty": "50:50",
    "ask_ai": "Küsi AI-lt",
    "ask_audience": "Küsi publikult",
}


def get_points(question_index):
    if 0 <= question_index < len(POINTS):
        return POINTS[question_index]
    return 0


def get_safe_level(question_index):
    for safe_idx in sorted(SAFE_LEVELS.keys(), reverse=True):
        if question_index >= safe_idx:
            return SAFE_LEVELS[safe_idx]
    return 0


def apply_fifty_fifty(question):
    correct = question["correctIndex"]
    wrong = [i for i in range(4) if i != correct]
    import random
    to_remove = random.sample(wrong, 2)
    remaining = sorted([correct] + [i for i in range(4) if i not in to_remove])
    return remaining, to_remove


def generate_audience_vote(question, difficulty):
    correct = question["correctIndex"]
    import random

    base_correct = 0.3 + (1.0 - difficulty / 15) * 0.5
    base_correct = min(base_correct, 0.95)

    votes = [0, 0, 0, 0]
    remaining = 100
    for i in range(3):
        if i == correct:
            continue
        votes[i] = random.randint(1, max(2, int((1 - base_correct) * 20 / 3)))
        remaining -= votes[i]

    votes[correct] = remaining
    for i in range(3):
        if votes[i] < 0:
            votes[correct] += votes[i]
            votes[i] = 0

    total = sum(votes)
    percentages = [round(v / total * 100) for v in votes]
    diff = 100 - sum(percentages)
    if diff != 0:
        percentages[correct] += diff

    return {chr(65 + i): pct for i, pct in enumerate(percentages)}


def generate_ai_hint(question):
    return f"Vihje: {question['explanation']}"
