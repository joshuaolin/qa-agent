import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocxDumper:
    def __init__(self, path):
        self.path = path

    def run(self):
        with zipfile.ZipFile(self.path) as z:
            names = z.namelist()
            root = ET.fromstring(z.read("word/document.xml"))
        print("MEDIA:", [n for n in names if n.startswith("word/media/")])
        body = root.find(W + "body")
        for i, el in enumerate(body):
            tag = el.tag.replace(W, "")
            if tag == "p":
                print(f"[{i}] P <{self.style(el)}> {self.text(el)}{' [IMG]' if self.has_image(el) else ''}")
            elif tag == "tbl":
                print(f"[{i}] TABLE")
                for r in el.iter(W + "tr"):
                    print("    | " + " | ".join(self.text(c) for c in r.findall(W + "tc")))
            else:
                print(f"[{i}] {tag}")

    def style(self, p):
        s = p.find(f"{W}pPr/{W}pStyle")
        return s.get(W + "val") if s is not None else ""

    def text(self, el):
        return "".join(t.text or "" for t in el.iter(W + "t"))

    def has_image(self, el):
        return any(True for _ in el.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"))


if __name__ == "__main__":
    DocxDumper(sys.argv[1]).run()
