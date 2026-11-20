import re
import sys


class TextOnlySvg:
    BACKGROUND_FILL = re.compile(r'<rect\b[^>]*fill="url\(#(?:pattern|paint)[^"]*\)"[^>]*/>\s*')
    IMAGE = re.compile(r"<image\b[^>]*/>\s*")

    def __init__(self, src, out):
        self.src = src
        self.out = out

    def run(self):
        with open(self.src, encoding="utf-8") as f:
            svg = f.read()
        before = len(svg)
        svg, rects = self.BACKGROUND_FILL.subn("", svg)
        svg, images = self.IMAGE.subn("", svg)
        with open(self.out, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"removed {rects} background rects and {images} image(s): {before} -> {len(svg)} chars")


if __name__ == "__main__":
    TextOnlySvg(sys.argv[1], sys.argv[2]).run()
