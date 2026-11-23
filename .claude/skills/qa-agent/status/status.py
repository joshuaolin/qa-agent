import datetime
import json
import sys
from pathlib import Path


class StatusBoard:
    STATES = ("doing", "waiting-owner", "blocked", "todo", "done")
    ICONS = {"doing": "▶", "waiting-owner": "⏳", "blocked": "⛔", "todo": "·", "done": "✓"}

    def __init__(self, repo):
        self.folder = Path(repo).resolve() / "qa-reports"
        self.folder.mkdir(exist_ok=True)
        self.data_file = self.folder / "status.json"
        self.view_file = self.folder / "STATUS.md"
        self.tasks = json.loads(self.data_file.read_text(encoding="utf-8")) if self.data_file.exists() else {}

    def now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def add(self, task_id, title, state="todo", note=""):
        if task_id in self.tasks:
            raise SystemExit(f"{task_id} already exists; use set")
        self.tasks[task_id] = {"title": title, "state": state, "note": note, "updated": self.now(), "history": []}
        self.set(task_id, state, note)

    def set(self, task_id, state, note=""):
        if task_id not in self.tasks:
            raise SystemExit(f"no task {task_id}; add it first")
        if state not in self.STATES:
            raise SystemExit(f"state must be one of {', '.join(self.STATES)}")
        task = self.tasks[task_id]
        task.update(state=state, note=note or task["note"], updated=self.now())
        task["history"].append([task["updated"], state, note])

    def render(self):
        lines = ["# QA status", "", f"Updated {self.now()}. States: " + ", ".join(f"{self.ICONS[s]} {s}" for s in self.STATES), "", "| | Task | State | Note | Updated |", "| --- | --- | --- | --- | --- |"]
        for state in self.STATES:
            for task_id, t in sorted(self.tasks.items(), key=lambda kv: kv[1]["updated"], reverse=True):
                if t["state"] == state:
                    lines.append(f"| {self.ICONS[state]} | **{task_id}** {t['title']} | {state} | {t['note'].replace('|', '/')} | {t['updated']} |")
        return "\n".join(lines) + "\n"

    def save(self):
        self.data_file.write_text(json.dumps(self.tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        self.view_file.write_text(self.render(), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    board = StatusBoard(sys.argv[1])
    command, rest = sys.argv[2], sys.argv[3:]
    if command == "add":
        board.add(rest[0], rest[1], *(rest[2:4]))
    elif command == "set":
        board.set(rest[0], rest[1], rest[2] if len(rest) > 2 else "")
    elif command != "list":
        raise SystemExit("usage: status.py <repo> add <id> <title> [state] [note] | set <id> <state> [note] | list")
    board.save()
    print(board.render())
