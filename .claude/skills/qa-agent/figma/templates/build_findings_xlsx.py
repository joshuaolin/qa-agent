import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from PIL import Image


class Style:
    HDR = PatternFill("solid", fgColor="B8CCE4")
    ENV = PatternFill("solid", fgColor="DEEAF6")
    FIG = PatternFill("solid", fgColor="EADCF8")
    FEEDBACK = PatternFill("solid", fgColor="FFFFFF")
    SEVERITY = {
        "High": PatternFill("solid", fgColor="F4CCCC"),
        "Medium": PatternFill("solid", fgColor="FCE5CD"),
        "Low": PatternFill("solid", fgColor="FFF2CC"),
    }
    VERDICT = {
        "FAIL": PatternFill("solid", fgColor="F4CCCC"),
        "NEAR": PatternFill("solid", fgColor="FFF2CC"),
        "PASS": PatternFill("solid", fgColor="D9EAD3"),
        "SKIP": PatternFill("solid", fgColor="EFEFEF"),
    }
    THIN = Side(style="thin", color="000000")
    BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    F9 = Font(name="Calibri", size=9)
    F9B = Font(name="Calibri", size=9, bold=True)
    F10B = Font(name="Calibri", size=10, bold=True)
    SUBTITLE = Font(name="Calibri", size=10, color="4A86E8")
    MUTED = Font(name="Calibri", size=9, italic=True, color="7F7F7F")
    WRAP = Alignment(vertical="top", wrap_text=True)
    CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


class FindingsWorkbook:
    def __init__(self, report_dir, out_path):
        self.dir = Path(report_dir)
        self.out = Path(out_path)
        self.data = json.loads((self.dir / "findings.json").read_text(encoding="utf-8"))
        diff_path = self.dir / "diff.json"
        self.diff = json.loads(diff_path.read_text(encoding="utf-8")) if diff_path.exists() else None
        self.wb = Workbook()
        self.title = f"FE Design QA – {self.data['site']} {self.data['component']}"

    def header(self, sheet, subtitle):
        sheet["A1"], sheet["A2"], sheet["A3"] = self.data.get("org", ""), subtitle, self.data.get("project", "")
        sheet["A1"].font = sheet["A2"].font = Style.F10B
        sheet["A3"].font = Style.SUBTITLE

    def cell(self, sheet, row, col, value, font=Style.F9, fill=None, align=Style.WRAP):
        c = sheet.cell(row=row, column=col, value=value)
        c.font, c.alignment, c.border = font, align, Style.BOX
        if fill:
            c.fill = fill
        return c

    def summary(self):
        s = self.wb.active
        s.title = "Summary"
        for col, width in zip("ABCD", (26, 90, 14, 18)):
            s.column_dimensions[col].width = width
        self.header(s, self.title)
        meta = [
            ("Environment", self.data["environment"]),
            ("Viewport / Browser", self.data.get("viewport", "")),
            ("Figma source", self.data.get("figma", "")),
            ("Ticket", self.data.get("ticket", "None given. Design parity only.")),
            ("Run date", self.data.get("runDate", "")),
            ("Verdict", self.data.get("verdict", "")),
        ]
        row = 5
        for key, value in meta:
            self.cell(s, row, 1, key, Style.F9B, Style.HDR)
            self.cell(s, row, 2, value)
            row += 1
        row += 1
        s.cell(row=row, column=1, value="Findings index (details on the Findings sheet)").font = Style.F9B
        row += 1
        for col, head in enumerate(("Finding ID", "Finding", "Severity", "Status"), start=1):
            self.cell(s, row, col, head, Style.F9B, Style.HDR)
        first = row + 1
        for f in self.data["findings"]:
            row += 1
            for col, value in enumerate((f["id"], f["title"], f["severity"], f["status"]), start=1):
                self.cell(s, row, col, value)
            s.cell(row=row, column=3).fill = Style.SEVERITY[f["severity"]]
        last = row
        row += 2
        s.cell(row=row, column=1, value="Findings by severity").font = Style.F9B
        row += 1
        for col, head in enumerate(("Severity", "Count", "Open (Fail)"), start=1):
            self.cell(s, row, col, head, Style.F9B, Style.HDR)
        start = row + 1
        for severity in ("High", "Medium", "Low"):
            row += 1
            self.cell(s, row, 1, severity)
            self.cell(s, row, 2, f"=COUNTIF($C${first}:$C${last},A{row})")
            self.cell(s, row, 3, f'=COUNTIFS($C${first}:$C${last},A{row},$D${first}:$D${last},"Fail")')
        row += 1
        self.cell(s, row, 1, "Total", Style.F9B)
        self.cell(s, row, 2, f"=SUM(B{start}:B{row - 1})", Style.F9B)
        self.cell(s, row, 3, f"=SUM(C{start}:C{row - 1})", Style.F9B)
        for head, key in (("What matches", "matches"), ("Not covered", "notCovered")):
            lines = self.data.get(key, [])
            if not lines:
                continue
            row += 2
            self.cell(s, row, 1, head, Style.F9B, Style.HDR)
            for i, line in enumerate(lines):
                s.cell(row=row + i, column=2, value=f"• {line}").font = Style.F9
                s.cell(row=row + i, column=2).alignment = Style.WRAP
            row += len(lines) - 1

    def place(self, sheet, image_path, anchor, row, max_w=760, max_h=440):
        path = self.dir / image_path
        with Image.open(path) as im:
            scale = min(1.0, max_w / im.width, max_h / im.height)
            width, height = int(im.width * scale), int(im.height * scale)
        picture = XLImage(str(path))
        picture.width, picture.height = width, height
        sheet.add_image(picture, anchor)
        sheet.row_dimensions[row].height = height * 0.75 + 6

    def placeholder(self, sheet, row, text):
        c = sheet.cell(row=row, column=3, value=text)
        c.font, c.alignment = Style.MUTED, Alignment(vertical="center", wrap_text=True)
        sheet.row_dimensions[row].height = 30

    def feedback(self, f):
        return (f"{f['id']} [{f['severity']}] {f['title']}\n\n"
                f"Area / Category: {f.get('area', '')}\nLive element: {f.get('live', '')}\nFigma layer: {f.get('layer', '')}\n\n"
                f"Property: {f.get('property', '')}\nExpected (Figma): {f.get('expected', '')}\nActual (Live): {f.get('actual', '')}\n\n"
                f"Status: {f['status']}\nRemarks: {f.get('remarks', '')}")

    def findings(self):
        fz = self.wb.create_sheet("Findings")
        for col, width in zip("ABC", (12, 12, 112)):
            fz.column_dimensions[col].width = width
        self.header(fz, "FE Design QA – Findings (row 1 = ENV live, row 2 = Figma, row 3 = Feedback)")
        for col, head in enumerate(("Finding", "Row", "Screenshot / Feedback"), start=1):
            self.cell(fz, 5, col, head, Style.F9B, Style.HDR, Style.CENTER)
        fz.freeze_panes = "A6"
        row = 6
        for f in self.data["findings"]:
            fz.merge_cells(start_row=row, start_column=1, end_row=row + 2, end_column=1)
            self.cell(fz, row, 1, f"{f['id']}\n{f['severity']}", Style.F10B, Style.SEVERITY[f["severity"]], Style.CENTER)
            for k, (label, fill) in enumerate((("ENV (Live)", Style.ENV), ("Figma", Style.FIG), ("Feedback", Style.FEEDBACK))):
                self.cell(fz, row + k, 2, label, Style.F9B, fill, Style.CENTER)
                for col in (1, 3):
                    fz.cell(row=row + k, column=col).border = Style.BOX
            for offset, key, missing in ((0, "env", "No live screenshot for this finding."),
                                         (1, "figma", f.get("figmaPending", "No design counterpart for this finding."))):
                if f.get(key):
                    self.place(fz, f[key], f"C{row + offset}", row + offset)
                else:
                    self.placeholder(fz, row + offset, missing)
            c = fz.cell(row=row + 2, column=3, value=self.feedback(f))
            c.font, c.alignment = Style.F9, Style.WRAP
            fz.row_dimensions[row + 2].height = 185
            row += 4

    def css_diff(self):
        if not self.diff:
            return
        cd = self.wb.create_sheet("CSS Diff")
        for col, width in zip("ABCDEFGHI", (14, 44, 34, 22, 14, 18, 7, 10, 34)):
            cd.column_dimensions[col].width = width
        self.header(cd, "FE Design QA – Raw property diff (compare.mjs)")
        heads = ("Element ID", "Live Selector", "Figma Layer", "Property", "Figma", "Live", "Δ", "Verdict", "Notes")
        for col, head in enumerate(heads, start=1):
            self.cell(cd, 5, col, head, Style.F9B, Style.HDR)
        cd.freeze_panes = "A6"
        order = {"FAIL": 0, "NEAR": 1, "SKIP": 2, "PASS": 3}
        notes = self.data.get("diffNotes", {})
        row = 5
        for item in sorted(self.diff.get("all", []), key=lambda x: (order.get(x["verdict"], 4), x["id"], x["property"])):
            row += 1
            norm = item.get("normalized") or {}
            delta = item.get("delta")
            values = (item["id"], item.get("selector", ""), item.get("figmaLayer", ""), item["property"],
                      norm.get("figma", item.get("figma")), norm.get("live", item.get("live")),
                      round(delta, 2) if isinstance(delta, (int, float)) else None, item["verdict"],
                      notes.get(f"{item['id']}.{item['property']}", ""))
            for col, value in enumerate(values, start=1):
                self.cell(cd, row, col, value)
            cd.cell(row=row, column=8).fill = Style.VERDICT.get(item["verdict"], Style.VERDICT["SKIP"])

    def save(self):
        self.summary()
        self.findings()
        self.css_diff()
        self.out.parent.mkdir(parents=True, exist_ok=True)
        self.wb.save(self.out)
        print("saved", self.out, "| findings", len(self.data["findings"]))


if __name__ == "__main__":
    FindingsWorkbook(sys.argv[1], sys.argv[2]).save()
