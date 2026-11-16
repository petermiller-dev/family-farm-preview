"""Generate the illustrated wireframe photo placeholders in assets/images/.

Each placeholder is a real WebP file at the final photo's recommended size,
with a subtle "photo needed" label drawn inside the image. Replacing the file
with the real photo (same filename) removes the label automatically.

Usage (needs Pillow):  python3 tools/make-placeholders.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images")
SS = 2  # supersample factor for smooth lines

CREAM = (244, 236, 221)
CREAM_2 = (236, 226, 205)
GREEN_FILL = (221, 227, 205)
GREEN_FILL_2 = (204, 214, 186)
GREEN_FILL_3 = (186, 199, 168)
LINE = (111, 131, 102)
LINE_SOFT = (160, 174, 148)
LABEL_TEXT = (74, 92, 70)

FONT_PATH = "/System/Library/Fonts/Avenir Next.ttc"


def font(size, index=0):
    try:
        return ImageFont.truetype(FONT_PATH, size * SS, index=index)
    except OSError:
        return ImageFont.load_default()


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (w * SS, h * SS), CREAM)
        self.d = ImageDraw.Draw(self.img, "RGBA")

    def p(self, x, y):
        return (x * self.w * SS, y * self.h * SS)

    def lw(self, px):
        return max(1, int(px * SS))

    def poly(self, pts, fill=None, outline=LINE, width=3):
        pts = [self.p(x, y) for x, y in pts]
        if fill:
            self.d.polygon(pts, fill=fill)
        if outline:
            self.d.line(pts + [pts[0]], fill=outline, width=self.lw(width), joint="curve")

    def line(self, pts, color=LINE, width=3):
        self.d.line([self.p(x, y) for x, y in pts], fill=color, width=self.lw(width), joint="curve")

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=LINE, width=3):
        # rx, ry in fractions of width / height respectively
        x0, y0 = self.p(cx - rx, cy - ry)
        x1, y1 = self.p(cx + rx, cy + ry)
        self.d.ellipse([x0, y0, x1, y1], fill=fill, outline=outline, width=self.lw(width))

    def circle(self, cx, cy, r_px, fill=None, outline=LINE, width=3):
        x, y = self.p(cx, cy)
        r = r_px * SS
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=outline, width=self.lw(width))

    def rrect(self, x0, y0, x1, y1, radius_px, fill=None, outline=LINE, width=3):
        a, b = self.p(x0, y0), self.p(x1, y1)
        self.d.rounded_rectangle([a, b], radius=radius_px * SS, fill=fill, outline=outline, width=self.lw(width))

    def wireframe(self):
        """Thin inset frame with corner ticks — the 'wireframe' feel."""
        inset = 0.025
        m = min(self.w, self.h) * inset
        x0, y0, x1, y1 = m, m, self.w - m, self.h - m
        c = LINE_SOFT
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], outline=c + (110,), width=self.lw(1.5))
        t = min(self.w, self.h) * 0.05
        for (cx, cy, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            self.d.line([(cx * SS, (cy + sy * t) * SS), (cx * SS, cy * SS), ((cx + sx * t) * SS, cy * SS)],
                        fill=LINE, width=self.lw(4))

    def label(self, cx, cy, title, filename, size):
        """Subtle pill label: camera glyph, shot description, filename + size."""
        f_small = font(int(size * 0.62), index=1)  # Avenir Next Demi Bold-ish face
        f_main = font(size, index=0)
        f_meta = font(int(size * 0.6))
        l1 = "PHOTO NEEDED"
        l3 = filename
        d = self.d
        widths = [d.textlength(l1, font=f_small) + len(l1) * 3 * SS,
                  d.textlength(title, font=f_main),
                  d.textlength(l3, font=f_meta)]
        pad_x, pad_y = size * 1.3 * SS, size * 0.9 * SS
        line_gap = size * 0.45 * SS
        heights = [size * 0.62 * SS, size * SS, size * 0.6 * SS]
        box_w = max(widths) + pad_x * 2
        box_h = sum(heights) + line_gap * 2 + pad_y * 2
        X, Y = self.p(cx, cy)
        bx0, by0 = X - box_w / 2, Y - box_h / 2
        d.rounded_rectangle([bx0, by0, bx0 + box_w, by0 + box_h], radius=box_h * 0.22,
                            fill=(250, 246, 237, 225), outline=LINE + (150,), width=self.lw(2))
        y = by0 + pad_y
        # letter-spaced eyebrow with a small camera glyph
        cam_w = size * 0.95 * SS
        total = widths[0] + cam_w
        x = X - total / 2
        ch = heights[0]
        d.rounded_rectangle([x, y + ch * 0.05, x + cam_w * 0.72, y + ch * 0.95], radius=ch * 0.18,
                            outline=LABEL_TEXT, width=self.lw(2))
        d.ellipse([x + cam_w * 0.2, y + ch * 0.25, x + cam_w * 0.52, y + ch * 0.75], outline=LABEL_TEXT, width=self.lw(2))
        x += cam_w
        for chr_ in l1:
            d.text((x, y), chr_, font=f_small, fill=LABEL_TEXT, anchor="la")
            x += d.textlength(chr_, font=f_small) + 3 * SS
        y += heights[0] + line_gap
        d.text((X, y), title, font=f_main, fill=(52, 66, 50), anchor="ma")
        y += heights[1] + line_gap
        d.text((X, y), l3, font=f_meta, fill=LABEL_TEXT + (210,), anchor="ma")

    def save(self, name):
        out = self.img.resize((self.w, self.h), Image.LANCZOS)
        path = os.path.join(OUT, name)
        out.save(path, "WEBP", quality=82, method=6)
        print(f"{name}: {self.w}x{self.h}, {os.path.getsize(path) // 1024} KB")


def hill(c, base, amp, freq, phase, fill, width=3):
    pts = []
    for i in range(0, 101):
        x = i / 100
        pts.append((x, base - amp * math.sin(freq * math.pi * x + phase)))
    c.poly(pts + [(1, 1), (0, 1)], fill=fill, outline=None)
    c.line(pts, width=width)
    return pts


def sheep(c, cx, cy, s, facing=1):
    # s is a pixel scale; convert to fractions
    rx, ry = s / c.w, s * 0.62 / c.h
    for dx, dy in [(-0.6, 0.05), (-0.2, -0.25), (0.25, -0.2), (0.55, 0.1), (0, 0.2)]:
        c.ellipse(cx + dx * rx * 0.8, cy + dy * ry, rx * 0.55, ry * 0.6, fill=(250, 246, 237), outline=None)
    c.ellipse(cx, cy, rx, ry, fill=None, width=2.5)
    hx = cx + facing * rx * 1.05
    c.ellipse(hx, cy - ry * 0.35, rx * 0.32, ry * 0.42, fill=CREAM_2, width=2.5)
    for lx in (-0.5, -0.15, 0.2, 0.55):
        c.line([(cx + lx * rx, cy + ry * 0.9), (cx + lx * rx, cy + ry * 1.55)], width=2.5)


def tree(c, x, y, r_px):
    c.line([(x, y), (x, y - r_px * 1.4 / c.h)], width=3)
    c.circle(x, y - r_px * 1.9 / c.h, r_px, fill=GREEN_FILL_2)
    c.circle(x - r_px * 0.6 / c.w, y - r_px * 1.5 / c.h, r_px * 0.7, fill=GREEN_FILL_2)


def make_hero():
    c = Canvas(2400, 1350)
    c.circle(0.80, 0.24, 90, fill=(248, 232, 200), outline=LINE_SOFT, width=3)
    for i, (y, a) in enumerate([(0.18, 0.06), (0.30, 0.05)]):
        c.line([(0.06 + i * 0.05, y), (0.16 + i * 0.05, y)], color=LINE_SOFT, width=3)
    hill(c, 0.56, 0.06, 1.6, 0.4, GREEN_FILL)
    # barn on the far hill
    bx, by = 0.22, 0.52
    c.poly([(bx - 0.04, by), (bx - 0.04, by - 0.08), (bx, by - 0.13), (bx + 0.04, by - 0.08), (bx + 0.04, by)],
           fill=CREAM_2, width=3)
    c.poly([(bx - 0.012, by), (bx - 0.012, by - 0.05), (bx + 0.012, by - 0.05), (bx + 0.012, by)], fill=None, width=2.5)
    tree(c, 0.12, 0.535, 34)
    tree(c, 0.34, 0.50, 28)
    tree(c, 0.90, 0.47, 40)
    hill(c, 0.70, 0.07, 1.1, 1.8, GREEN_FILL_2)
    hill(c, 0.86, 0.05, 1.4, 3.1, GREEN_FILL_3)
    # fence across the middle hill
    for i in range(10):
        x = 0.03 + i * 0.045
        y = 0.70 - 0.07 * math.sin(1.1 * math.pi * x + 1.8)
        c.line([(x, y + 0.01), (x, y - 0.07)], width=3)
    rail = [(0.03 + i * 0.005, 0.70 - 0.07 * math.sin(1.1 * math.pi * (0.03 + i * 0.005) + 1.8) - 0.05) for i in range(82)]
    c.line(rail, width=2.5)
    c.line([(x, y + 0.025) for x, y in rail], width=2.5)
    sheep(c, 0.62, 0.66, 70)
    sheep(c, 0.71, 0.70, 58, facing=-1)
    sheep(c, 0.78, 0.64, 48)
    # grass ticks in the foreground
    for i in range(26):
        x = 0.02 + i * 0.038
        y = 0.93 + 0.02 * math.sin(i * 1.7)
        c.line([(x, y), (x + 0.004, y - 0.03), (x + 0.008, y)], color=LINE, width=2.5)
    c.wireframe()
    # label sits top-centre so it stays inside both desktop and mobile crops
    c.label(0.5, 0.25, "Wide farm or pasture view", "farm-pasture-hero.webp  ·  2400 × 1350", 40)
    c.save("farm-pasture-hero.webp")


def make_eggs():
    c = Canvas(1600, 1200)
    o = -0.08  # lift the scene so the label sits clear of the carton
    c.d.rectangle([0, int((0.72 + o) * c.h * SS), c.w * SS, c.h * SS], fill=CREAM_2)
    c.line([(0, 0.72 + o), (1, 0.72 + o)], color=LINE_SOFT, width=2)
    # open lid behind
    c.poly([(0.16, 0.36 + o), (0.84, 0.36 + o), (0.80, 0.18 + o), (0.20, 0.18 + o)], fill=GREEN_FILL, width=3)
    # carton base
    c.poly([(0.12, 0.40 + o), (0.88, 0.40 + o), (0.84, 0.82 + o), (0.16, 0.82 + o)], fill=GREEN_FILL_2, width=3.5)
    for row, (y, scale) in enumerate([(0.50 + o, 0.95), (0.68 + o, 1.05)]):
        for i in range(6):
            x = 0.215 + i * 0.114
            c.ellipse(x, y + 0.03, 0.047 * scale, 0.05 * scale, fill=GREEN_FILL_3, outline=LINE_SOFT, width=2)
            shade = (250, 245, 234) if (i + row) % 3 else (238, 222, 196)
            c.ellipse(x, y - 0.01, 0.038 * scale, 0.07 * scale, fill=shade, width=3)
            c.line([(x - 0.012, y - 0.05), (x - 0.006, y - 0.06)], color=LINE_SOFT, width=2.5)
    c.wireframe()
    c.label(0.5, 0.87, "Close-up of eggs in a carton", "farm-eggs.webp  ·  1600 × 1200", 34)
    c.save("farm-eggs.webp")


def make_lamb():
    c = Canvas(1600, 1200)
    # board
    c.rrect(0.10, 0.30, 0.90, 0.80, 36, fill=CREAM_2, width=3)
    for i in range(4):
        c.line([(0.14, 0.40 + i * 0.1), (0.86, 0.40 + i * 0.1)], color=LINE_SOFT + (120,), width=1.5)
    # wrapped parcel with twine
    c.rrect(0.16, 0.36, 0.52, 0.70, 18, fill=(250, 245, 234), width=3.5)
    c.line([(0.34, 0.36), (0.34, 0.70)], width=3)
    c.line([(0.16, 0.53), (0.52, 0.53)], width=3)
    c.ellipse(0.34, 0.53, 0.018, 0.022, fill=CREAM_2, width=3)
    c.rrect(0.38, 0.40, 0.49, 0.48, 8, fill=GREEN_FILL, outline=LINE_SOFT, width=2)
    c.line([(0.395, 0.43), (0.47, 0.43)], color=LINE_SOFT, width=2)
    c.line([(0.395, 0.455), (0.45, 0.455)], color=LINE_SOFT, width=2)
    # sealed package with a chop outline
    c.rrect(0.56, 0.38, 0.86, 0.72, 22, fill=GREEN_FILL, width=3.5)
    c.ellipse(0.69, 0.56, 0.08, 0.09, fill=(236, 208, 196), width=3)
    c.ellipse(0.69, 0.56, 0.035, 0.04, fill=(248, 236, 226), outline=LINE_SOFT, width=2)
    c.line([(0.765, 0.53), (0.83, 0.47)], width=8)
    c.circle(0.833, 0.465, 12, fill=CREAM, width=3)
    c.wireframe()
    c.label(0.5, 0.15, "Packaged lamb, as customers receive it", "farm-lamb.webp  ·  1600 × 1200", 34)
    c.save("farm-lamb.webp")


def person(c, x, ground, h_px, fill):
    h = h_px / c.h
    w = h_px * 0.32 / c.w
    c.circle(x, ground - h * 0.88, h_px * 0.11, fill=CREAM_2, width=3)
    c.poly([(x - w / 2, ground - h * 0.74), (x + w / 2, ground - h * 0.74), (x + w * 0.42, ground - h * 0.36),
            (x - w * 0.42, ground - h * 0.36)], fill=fill, width=3)
    c.line([(x - w * 0.2, ground - h * 0.36), (x - w * 0.24, ground)], width=4)
    c.line([(x + w * 0.2, ground - h * 0.36), (x + w * 0.24, ground)], width=4)
    return h, w


def hen(c, x, y, s):
    c.ellipse(x, y, s / c.w, s * 0.7 / c.h, fill=(250, 245, 234), width=2.5)
    c.circle(x + s * 0.8 / c.w, y - s * 0.55 / c.h, s * 0.38, fill=(250, 245, 234), width=2.5)
    c.line([(x + s * 1.15 / c.w, y - s * 0.55 / c.h), (x + s * 1.38 / c.w, y - s * 0.48 / c.h)], width=2.5)
    c.line([(x, y + s * 0.7 / c.h), (x, y + s * 1.05 / c.h)], width=2.5)


def make_family():
    c = Canvas(1200, 1500)
    hill(c, 0.62, 0.03, 1.2, 0.6, GREEN_FILL)
    # barn
    c.poly([(0.08, 0.62), (0.08, 0.44), (0.24, 0.34), (0.40, 0.44), (0.40, 0.62)], fill=CREAM_2, width=3.5)
    c.poly([(0.19, 0.62), (0.19, 0.50), (0.29, 0.50), (0.29, 0.62)], fill=None, width=3)
    c.line([(0.19, 0.50), (0.29, 0.62)], width=2.5)
    c.line([(0.29, 0.50), (0.19, 0.62)], width=2.5)
    tree(c, 0.86, 0.60, 46)
    hill(c, 0.80, 0.025, 1.0, 2.2, GREEN_FILL_2)
    # adult carrying a bucket, child alongside
    ground = 0.86
    h, w = person(c, 0.52, ground, 420, GREEN_FILL_3)
    c.line([(0.52 + w / 2, ground - h * 0.70), (0.52 + w * 0.85, ground - h * 0.40)], width=4)
    c.poly([(0.52 + w * 0.65, ground - h * 0.40), (0.52 + w * 1.05, ground - h * 0.40),
            (0.52 + w * 0.98, ground - h * 0.24), (0.52 + w * 0.72, ground - h * 0.24)], fill=CREAM_2, width=3)
    h2, w2 = person(c, 0.70, ground, 270, GREEN_FILL_2)
    c.line([(0.70 - w2 / 2, ground - h2 * 0.70), (0.52 + w * 1.15, ground - h * 0.40)], width=3.5)
    hen(c, 0.20, 0.84, 34)
    hen(c, 0.30, 0.88, 28)
    c.wireframe()
    c.label(0.5, 0.15, "Family farm chores (if approved)", "farm-family.webp  ·  1200 × 1500", 32)
    c.save("farm-family.webp")


def make_market():
    c = Canvas(1600, 1000)
    c.d.rectangle([0, int(0.80 * c.h * SS), c.w * SS, c.h * SS], fill=CREAM_2)
    # canopy
    c.poly([(0.14, 0.36), (0.50, 0.14), (0.86, 0.36)], fill=GREEN_FILL_2, width=3.5)
    scallop = []
    for i in range(0, 13):
        x0 = 0.14 + i * 0.06
        if x0 >= 0.86:
            break
        c.d.pieslice([*c.p(x0, 0.32), *c.p(x0 + 0.06, 0.42)], 0, 180, fill=GREEN_FILL_2,
                     outline=LINE, width=c.lw(3))
    c.line([(0.14, 0.36), (0.86, 0.36)], width=3)
    c.line([(0.16, 0.40), (0.16, 0.86)], width=4)
    c.line([(0.84, 0.40), (0.84, 0.86)], width=4)
    # table with cloth
    c.poly([(0.22, 0.60), (0.78, 0.60), (0.80, 0.84), (0.20, 0.84)], fill=(250, 245, 234), width=3.5)
    for i in range(1, 8):
        x = 0.20 + i * 0.075
        c.line([(x, 0.62), (x + 0.003, 0.84)], color=LINE_SOFT, width=1.5)
    # cartons and crate on the table
    for i in range(3):
        x = 0.27 + i * 0.09
        c.rrect(x, 0.53, x + 0.075, 0.60, 6, fill=GREEN_FILL, width=2.5)
        for j in range(3):
            c.ellipse(x + 0.014 + j * 0.023, 0.545, 0.009, 0.014, fill=(250, 245, 234), outline=LINE_SOFT, width=1.5)
    c.rrect(0.58, 0.48, 0.74, 0.60, 6, fill=CREAM_2, width=3)
    c.line([(0.58, 0.54), (0.74, 0.54)], width=2)
    # chalkboard sign
    c.poly([(0.86, 0.86), (0.89, 0.58), (0.97, 0.58), (0.98, 0.86)], fill=None, outline=None)
    c.rrect(0.87, 0.58, 0.97, 0.72, 8, fill=GREEN_FILL_3, width=3)
    c.line([(0.89, 0.72), (0.88, 0.86)], width=3)
    c.line([(0.95, 0.72), (0.96, 0.86)], width=3)
    c.wireframe()
    c.label(0.22, 0.13, "Farmers market booth", "farm-market.webp  ·  1600 × 1000", 30)
    c.save("farm-market.webp")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    make_hero()
    make_eggs()
    make_lamb()
    make_family()
    make_market()
