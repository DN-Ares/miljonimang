import os
import re

INPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "input")


def get_assignment_list():
    assignments = []
    if not os.path.exists(INPUT_DIR):
        return assignments

    for entry in sorted(os.listdir(INPUT_DIR)):
        entry_path = os.path.join(INPUT_DIR, entry)
        if os.path.isdir(entry_path) and re.match(r"^\d+$", entry):
            assignment_md = os.path.join(entry_path, "assignment.md")
            title = entry
            if os.path.exists(assignment_md):
                with open(assignment_md, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        title = first_line[2:].strip()
            assignments.append({"id": entry, "title": title, "path": entry_path})
    return assignments


def read_assignment(assignment_id):
    base_path = os.path.join(INPUT_DIR, assignment_id)
    if not os.path.isdir(base_path):
        return None

    assignment_md = os.path.join(base_path, "assignment.md")
    if not os.path.exists(assignment_md):
        return None

    with open(assignment_md, "r", encoding="utf-8") as f:
        assignment_content = f.read()

    solution_files = read_solution_files(base_path)

    return {
        "id": assignment_id,
        "content": assignment_content,
        "solution_files": solution_files,
    }


def read_solution_files(base_path):
    files = {}
    for root, dirs, filenames in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "vendor", "__pycache__")]
        for filename in filenames:
            if filename == "assignment.md":
                continue
            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, base_path)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    files[rel_path] = f.read()
            except (UnicodeDecodeError, IOError):
                files[rel_path] = "[Binary file - cannot display content]"
    return files
