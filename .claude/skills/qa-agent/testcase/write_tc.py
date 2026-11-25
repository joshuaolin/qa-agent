import copy
import datetime
import io
import json
import re
import shutil
import sys
from pathlib import Path

import openpyxl
from openpyxl.drawing.image import Image
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.hyperlink import Hyperlink
from PIL import Image as Picture

FIRST_ROW = 6
STYLE_ROW = 6
COLUMNS = "ABCDEFGHIJKLMNOPQR"
TEMPLATE_SHEET = "Module1"
HEADER_ROW = 5


class SheetRename:
    def __init__(self, old, new):
        self.old = old
        self.new = new

    def apply(self, wb):
        wb[self.old].title = self.new
        quoted = f"'{self.new}'!"
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if isinstance(c.value, str) and c.value.startswith("=") and f"{self.old}!" in c.value:
                        c.value = c.value.replace(f"{self.old}!", quoted)
                    elif c.value == self.old:
                        c.value = self.new
        left = [(ws.title, c.coordinate) for ws in wb.worksheets for row in ws.iter_rows() for c in row if isinstance(c.value, str) and self.old in c.value]
        if left:
            raise SystemExit(f"{self.old} still referenced after rename: {left[:5]}")


class ExtraColumn:
    def __init__(self, col, header, style_from):
        self.col = col
        self.header = header
        self.style_from = style_from

    def add(self, ws):
        src, dst = ws[f"{self.style_from}{HEADER_ROW}"], ws[f"{self.col}{HEADER_ROW}"]
        dst.value = self.header
        dst.font, dst.border, dst.fill, dst.alignment = copy.copy(src.font), copy.copy(src.border), copy.copy(src.fill), copy.copy(src.alignment)
        ws.column_dimensions[self.col].width = ws.column_dimensions[self.style_from].width
BODY_FONT = Font(name="Calibri", size=9)
LINK_FONT = Font(name="Calibri", size=9, color="0563C1", underline="single")
HEADER_FILL = PatternFill("solid", fgColor="B8CCE4")


class Itemized:
    BULLET = "• "
    MAX_SENTENCE = 120

    def __init__(self, tc_id, field):
        self.tc_id = tc_id
        self.field = field

    def items(self, value):
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        lines = [l.strip() for l in str(value).split("\n") if l.strip()]
        if len(lines) == 1 and len(lines[0]) > self.MAX_SENTENCE:
            raise SystemExit(f"{self.tc_id} {self.field} is one {len(lines[0])}-character sentence; write it in tc_rows.json / review.json as a list of short items")
        return lines

    def bullets(self, value):
        items = self.items(value)
        return items[0] if len(items) == 1 else "\n".join(self.BULLET + i for i in items)

    def numbered(self, value):
        return "\n".join(f"{n}. {i}" for n, i in enumerate(self.items(value), start=1))


class TopLevel:
    OPEN, CLOSE = "([", ")]"

    @classmethod
    def split(cls, text, sep):
        out, depth, quoted, start, i = [], 0, False, 0, 0
        while i < len(text):
            ch = text[i]
            if ch == '"':
                quoted = not quoted
            elif not quoted and ch in cls.OPEN:
                depth += 1
            elif not quoted and ch in cls.CLOSE:
                depth = max(0, depth - 1)
            elif not quoted and depth == 0 and text.startswith(sep, i):
                out.append(text[start:i].strip())
                i += len(sep)
                start = i
                continue
            i += 1
        out.append(text[start:].strip())
        return [p for p in out if p]


class WhatWasSeen:
    QUOTE = re.compile(r'"[^"]*"')
    COUNTED = re.compile(r"^(.*?)\s*(#\d+\s.*)$")
    MIN_LISTED = 3
    BULLET = "• "
    SUB = "    – "

    def __init__(self, page_prefix):
        self.page = re.compile(page_prefix)

    def part(self, text):
        if len(self.QUOTE.findall(text)) < self.MIN_LISTED:
            return [self.BULLET + text]
        items = TopLevel.split(text, ", ")
        head = text[:text.index('"')]
        counted = self.COUNTED.match(items[0])
        if head.rstrip().endswith(":") and items[0].startswith(head):
            label, items[0] = head.rstrip(), items[0][len(head):]
        elif counted and counted.group(1):
            label, items[0] = f"{counted.group(1).rstrip(' :')}:", counted.group(2)
        else:
            return [self.BULLET + items[0]] + [self.SUB + i for i in items[1:]]
        return [self.BULLET + label] + [self.SUB + i for i in items]

    def text(self, details):
        out = []
        blocks = details.split(" || ")
        for block in blocks:
            page = self.page.match(block)
            body = block[page.end():] if page else block
            if page:
                out.append(f"{page.group(1)}:")
            for p in TopLevel.split(body, "; "):
                out += self.part(p)
            if len(blocks) > 1:
                out.append("")
        lines = out[:-1] if out and out[-1] == "" else out
        if len(lines) == 1:
            return lines[0][len(self.BULLET):]
        return "\n".join(lines)


class Outcome:
    def __init__(self, results, review, order, unit):
        self.by_seq = {}
        for r in results:
            self.by_seq.setdefault(r["seq"], []).append(r)
        self.review = review
        self.order = order
        self.unit = unit

    def rows(self, seq):
        return sorted(self.by_seq.get(seq, []), key=lambda r: self.order.index(r["locale"]))

    def verdict(self, seq):
        rows = self.rows(seq)
        blocked = self.by_seq.get(99, [])
        note = self.review.get(str(seq), {})
        if not rows and not blocked and not note.get("status"):
            raise SystemExit(f"seq {seq} has no rows in results.json, no seq 99 blocked entry and no review.json status; refusing to call it Passed")
        accepted = set(note.get("passLocales", []))
        fails = [r["locale"] for r in rows if r["status"] == "fail" and r["locale"] not in accepted]
        na = [r["locale"] for r in rows if r["status"] == "na"]
        missing = [l for l in self.order if l not in {r["locale"] for r in rows}]
        if missing and blocked:
            status, summary = "Blocked", f"not executed on {', '.join(missing)}"
        elif fails:
            status, summary = "Failed", f"failed on {', '.join(fails)}"
        else:
            status, summary = "Passed", f"passed on every {self.unit.lower()} run ({', '.join(r['locale'] for r in rows)})"
        if accepted:
            summary += f"; {', '.join(sorted(accepted))} accepted as passed (see remark)"
        if na:
            summary += f"; not applicable on {', '.join(na)} (component not present)"
        if note.get("status"):
            status, summary = note["status"], note.get("summary", summary)

        def label(r):
            if r["status"] == "fail" and r["locale"] in accepted:
                return "ACCEPTED"
            if r["status"] == "fail" and note.get("status") in ("Passed", "Blocked"):
                return note.get("pendingLabel", "PENDING").replace(" (see Remarks)", "")
            return {"na": "N/A"}.get(r["status"], r["status"].upper())

        lines = [(r["locale"], label(r), r["details"]) for r in rows]
        lines += [(l, "NOT RUN", b["details"]) for l in missing for b in blocked if b["locale"] == l]
        notes = Itemized(f"seq {seq}", "remark").items(note["remark"]) if note.get("remark") else []
        remark = "\n".join([f"qa-agent: {summary}"] + [Itemized.BULLET + n for n in notes])
        evidence = [("all", e) for e in note.get("evidence", [])] + [(r["locale"], e) for r in rows for e in r["evidence"]]
        return status, lines, remark, evidence


class Summary:
    QUOTE = re.compile(r'"([^"]*)"')
    ORDER = ["FAIL", "NOT RUN", "BLOCKED", "PENDING PO", "ACCEPTED", "N/A", "PASS"]
    HEADS = {"FAIL": "FAILED", "PASS": "PASSED"}
    DETAILED = {"FAIL", "NOT RUN", "BLOCKED"}
    MAX_QUOTE = 45
    MAX_QUOTES = 2
    MAX_REASON = 170

    def __init__(self, config):
        self.issue = re.compile("|".join(map(re.escape, config["issueWords"])), re.I)
        self.page = re.compile(config["pagePrefix"])

    def quote(self, match):
        text = match.group(1)
        return f'"{text[:self.MAX_QUOTE]}…"' if len(text) > self.MAX_QUOTE else match.group(0)

    def segment(self, seg):
        seg = re.sub(r"https?://[^/\s]+", "", seg)
        quotes = self.QUOTE.findall(seg)
        if len(quotes) > self.MAX_QUOTES:
            head = seg[:seg.index('"')]
            seg = head + ", ".join(f'"{q}"' for q in quotes[:self.MAX_QUOTES]) + f" (+{len(quotes) - self.MAX_QUOTES} more)"
        return self.QUOTE.sub(self.quote, seg)

    def cut(self, text):
        return text if len(text) <= self.MAX_REASON else text[:self.MAX_REASON - 1] + "…"

    def reason(self, details):
        found = {}
        for block in details.split(" || "):
            page = self.page.match(block)
            name = page.group(1) if page else None
            body = block[page.end():] if page else block
            for part in (p.strip() for p in body.split("; ")):
                if part and self.issue.search(part):
                    pages = found.setdefault(self.segment(part), [])
                    if name:
                        pages.append(name)
        if not found:
            return self.cut(self.segment(details))
        return self.cut("; ".join(f"{seg} on {', '.join(pages)}" if pages else seg for seg, pages in found.items()))

    def text(self, lines, tc_id):
        groups = {}
        for locale, label, details in lines:
            groups.setdefault(label, []).append((locale, details))
        out = []
        for label in sorted(groups, key=lambda l: self.ORDER.index(l) if l in self.ORDER else len(self.ORDER)):
            head = self.HEADS.get(label, label)
            if label in self.DETAILED:
                out += [f"{head}: {locale} - {self.reason(details)}" for locale, details in groups[label]]
            else:
                note = " (see Remarks)" if label in ("ACCEPTED", "PENDING PO") else ""
                out.append(f"{head}: {', '.join(l for l, _ in groups[label])}{note}")
        out.append(f"→ What was seen and screenshots for {tc_id}: click this cell")
        return "\n".join(out)


class Screenshot:
    MAX_WIDTH = 830
    MAX_HEIGHT = 1100
    QUALITY = 88

    def __init__(self, path):
        self.path = path
        with Picture.open(path) as pic:
            width, height = pic.size
            scale = min(1, self.MAX_WIDTH / width, self.MAX_HEIGHT / height)
            self.width, self.height = round(width * scale), round(height * scale)
            self.data = io.BytesIO()
            pic.convert("RGB").resize((self.width, self.height), Picture.LANCZOS).save(self.data, format="JPEG", quality=self.QUALITY, optimize=True)

    def place(self, ws, cell):
        self.data.seek(0)
        image = Image(self.data)
        image.width, image.height = self.width, self.height
        ws.add_image(image, cell)


class EvidenceSheet:
    HEADERS = ["Test Case No./ID", "{unit}", "Result", "What was seen", "Screenshot", "Screenshot", "Screenshot"]
    WIDTHS = (16, 9, 11, 48, 128, 128, 128)
    SHOT_COLUMNS = "EFG"
    FILLS = {"PASS": "C6EFCE", "FAIL": "FFC7CE"}
    OTHER_FILL = "FFEB9C"
    CHARS_PER_LINE = 52
    LINE_PT = 12
    MAX_ROW_PT = 409
    CAPTION_PT = 14
    NO_SHOT = "component not on this page; no screenshot taken"
    NOT_EXECUTED = "ticket screenshot (expected look, not a run)"
    REFERENCE = "reference: the same component on a live page, not this ticket's page"

    def __init__(self, wb, folder, unit, no_shot, seen):
        self.ws = wb.create_sheet("Evidence")
        self.folder = Path(folder)
        self.no_shot = no_shot
        self.seen = seen
        self.row = 2
        self.anchors = {}
        self.file_rows = {}
        for i, h in enumerate(self.HEADERS, start=1):
            c = self.ws.cell(row=1, column=i, value=h.format(unit=unit))
            c.font = Font(name="Calibri", size=9, bold=True)
            c.fill = HEADER_FILL
        for i, width in enumerate(self.WIDTHS):
            self.ws.column_dimensions["ABCDEFG"[i]].width = width
        self.ws.freeze_panes = "A2"

    def shots_per_line(self, tc_id, lines, evidence):
        placed = []
        out = []
        for locale, _, _ in lines:
            mine = list(dict.fromkeys(f for l, f in evidence if l in (locale, "all")))
            own = [f for f in mine if f not in placed]
            placed += own
            out.append((own, [f for f in mine if f not in own]))
        if not any(own or shared for own, shared in out) and tc_id not in self.no_shot:
            raise SystemExit(f"{tc_id} has no evidence; a page-source check needs its consolidated table screenshot (TC-<T>-<seq>-all-step<k>.png, k = the column H step it proves)")
        return out

    def caption(self, tc_id, file):
        if "-ref-" in file:
            return f"{self.REFERENCE}: {file}"
        if "-step" not in file:
            return f"{self.NOT_EXECUTED}: {file}"
        step = file.rsplit("-step", 1)[-1].split(".")[0]
        owner = re.match(r"(TC-[A-Za-z0-9]+-(\d+))-", file)
        if owner and owner.group(1) != tc_id:
            return f"TC-{owner.group(2)} step {step}: {file}"
        return f"step {step}: {file}"

    def write_line(self, tc_id, locale, label, details):
        for col, value in enumerate((tc_id, locale, label, details), start=1):
            c = self.ws.cell(row=self.row, column=col, value=value)
            c.font = BODY_FONT
            c.alignment = Alignment(vertical="top", wrap_text=True)
        self.ws.cell(row=self.row, column=3).fill = PatternFill("solid", fgColor=self.FILLS.get(label, self.OTHER_FILL))

    def write_gap(self, tc_id):
        note = self.no_shot.get(tc_id, {"text": self.NO_SHOT})
        gap = self.ws.cell(row=self.row, column=5, value=note["text"])
        gap.font = Font(name="Calibri", size=9, italic=True)
        gap.alignment = Alignment(vertical="top", wrap_text=True)
        if note.get("linkTc") in self.anchors:
            gap.hyperlink = Hyperlink(ref=f"E{self.row}", location=f"'Evidence'!A{self.anchors[note['linkTc']]}")
            gap.font = Font(name="Calibri", size=9, italic=True, color="0563C1", underline="single")

    def write_shots(self, tc_id, files):
        if len(files) > len(self.SHOT_COLUMNS):
            raise SystemExit(f"{len(files)} screenshots on one line; the Evidence sheet has {len(self.SHOT_COLUMNS)} screenshot columns")
        shots = [Screenshot(self.folder / f) for f in files]
        for col, file, shot in zip(self.SHOT_COLUMNS, files, shots):
            cap = self.ws[f"{col}{self.row}"]
            cap.value = self.caption(tc_id, file)
            cap.font = Font(name="Calibri", size=8, italic=True, color="595959")
            cap.alignment = Alignment(vertical="top")
            shot.place(self.ws, f"{col}{self.row + 1}")
        return max(shot.height for shot in shots) * 72 / 96

    def write_shared(self, files):
        first = self.file_rows[files[0]]
        note = self.ws.cell(row=self.row, column=5, value=f"same screenshot as row {first} above: {', '.join(files)}")
        note.hyperlink = Hyperlink(ref=f"E{self.row}", location=f"'Evidence'!A{first}")
        note.font = Font(name="Calibri", size=9, italic=True, color="0563C1", underline="single")
        note.alignment = Alignment(vertical="top", wrap_text=True)

    def merge_text(self, start, end):
        if end > start:
            for col in range(1, 5):
                self.ws.merge_cells(start_row=start, end_row=end, start_column=col, end_column=col)

    def add(self, tc_id, lines, evidence):
        self.anchors[tc_id] = self.row
        for (locale, label, details), (own, shared) in zip(lines, self.shots_per_line(tc_id, lines, evidence)):
            start = self.row
            seen = self.seen.text(details)
            self.write_line(tc_id, locale, label, seen)
            text_pt = self.LINE_PT * sum(max(1, -(-len(l) // self.CHARS_PER_LINE)) for l in seen.split("\n"))
            if not own:
                if shared:
                    self.write_shared(shared)
                else:
                    self.write_gap(tc_id)
                self.ws.row_dimensions[self.row].height = max(text_pt, self.LINE_PT * 2)
                self.row += 1
                continue
            self.file_rows.update({f: start for f in own})
            image_pt = self.write_shots(tc_id, own)
            self.ws.row_dimensions[self.row].height = self.CAPTION_PT
            self.row += 1
            remaining = max(image_pt + 6, text_pt - self.CAPTION_PT)
            while remaining > 0:
                self.ws.row_dimensions[self.row].height = min(self.MAX_ROW_PT, remaining)
                remaining -= self.MAX_ROW_PT
                self.row += 1
            self.merge_text(start, self.row - 1)
        self.row += 1

    def finish(self):
        self.ws.sheet_view.zoomScale = 90


class TcWriter:
    REQUIRED = ("ticket", "project", "order", "precondition", "locales", "summary", "rows")
    SHEET = "Test Cases"
    AUTHOR = "qa-agent"
    STYLE_SOURCE = {"R": "Q"}
    EXTRA = ExtraColumn("R", "Final Validation By", "Q")
    WARN_MB = 20
    WIDTHS = {"E": 30, "G": 34, "H": 55, "I": 38, "K": 60, "M": 40}
    K_CHARS_PER_LINE = 70
    CHARS_PER_WIDTH = 1.1

    def __init__(self, template, out, config, results, review):
        missing = [k for k in self.REQUIRED if k not in config]
        if missing:
            raise SystemExit(f"tc_rows.json is missing {', '.join(missing)}; \"order\" is the locale/env list in run order, \"unit\" (optional) is Locale or Env")
        self.template = Path(template)
        self.out = Path(out)
        self.config = config
        self.unit = config.get("unit", "Locale")
        self.outcome = Outcome(results, review, config["order"], self.unit)
        self.folder = self.out.parent / f"TC-{config['ticket']}-evidence"

    def wrapped_lines(self, ws, col, text):
        per_line = max(12, int((ws.column_dimensions[col].width or 13) * self.CHARS_PER_WIDTH))
        return sum(max(1, -(-len(line) // per_line)) for line in text.split("\n"))

    def copy_style(self, ws, src_row, dst_row):
        for col in COLUMNS:
            src, dst = ws[f"{self.STYLE_SOURCE.get(col, col)}{src_row}"], ws[f"{col}{dst_row}"]
            dst.font, dst.border, dst.fill = copy.copy(src.font), copy.copy(src.border), copy.copy(src.fill)
            dst.alignment = Alignment(horizontal=src.alignment.horizontal, vertical="top", wrap_text=True)
            dst.number_format = src.number_format

    def extend_validations(self, ws, last_row):
        for dv in ws.data_validations.dataValidation:
            ref = str(dv.sqref)
            dv.sqref = openpyxl.worksheet.cell_range.MultiCellRange(f"J{FIRST_ROW}:J{last_row}" if ref.startswith("J") else f"B{FIRST_ROW}:C{last_row}")

    def archive_previous(self, archive):
        if not self.out.exists():
            return None
        if (self.out.parent / f"~${self.out.name}").exists():
            raise SystemExit(f"{self.out.name} is open in Excel; close it first")
        archive.mkdir(exist_ok=True)
        target = archive / f"{self.out.stem}-{datetime.datetime.now():%Y%m%d-%H%M%S}{self.out.suffix}"
        shutil.move(str(self.out), target)
        return target

    def extend_status_colors(self, ws, last_row):
        formats = list(ws.conditional_formatting)
        source = [rule for cf in formats if str(cf.sqref) == f"J{STYLE_ROW}" for rule in cf.rules]
        if not source:
            raise SystemExit(f"no status colour rules on J{STYLE_ROW} in the template")
        existing = {str(cf.sqref) for cf in formats}
        priority = max((rule.priority for cf in formats for rule in cf.rules), default=0)
        for r in range(FIRST_ROW, last_row + 1):
            if f"J{r}" in existing:
                continue
            for rule in source:
                clone = copy.deepcopy(rule)
                clone.formula = [f.replace(f"J{STYLE_ROW}", f"J{r}") for f in rule.formula]
                priority += 1
                clone.priority = priority
                ws.conditional_formatting.add(f"J{r}", clone)

    def dashboard(self, wb, today):
        ws = wb["Dashboard"]
        ws["A10"], ws["F10"], ws["G10"], ws["D12"] = self.config["project"], today, today, self.AUTHOR
        ws["F10"].number_format = ws["G10"].number_format = "yyyy-mm-dd"

    def revision_history(self, wb):
        ws = wb["Revision History"]
        for n, rev in enumerate(self.config.get("revisions", [])):
            r = 9 + n
            if r > 9:
                for col in "ABCDEFGH":
                    src, dst = ws[f"{col}9"], ws[f"{col}{r}"]
                    dst.font, dst.border, dst.fill, dst.alignment, dst.number_format = copy.copy(src.font), copy.copy(src.border), copy.copy(src.fill), copy.copy(src.alignment), src.number_format
            ws[f"A{r}"], ws[f"B{r}"], ws[f"D{r}"], ws[f"H{r}"] = datetime.date.fromisoformat(rev["date"]), rev["version"], rev["description"], rev["author"]

    def run(self, archive):
        archived = self.archive_previous(archive)
        if archived:
            print("previous copy archived to", archived)
        shutil.copyfile(self.template, self.out)
        wb = openpyxl.load_workbook(self.out)
        SheetRename(TEMPLATE_SHEET, self.SHEET).apply(wb)
        ws = wb[self.SHEET]
        ws["A3"] = self.config["project"]
        self.EXTRA.add(ws)
        sheet = EvidenceSheet(wb, self.folder, self.unit, self.config.get("noShot", {}), WhatWasSeen(self.config["summary"]["pagePrefix"]))
        summary = Summary(self.config["summary"])
        today = datetime.date.fromisoformat(self.config["runDate"]) if self.config.get("runDate") else datetime.date.today()
        precondition = Itemized("all rows", "precondition").numbered(self.config["precondition"])
        for col, width in self.WIDTHS.items():
            ws.column_dimensions[col].width = width
        for n, row in enumerate(self.config["rows"]):
            r = FIRST_ROW + n
            tc_id = f"TC-{self.config['ticket']}-{row['seq']:02d}"
            status, lines, remark, evidence = self.outcome.verdict(row["seq"])
            sheet.add(tc_id, lines, evidence)
            self.copy_style(ws, STYLE_ROW, r)
            actual = summary.text(lines, tc_id)
            data = Itemized(tc_id, "data").items(row["data"]) + self.config.get("dataCommon", [])
            expected = Itemized(tc_id, "expected").bullets(row["expected"])
            values = {
                "A": row["requirement"], "B": row["complexity"], "C": row["priority"],
                "D": tc_id, "E": precondition,
                "F": row["name"], "G": Itemized(tc_id, "data").bullets([d.replace("{locales}", self.config["locales"]) for d in data]), "H": row["steps"],
                "I": expected, "J": status, "K": actual, "L": self.AUTHOR,
                "M": remark, "O": today, "P": today, "Q": self.AUTHOR,
            }
            for col, value in values.items():
                ws[f"{col}{r}"] = value
            ws[f"K{r}"].hyperlink = Hyperlink(ref=f"K{r}", location=f"'Evidence'!A{sheet.anchors[tc_id]}", tooltip=f"Open what was seen and the screenshots for {tc_id}")
            ws[f"O{r}"].number_format = ws[f"P{r}"].number_format = "yyyy-mm-dd"
            k_lines = sum(max(1, -(-len(line) // self.K_CHARS_PER_LINE)) for line in actual.split("\n"))
            wrapped = {col: self.wrapped_lines(ws, col, ws[f"{col}{r}"].value) for col in "EGHIM"}
            height = max(k_lines + 1, *(n + 1 for n in wrapped.values()), 8)
            ws.row_dimensions[r].height = min(409, 12 * height)
        sheet.finish()
        last = FIRST_ROW + len(self.config["rows"]) - 1
        self.extend_validations(ws, last)
        self.extend_status_colors(ws, last)
        self.revision_history(wb)
        self.dashboard(wb, today)
        wb.save(self.out)
        self.verify(len(self.config["rows"]))

    def verify(self, count):
        check = openpyxl.load_workbook(self.out)
        m, e = check[self.SHEET], check["Evidence"]
        rules = {str(cf.sqref) for cf in m.conditional_formatting}
        formulas = [c.value for c in check["Dashboard"]["B"] if isinstance(c.value, str) and c.value.startswith("=COUNTIF")]
        print("header R:", m[f"R{HEADER_ROW}"].value, "| L/Q:", m[f"L{FIRST_ROW}"].value, m[f"Q{FIRST_ROW}"].value, "| dashboard COUNTIFs on the renamed sheet:", sum(f"'{self.SHEET}'!" in f for f in formulas), "/", len(formulas))
        for n in range(count):
            r = FIRST_ROW + n
            link = m[f"K{r}"].hyperlink.location if m[f"K{r}"].hyperlink else None
            print(m[f"D{r}"].value, "|", m[f"J{r}"].value, "| colour rules:", f"J{r}" in rules, "|", link, "|", m[f"M{r}"].value[:90])
        size_mb = self.out.stat().st_size / 1024 / 1024
        print("sheets:", check.sheetnames, "| embedded screenshots:", len(e._images), f"| size: {size_mb:.1f} MB")
        if size_mb > self.WARN_MB:
            print(f"WARNING: {size_mb:.1f} MB is over {self.WARN_MB} MB; too big to mail to dev, split the workbook or lower Screenshot.MAX_WIDTH")


if __name__ == "__main__":
    ticket_dir = Path(sys.argv[1]).resolve()
    config = json.loads((ticket_dir / "tc_rows.json").read_text(encoding="utf-8-sig"))
    results = json.loads((ticket_dir / "results.json").read_text(encoding="utf-8-sig"))
    review_path = ticket_dir / "review.json"
    review = json.loads(review_path.read_text(encoding="utf-8-sig")) if review_path.exists() else {}
    TcWriter(sys.argv[2], sys.argv[3], config, results, review).run(ticket_dir / "archive")
