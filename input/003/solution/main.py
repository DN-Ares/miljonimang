import json
import os

DATA_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def add_task(title):
    tasks = load_tasks()
    tasks.append({"title": title, "done": False})
    save_tasks(tasks)
    print(f"Ülesanne '{title}' lisatud.")

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("Ülesandeid pole.")
        return
    for i, task in enumerate(tasks, 1):
        status = "✓" if task["done"] else " "
        print(f"{i}. [{status}] {task['title']}")

def mark_done(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index]["done"] = True
        save_tasks(tasks)
        print(f"Ülesanne {index + 1} märgitud tehtuks.")
    else:
        print("Vigane indeks.")

def delete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        removed = tasks.pop(index)
        save_tasks(tasks)
        print(f"Ülesanne '{removed['title']}' kustutatud.")
    else:
        print("Vigane indeks.")

if __name__ == "__main__":
    while True:
        print("\n--- To-do List ---")
        print("1. Lisa ülesanne")
        print("2. Kuva ülesanded")
        print("3. Märgi tehtuks")
        print("4. Kustuta ülesanne")
        print("5. Välju")
        choice = input("Valik: ")

        if choice == "1":
            title = input("Ülesande nimi: ")
            add_task(title)
        elif choice == "2":
            list_tasks()
        elif choice == "3":
            index = int(input("Indeks: ")) - 1
            mark_done(index)
        elif choice == "4":
            index = int(input("Indeks: ")) - 1
            delete_task(index)
        elif choice == "5":
            break
