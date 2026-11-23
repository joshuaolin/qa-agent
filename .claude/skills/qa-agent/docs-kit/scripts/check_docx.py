import re
import sys
import zipfile
import xml.etree.ElementTree as ET

BOM = chr(0xFEFF)


class DocxChecker:
    def __init__(self, path):
        self.path = path
        self.problems = []

    def run(self):
        with zipfile.ZipFile(self.path) as z:
            names = set(z.namelist())
            for n in names:
                if n.endswith(".xml") or n.endswith(".rels"):
                    try:
                        ET.fromstring(z.read(n))
                    except ET.ParseError as e:
                        self.problems.append(f"bad xml {n}: {e}")
            doc = z.read("word/document.xml").decode("utf-8")
            rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
            ct = z.read("[Content_Types].xml").decode("utf-8")
        rel_map = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rels))
        for rid in re.findall(r'r:embed="(rId\d+)"', doc):
            target = rel_map.get(rid)
            if not target or "word/" + target not in names:
                self.problems.append(f"broken image ref {rid} -> {target}")
        ids = re.findall(r'<wp:docPr id="(\d+)"', doc)
        if len(ids) != len(set(ids)):
            self.problems.append(f"duplicate docPr ids {ids}")
        if 'Extension="png"' not in ct:
            self.problems.append("png content type missing")
        if BOM in doc:
            self.problems.append("literal U+FEFF in document.xml")
        print("images:", len(re.findall(r"r:embed=", doc)), "docPr:", ids)
        print("OK" if not self.problems else "\n".join(self.problems))


if __name__ == "__main__":
    DocxChecker(sys.argv[1]).run()
