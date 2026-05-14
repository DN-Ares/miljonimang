import json
import os
import random
from flask import Flask, render_template, request, jsonify, session

from utils.file_reader import get_assignment_list, read_assignment
from utils.question_generator import generate_questions
from utils.cache import load_from_cache, save_to_cache
from utils.storage import save_result, load_all_results
from utils.game_logic import (
    POINTS,
    get_points,
    get_safe_level,
    apply_fifty_fifty,
    generate_audience_vote,
    generate_ai_hint,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "miljonimang-dev-key-2024")


@app.route("/")
def index():
    assignments = get_assignment_list()
    return render_template("index.html", assignments=assignments)


@app.route("/select/<assignment_id>")
def select_assignment(assignment_id):
    assignment_data = read_assignment(assignment_id)
    if not assignment_data:
        return "Ülesannet ei leitud", 404

    session["assignment_id"] = assignment_id
    session["current_question"] = 0
    session["score"] = 0
    session["game_over"] = False
    session["game_won"] = False
    session["lifelines"] = {"fifty_fifty": True, "ask_ai": True, "ask_audience": True}
    session["fifty_fifty_removed"] = []
    session["asked_audience"] = False

    title = assignment_id
    for a in get_assignment_list():
        if a["id"] == assignment_id:
            title = a["title"]
            break
    session["assignment_title"] = title

    return render_template("game.html", assignment_id=assignment_id, assignment_title=title)


@app.route("/api/assignment/<assignment_id>")
def api_assignment_content(assignment_id):
    data = read_assignment(assignment_id)
    if not data:
        return jsonify({"error": "Ei leitud"}), 404
    return jsonify({
        "id": data["id"],
        "content": data["content"],
        "solution_files": data["solution_files"],
    })


@app.route("/api/questions/<assignment_id>")
def api_get_questions(assignment_id):
    assignment_data = read_assignment(assignment_id)
    if not assignment_data:
        return jsonify({"error": "Ülesannet ei leitud"}), 404

    cached = load_from_cache(assignment_data)
    if cached:
        questions = cached
    else:
        api_key = request.args.get("api_key") or os.environ.get("OPENAI_API_KEY")
        questions = generate_questions(assignment_data, api_key)
        save_to_cache(assignment_data, questions)

    safe_questions = []
    for q in questions:
        safe_questions.append({
            "level": q["level"],
            "question": q["question"],
            "options": q["options"],
            "correctIndex": q["correctIndex"],
            "explanation": q["explanation"],
        })

    session["questions"] = safe_questions
    session["shuffled_questions"] = random.sample(safe_questions, len(safe_questions))
    return jsonify(safe_questions)


@app.route("/api/question/<int:question_num>")
def api_get_question(question_num):
    questions = session.get("shuffled_questions", [])
    if not questions:
        return jsonify({"error": "Küsimused puuduvad"}), 400
    if question_num < 0 or question_num >= len(questions):
        return jsonify({"error": "Küsimust pole"}), 404

    q = questions[question_num]
    return jsonify({
        "level": q["level"],
        "question": q["question"],
        "options": q["options"],
        "current": question_num + 1,
        "total": len(questions),
        "points": get_points(question_num),
        "safe_level": get_safe_level(question_num),
    })


@app.route("/api/answer", methods=["POST"])
def api_answer():
    data = request.get_json()
    question_num = data.get("question_num", 0)
    selected = data.get("selected", -1)

    questions = session.get("shuffled_questions", [])
    if not questions or question_num >= len(questions):
        return jsonify({"error": "Vigane päring"}), 400

    q = questions[question_num]
    correct = q["correctIndex"] == selected

    if correct:
        earned = get_points(question_num)
        session["score"] = earned
        session["current_question"] = question_num + 1

        if question_num + 1 >= len(questions):
            session["game_won"] = True
            _save_game_result()
            return jsonify({
                "correct": True,
                "game_won": True,
                "explanation": q["explanation"],
                "score": earned,
            })
        return jsonify({
            "correct": True,
            "game_won": False,
            "correct_index": q["correctIndex"],
            "explanation": q["explanation"],
            "score": earned,
        })
    else:
        fallback_score = get_safe_level(question_num)
        session["score"] = fallback_score
        session["game_over"] = True
        _save_game_result()
        return jsonify({
            "correct": False,
            "game_over": True,
            "correct_index": q["correctIndex"],
            "explanation": q["explanation"],
            "score": fallback_score,
        })


def _save_game_result():
    save_result(
        assignment_id=session.get("assignment_id", ""),
        assignment_title=session.get("assignment_title", ""),
        score=session.get("score", 0),
        total=sum(POINTS),
        won=session.get("game_won", False),
        questions_count=session.get("current_question", 0),
    )


@app.route("/api/lifeline", methods=["POST"])
def api_lifeline():
    data = request.get_json()
    lifeline_type = data.get("type")
    question_num = data.get("question_num", 0)

    questions = session.get("shuffled_questions", [])
    lifelines = session.get("lifelines", {})

    if not lifelines.get(lifeline_type):
        return jsonify({"error": "Õlekõrs on juba kasutatud"}), 400

    q = questions[question_num] if question_num < len(questions) else None
    if not q:
        return jsonify({"error": "Küsimust pole"}), 404

    result = {}

    if lifeline_type == "fifty_fifty":
        remaining, removed = apply_fifty_fifty(q)
        lifelines["fifty_fifty"] = False
        session["fifty_fifty_removed"] = removed
        result = {"type": "fifty_fifty", "remaining": remaining}

    elif lifeline_type == "ask_audience":
        votes = generate_audience_vote(q, question_num)
        lifelines["ask_audience"] = False
        result = {"type": "ask_audience", "votes": votes}

    elif lifeline_type == "ask_ai":
        hint = generate_ai_hint(q)
        lifelines["ask_ai"] = False
        result = {"type": "ask_ai", "hint": hint}

    session["lifelines"] = lifelines
    session.modified = True
    return jsonify(result)


@app.route("/api/state")
def api_state():
    return jsonify({
        "current_question": session.get("current_question", 0),
        "score": session.get("score", 0),
        "game_over": session.get("game_over", False),
        "game_won": session.get("game_won", False),
        "lifelines": session.get("lifelines", {}),
        "assignment_id": session.get("assignment_id", ""),
    })


@app.route("/api/restart", methods=["POST"])
def api_restart():
    data = request.get_json()
    assignment_id = data.get("assignment_id") or session.get("assignment_id")
    if not assignment_id:
        return jsonify({"error": "Puudub ülesande ID"}), 400

    session["current_question"] = 0
    session["score"] = 0
    session["game_over"] = False
    session["game_won"] = False
    session["lifelines"] = {"fifty_fifty": True, "ask_ai": True, "ask_audience": True}
    session["fifty_fifty_removed"] = []
    session["asked_audience"] = False
    if "questions" in session:
        session["shuffled_questions"] = random.sample(session["questions"], len(session["questions"]))
    session.modified = True
    return jsonify({"success": True})


@app.route("/api/regenerate", methods=["POST"])
def api_regenerate():
    data = request.get_json()
    assignment_id = data.get("assignment_id") or session.get("assignment_id")
    if not assignment_id:
        return jsonify({"error": "Puudub ülesande ID"}), 400

    assignment_data = read_assignment(assignment_id)
    if not assignment_data:
        return jsonify({"error": "Ülesannet ei leitud"}), 404

    session.pop("questions", None)
    session.pop("shuffled_questions", None)

    return jsonify({"success": True, "redirect": f"/select/{assignment_id}"})


@app.route("/result")
def result():
    score = session.get("score", 0)
    game_won = session.get("game_won", False)
    game_over = session.get("game_over", False)
    total_possible = sum(POINTS)
    return render_template("result.html", score=score, game_won=game_won, game_over=game_over,
                           total=total_possible, POINTS=POINTS)


@app.route("/history")
def history():
    results = load_all_results()
    results.reverse()
    return render_template("history.html", results=results)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
