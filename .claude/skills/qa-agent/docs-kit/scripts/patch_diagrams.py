import json
import sys
from pathlib import Path


class DiagramPatch:
    def __init__(self, folder, changes_file):
        self.folder = Path(folder)
        self.spec = json.loads((self.folder / changes_file).read_text(encoding="utf-8"))

    def run(self):
        source = self.folder / self.spec["from"]
        html = source.read_text(encoding="utf-8")
        for old, new in self.spec["changes"]:
            if html.count(old) != 1:
                raise SystemExit(f"expected one match for: {old[:60]}")
            html = html.replace(old, new)
        (self.folder / "diagrams.html").write_text(html, encoding="utf-8")
        print(f"diagrams.html = {self.spec['from']} + {len(self.spec['changes'])} changes")


if __name__ == "__main__":
    DiagramPatch(sys.argv[1], sys.argv[2]).run()
