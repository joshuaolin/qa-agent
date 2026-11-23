import json
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, unescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docx_body import BodySplitter

TEXT = re.compile(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", re.S)


class Para:
    RUN = re.compile(r"<w:r(?:\s[^>]*)?>")
    RPR = re.compile(r"<w:r(?:\s[^>]*)?>\s*(<w:rPr>.*?</w:rPr>)", re.S)

    def __init__(self, template):
        self.template = template

    def with_text(self, text):
        ppr_end = self.template.find("</w:pPr>")
        search_from = ppr_end + len("</w:pPr>") if ppr_end >= 0 else self.template.index(">") + 1
        first_run = self.RUN.search(self.template, search_from)
        head = self.template[: first_run.start()] if first_run else self.template[: self.template.rindex("</w:p>")]
        rpr = self.RPR.search(self.template, search_from)
        run = f'<w:r>{rpr.group(1) if rpr else ""}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'
        return head + run + "</w:p>"


class Table:
    ROW = re.compile(r"<w:tr(?:\s[^>]*)?>.*?</w:tr>", re.S)
    CELL = re.compile(r"<w:tc(?:\s[^>]*)?>.*?</w:tc>", re.S)
    T = re.compile(r"<w:t(?:\s[^>]*)?>.*?</w:t>", re.S)

    def __init__(self, template):
        self.template = template
        rows = self.ROW.findall(template)
        self.header, self.data = rows[0], rows[1]
        self.prefix = template[: template.index(rows[0])]

    def fill(self, row, values):
        cells = self.CELL.findall(row)
        if len(cells) != len(values):
            raise ValueError(f"row has {len(values)} values but the template row has {len(cells)} cells: {values}")
        if any(not self.T.search(c) for c in cells):
            raise ValueError("template row has an empty cell with no <w:t>; pick a filled row as the template")
        filled = [self.T.sub(lambda _m, v=v: f'<w:t xml:space="preserve">{escape(v)}</w:t>', c, count=1) for c, v in zip(cells, values)]
        return row[: row.index(cells[0])] + "".join(filled) + "</w:tr>"

    def build(self, rows):
        return self.prefix + self.fill(self.header, rows[0]) + "".join(self.fill(self.data, r) for r in rows[1:]) + "</w:tbl>"

    def append(self, rows):
        end = self.template.rindex("</w:tbl>")
        return self.template[:end] + "".join(self.fill(self.data, r) for r in rows) + "</w:tbl>"

    def replace_row(self, key, values):
        for row in self.ROW.findall(self.template):
            first = self.CELL.findall(row)[0]
            if unescape("".join(TEXT.findall(first))) == key:
                return self.template.replace(row, self.fill(row, values), 1)
        raise KeyError(f"no row starts with {key!r}")


class Package:
    IMAGE_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"

    def __init__(self, path):
        with zipfile.ZipFile(path) as z:
            self.files = {n: z.read(n) for n in z.namelist()}
        self.xml = self.files["word/document.xml"].decode("utf-8")
        self.next_doc_pr = max([int(i) for i in re.findall(r'<wp:docPr id="(\d+)"', self.xml)] or [0]) + 1

    def add_image(self, path, name):
        rels = self.files["word/_rels/document.xml.rels"].decode("utf-8")
        rid = "rId" + str(max(int(i) for i in re.findall(r'Id="rId(\d+)"', rels)) + 1)
        target = f"media/{name}"
        rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="{self.IMAGE_REL}" Target="{target}"/></Relationships>')
        self.files["word/_rels/document.xml.rels"] = rels.encode("utf-8")
        data = Path(path).read_bytes()
        self.files["word/" + target] = data
        return rid, int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")

    def write(self, path, parts):
        start = self.xml.index("<w:body>") + len("<w:body>")
        end = self.xml.rindex("</w:body>")
        self.files["word/document.xml"] = (self.xml[:start] + "".join(parts) + self.xml[end:]).encode("utf-8")
        ct = self.files["[Content_Types].xml"].decode("utf-8")
        if 'Extension="png"' not in ct:
            self.files["[Content_Types].xml"] = ct.replace("<Default ", '<Default Extension="png" ContentType="image/png"/><Default ', 1).encode("utf-8")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for name, data in self.files.items():
                z.writestr(name, data)


class DocxEdit:
    def __init__(self, config_path):
        self.base = Path(config_path).resolve().parent
        self.config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        self.package = Package(self.base / self.config["src"])
        self.parts = BodySplitter(self.package.xml).elements()
        self.templates = {k: self.parts[i] for k, i in self.config["templates"].items()}

    def text_of(self, el):
        return unescape("".join(TEXT.findall(el)))

    def find(self, anchor, start=0):
        for i in range(start, len(self.parts)):
            if self.text_of(self.parts[i]) == anchor:
                return i
        raise KeyError(f"anchor not found: {anchor!r}")

    def locate(self, op):
        if "at" in op:
            return self.find(op["at"])
        return self.find(op["after"]) + op.get("offset", 1)

    def next_index(self, start, predicate):
        return next(i for i in range(start, len(self.parts)) if predicate(self.parts[i]))

    def image(self, template, path, name):
        rid, w, h = self.package.add_image(self.base / path, name)
        cx = self.config.get("image_width_emu", 5705856)
        cy = round(cx * h / w)
        p = re.sub(r'r:embed="rId\d+"', f'r:embed="{rid}"', template)
        p = re.sub(r'cx="\d+" cy="\d+"', f'cx="{cx}" cy="{cy}"', p)
        n = self.package.next_doc_pr
        p = re.sub(r'<wp:docPr id="\d+" name="[^"]*"', f'<wp:docPr id="{n}" name="Picture {n}"', p)
        self.package.next_doc_pr += 1
        return p

    def item(self, spec):
        if "table" in spec:
            return Table(self.templates[spec["table"]]).build(spec["rows"])
        if "image" in spec:
            return self.image(self.templates[spec.get("template", "image")], spec["image"], spec["name"])
        if "raw" in spec:
            return self.templates[spec["raw"]]
        return Para(self.templates[spec["style"]]).with_text(spec["text"])

    def apply(self, op):
        kind = op["op"]
        if kind == "set_text":
            i = self.locate(op)
            source = self.templates[op["style"]] if "style" in op else self.parts[i]
            self.parts[i] = Para(source).with_text(op["text"])
        elif kind == "append_text":
            i = self.locate(op)
            source = self.templates[op["style"]] if "style" in op else self.parts[i]
            self.parts[i] = Para(source).with_text(self.text_of(self.parts[i]) + op["text"])
        elif kind == "insert":
            i = self.find(op["before"]) if "before" in op else self.find(op["after"]) + 1
            self.parts[i:i] = [self.item(s) for s in op["items"]]
        elif kind == "insert_after_image":
            i = self.next_index(self.find(op["after"]), lambda p: "<w:drawing>" in p) + 1
            self.parts[i:i] = [self.item(s) for s in op["items"]]
        elif kind == "replace_image":
            i = self.next_index(self.find(op["after"]), lambda p: "<w:drawing>" in p)
            self.parts[i] = self.image(self.parts[i], op["image"], op["name"])
        elif kind == "append_rows":
            i = self.next_index(self.find(op["after"]), lambda p: p.startswith("<w:tbl"))
            self.parts[i] = Table(self.parts[i]).append(op["rows"])
        elif kind == "replace_row":
            i = self.next_index(self.find(op["after"]), lambda p: p.startswith("<w:tbl"))
            self.parts[i] = Table(self.parts[i]).replace_row(op["key"], op["values"])
        elif kind == "replace_until_end":
            start = self.find(op["after"]) + 1
            end = self.next_index(start, lambda p: p.startswith("<w:sectPr"))
            self.parts[start:end] = [self.item(s) for s in op["items"]]
        else:
            raise ValueError(f"unknown op {kind}")

    def run(self):
        for op in self.config["operations"]:
            self.apply(op)
        out = self.base / self.config["out"]
        self.package.write(out, self.parts)
        print("written", out)


if __name__ == "__main__":
    DocxEdit(sys.argv[1]).run()
