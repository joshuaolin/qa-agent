import re
import sys
import zipfile


class BodySplitter:
    TOKEN = re.compile(r"<(/?)(w:p|w:tbl|w:sectPr)\b[^>]*?(/?)>")

    def __init__(self, xml):
        self.xml = xml
        self.start = xml.index("<w:body>") + len("<w:body>")
        self.end = xml.rindex("</w:body>")

    def elements(self):
        body = self.xml[self.start:self.end]
        out, depth, begin = [], 0, None
        for m in self.TOKEN.finditer(body):
            closing, selfclose = m.group(1) == "/", m.group(3) == "/"
            if not closing and depth == 0:
                begin = m.start()
            if selfclose:
                if depth == 0:
                    out.append(body[begin:m.end()])
                continue
            depth += -1 if closing else 1
            if depth == 0:
                out.append(body[begin:m.end()])
        return out


if __name__ == "__main__":
    with zipfile.ZipFile(sys.argv[1]) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    parts = BodySplitter(xml).elements()
    print("count", len(parts))
    for i in map(int, sys.argv[2:]):
        print(f"===== [{i}] len={len(parts[i])}")
        print(parts[i][:3000])
