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

    def body_start(self):
        ppr_end = self.template.find("</w:pPr>")
        return ppr_end + len("</w:pPr>") if ppr_end >= 0 else self.template.index(">") + 1

    def head(self):
        first_run = self.RUN.search(self.template, self.body_start())
        return self.template[: first_run.start()] if first_run else self.template[: self.template.rindex("</w:p>")]

    def run_rpr(self, index):
        runs = list(re.finditer(r"<w:r(?:\s[^>]*)?>(.*?)</w:r>", self.template[self.body_start():], re.S))
        found = re.match(r"\s*(<w:rPr>.*?</w:rPr>)", runs[index].group(1), re.S)
        return found.group(1) if found else ""

    def with_text(self, text):
        rpr = self.RPR.search(self.template, self.body_start())
        return self.with_runs([(text, rpr.group(1) if rpr else "")])

    def with_runs(self, segments):
        runs = "".join(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>' for text, rpr in segments if text)
        return self.head() + runs + "</w:p>"

    def as_list_item(self, num_id):
        num = f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr>'
        if "<w:pPr>" not in self.template:
            return Para(self.template.replace(">", f"><w:pPr>{num}</w:pPr>", 1))
        ppr_start = self.template.index("<w:pPr>")
        ppr = self.template[ppr_start : self.template.index("</w:pPr>") + len("</w:pPr>")]
        clean = re.sub(r"<w:ind\b[^>]*/>|<w:numPr>.*?</w:numPr>", "", ppr, flags=re.S)
        before = list(re.finditer(r"<w:(?:pStyle|keepNext|keepLines|pageBreakBefore|framePr|widowControl)\b[^>]*/>", clean))
        cut = before[-1].end() if before else len("<w:pPr>")
        return Para(self.template.replace(ppr, clean[:cut] + num + clean[cut:], 1))


class RichText:
    TOKEN = re.compile(r"\*\*(.+?)\*\*|`(.+?)`")

    def __init__(self, marks):
        self.marks = marks

    def segments(self, text):
        out, pos = [], 0
        for m in self.TOKEN.finditer(text):
            out.append((text[pos : m.start()], ""))
            out.append((m.group(1), self.marks["bold"]) if m.group(1) is not None else (m.group(2), self.marks["code"]))
            pos = m.end()
        out.append((text[pos:], ""))
        return out


class Table:
    ROW = re.compile(r"<w:tr(?:\s[^>]*)?>.*?</w:tr>", re.S)
    CELL = re.compile(r"<w:tc(?:\s[^>]*)?>.*?</w:tc>", re.S)
    T = re.compile(r"<w:t(?:\s[^>]*)?>.*?</w:t>", re.S)

    PARA = re.compile(r"<w:p(?:\s[^>]*)?>.*?</w:p>", re.S)

    def __init__(self, template, list_num=None):
        self.template = template
        self.list_num = list_num
        rows = self.ROW.findall(template)
        self.header, self.data = rows[0], rows[1]
        self.prefix = template[: template.index(rows[0])]

    def cell(self, cell, value):
        if not isinstance(value, list):
            return self.T.sub(lambda _m: f'<w:t xml:space="preserve">{escape(value)}</w:t>', cell, count=1)
        if self.list_num is None:
            raise ValueError("a list cell needs list_num in the config (a bullet numId from numbering.xml)")
        paras = self.PARA.findall(cell)
        start, end = cell.index(paras[0]), cell.rindex(paras[-1]) + len(paras[-1])
        items = "".join(Para(paras[0]).as_list_item(self.list_num).with_text(v) for v in value)
        return cell[:start] + items + cell[end:]

    def fill(self, row, values):
        cells = self.CELL.findall(row)
        if len(cells) != len(values):
            raise ValueError(f"row has {len(values)} values but the template row has {len(cells)} cells: {values}")
        if any(not self.T.search(c) for c in cells):
            raise ValueError("template row has an empty cell with no <w:t>; pick a filled row as the template")
        filled = [self.cell(c, v) for c, v in zip(cells, values)]
        return row[: row.index(cells[0])] + "".join(filled) + "</w:tr>"

    def insert_row(self, before, values):
        for row in self.ROW.findall(self.template):
            if unescape("".join(TEXT.findall(self.CELL.findall(row)[0]))) == before:
                return self.template.replace(row, self.fill(self.data, values) + row, 1)
        raise KeyError(f"no row starts with {before!r}")

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

    def drop_unused_images(self, body):
        rels_name = "word/_rels/document.xml.rels"
        rels = self.files[rels_name].decode("utf-8")
        used = set(re.findall(r'r:(?:embed|link|id)="([^"]+)"', body))
        for tag in re.findall(r"<Relationship\b[^>]*/>", rels):
            if self.IMAGE_REL in tag and re.search(r'Id="([^"]+)"', tag).group(1) not in used:
                rels = rels.replace(tag, "")
        self.files[rels_name] = rels.encode("utf-8")
        targets = set()
        for name, data in self.files.items():
            if name.endswith(".rels"):
                targets.update(Path(t).name for t in re.findall(r'Target="([^"]+)"', data.decode("utf-8")))
        for name in [n for n in self.files if n.startswith("word/media/") and Path(n).name not in targets]:
            del self.files[name]

    def write(self, path, parts):
        start = self.xml.index("<w:body>") + len("<w:body>")
        end = self.xml.rindex("</w:body>")
        body = "".join(parts)
        self.files["word/document.xml"] = (self.xml[:start] + body + self.xml[end:]).encode("utf-8")
        self.drop_unused_images(self.files["word/document.xml"].decode("utf-8"))
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
        marks = {k: v["rpr"] if "rpr" in v else Para(self.templates[v["template"]]).run_rpr(v["run"]) for k, v in self.config.get("marks", {}).items()}
        self.rich = RichText(marks)

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
            return self.table(self.templates[spec["table"]]).build(spec["rows"])
        if "image" in spec:
            return self.image(self.templates[spec.get("template", "image")], spec["image"], spec["name"])
        if "raw" in spec:
            return self.templates[spec["raw"]]
        para = Para(self.templates[spec["style"]])
        if "list" in spec:
            para = para.as_list_item(spec["list"])
        if "rich" in spec:
            return para.with_runs(self.rich.segments(spec["rich"]))
        return para.with_text(spec["text"])

    def table(self, template):
        return Table(template, self.config.get("list_num"))

    def section(self, heading):
        start = self.find(heading)
        style = re.search(r'<w:pStyle w:val="([^"]+)"', self.parts[start])
        if not style:
            raise ValueError(f"{heading!r} has no paragraph style, so its section end can't be found; use remove with from/until")
        marker = f'<w:pStyle w:val="{style.group(1)}"'
        end = next((i for i in range(start + 1, len(self.parts)) if marker in self.parts[i] or self.parts[i].startswith("<w:sectPr")), len(self.parts))
        return start, end

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
            i = self.find(op["after"])
            for _ in range(op.get("nth", 1)):
                i = self.next_index(i + 1, lambda p: "<w:drawing>" in p)
            self.parts[i] = self.image(self.parts[i], op["image"], op["name"])
        elif kind == "append_rows":
            i = self.next_index(self.find(op["after"]), lambda p: p.startswith("<w:tbl"))
            self.parts[i] = self.table(self.parts[i]).append(op["rows"])
        elif kind == "insert_row":
            i = self.next_index(self.find(op["after"]), lambda p: p.startswith("<w:tbl"))
            self.parts[i] = self.table(self.parts[i]).insert_row(op["before"], op["values"])
        elif kind == "replace_row":
            i = self.next_index(self.find(op["after"]), lambda p: p.startswith("<w:tbl"))
            self.parts[i] = self.table(self.parts[i]).replace_row(op["key"], op["values"])
        elif kind == "remove":
            start = self.find(op["from"])
            end = self.find(op["until"], start) if "until" in op else start + 1
            del self.parts[start:end]
        elif kind == "remove_section":
            start, end = self.section(op["heading"])
            del self.parts[start:end]
        elif kind == "move_section":
            start, end = self.section(op["heading"])
            block = self.parts[start:end]
            del self.parts[start:end]
            i = self.find(op["before"])
            self.parts[i:i] = block
        elif kind == "replace_until_end":
            start = self.find(op["after"]) + 1
            end = self.next_index(start, lambda p: p.startswith("<w:sectPr"))
            self.parts[start:end] = [self.item(s) for s in op["items"]]
        else:
            raise ValueError(f"unknown op {kind}")

    def unique_ids(self):
        seen = set()

        def keep_first(match):
            if match.group(1) in seen:
                return ""
            seen.add(match.group(1))
            return match.group(0)

        self.parts = [re.sub(r' w14:paraId="([^"]+)"', keep_first, part) for part in self.parts]

    def run(self):
        for op in self.config["operations"]:
            self.apply(op)
        self.unique_ids()
        out = self.base / self.config["out"]
        self.package.write(out, self.parts)
        print("written", out)


if __name__ == "__main__":
    DocxEdit(sys.argv[1]).run()
