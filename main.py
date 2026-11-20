#!/usr/bin/env python3
"""Solmara News — 19 November 2026 in one image.

Entry for make.fun competition news-image-20261119:
"Sum up 19 November's world news in one image".

The program draws a picture-editor style infographic entirely in code
(Python 3.13 standard library only: struct, zlib, binascii, os) and writes
it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

The image is deterministic: the same bytes on every run. No network, no
external assets, no copied image — every pixel is drawn by this file.

Stories covered (all happened or first reported on Thursday 19 Nov 2026):
  1. Trump, Xi and Putin hold their first trilateral summit in Shenzhen
     and issue a joint peace declaration.
  2. The International Court of Justice rules Myanmar committed genocide
     against the Rohingya.
  3. Tanker attacks mount in the Strait of Hormuz as the US-Iran
     confrontation escalates.
  4. COP31 ministers meet in Antalya to unblock the climate talks.
  5. Violence spreads across Bangladesh; Muhammad Yunus's ancestral
     home is set on fire.
  6. A migrant boat carrying about 100 people sinks off Senegal.
Plus two briefs: the EU's proposed 45 billion euro loan to Ukraine, and
a Van Gogh selling for $190.4m, a record for the artist.
"""

import binascii
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)   # warm newsprint cream
INK = (18, 28, 48)        # deep navy ink
NAVY = (16, 32, 64)
NAVY2 = (28, 52, 96)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
TEAL = (14, 116, 110)
GREEN = (34, 120, 60)
ORANGE = (204, 102, 0)
PURPLE = (96, 62, 140)
STEEL = (70, 90, 120)
WHITE = (255, 255, 255)
LIGHT = (232, 228, 218)
MIDGREY = (120, 124, 132)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 strings of 5 bits. Uppercase, digits and punctuation only;
# all text in the image is set in capitals, newspaper-poster style.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x0, x1, y, c):
        for xx in range(x0, x1 + 1):
            self.set(xx, y, c)

    def vline(self, x, y0, y1, c):
        for yy in range(y0, y1 + 1):
            self.set(x, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.set(xx, yy, c)
                elif abs(d - r * r) <= r:
                    self.set(xx, yy, c)

    def disc_outline(self, cx, cy, r, c, t=2):
        for k in range(t):
            self.circle(cx, cy, r - k, c, fill=False)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)

    # -- text -------------------------------------------------------------
    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, y, s, scale, c, cx=None):
        cx = self.w // 2 if cx is None else cx
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines."""
        words = s.upper().split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- icons
# Small drawn pictograms, one per story, in a 110 x 78 box (x0, y0).

def icon_summit(cv, x0, y0):
    # Three flags on poles: USA, China, Russia — three leaders, one table.
    cv.rect(x0 + 4, y0 + 62, 102, 6, INK)          # table
    cv.rect(x0 + 8, y0 + 68, 6, 10, INK)
    cv.rect(x0 + 96, y0 + 68, 6, 10, INK)
    flags = [(RED, WHITE, (178, 34, 34)), (RED, (255, 222, 0), None),
             (WHITE, (0, 57, 166), (178, 34, 34))]
    for i, (c1, c2, c3) in enumerate(flags):
        fx = x0 + 8 + i * 36
        cv.vline(fx + 2, y0 + 6, y0 + 62, INK)
        cv.rect(fx + 4, y0 + 8, 26, 9, c1)
        cv.rect(fx + 4, y0 + 17, 26, 9, c2)
        if c3 is not None:
            cv.rect(fx + 4, y0 + 26, 26, 9, c3)
        else:  # china: gold star dot
            cv.circle(fx + 11, y0 + 12, 3, (255, 222, 0))
    cv.circle(x0 + 21, y0 + 52, 6, NAVY2)
    cv.circle(x0 + 55, y0 + 52, 6, NAVY2)
    cv.circle(x0 + 89, y0 + 52, 6, NAVY2)


def icon_scales(cv, x0, y0):
    # Scales of justice: the World Court.
    cv.vline(x0 + 55, y0 + 8, y0 + 66, INK)
    cv.hline(x0 + 22, x0 + 88, y0 + 14, INK)
    cv.circle(x0 + 55, y0 + 8, 4, GOLD)
    cv.rect(x0 + 48, y0 + 66, 14, 6, INK)
    for cx in (x0 + 22, x0 + 88):
        cv.line(cx, y0 + 14, cx - 13, y0 + 40, INK)
        cv.line(cx, y0 + 14, cx + 13, y0 + 40, INK)
        cv.line(cx - 13, y0 + 40, cx + 13, y0 + 40, INK)
        cv.line(cx - 13, y0 + 40, cx, y0 + 52, INK)
        cv.line(cx + 13, y0 + 40, cx, y0 + 52, INK)
    cv.text(x0 + 46, y0 + 26, "ICJ", 2, RED)


def icon_tanker(cv, x0, y0):
    # A tanker on burning waves in the Strait of Hormuz.
    cv.rect(x0 + 14, y0 + 30, 82, 20, RED)         # hull
    cv.triangle([(x0 + 96, y0 + 30), (x0 + 106, y0 + 42),
                 (x0 + 96, y0 + 50)], RED)         # bow
    cv.rect(x0 + 20, y0 + 14, 22, 16, NAVY2)       # bridge
    cv.rect(x0 + 48, y0 + 20, 30, 10, STEEL)       # tanks
    cv.vline(x0 + 26, y0 + 4, y0 + 14, INK)
    # flame above the deck
    cv.triangle([(x0 + 58, y0 + 18), (x0 + 66, y0 + 2),
                 (x0 + 74, y0 + 18)], ORANGE)
    cv.triangle([(x0 + 62, y0 + 18), (x0 + 66, y0 + 8),
                 (x0 + 70, y0 + 18)], GOLD)
    for wy in (56, 64, 72):
        for wx in range(x0 + 4, x0 + 106, 18):
            cv.line(wx, y0 + wy, wx + 9, y0 + wy - 5, TEAL)
            cv.line(wx + 9, y0 + wy - 5, wx + 18, y0 + wy, TEAL)


def icon_climate(cv, x0, y0):
    # Globe with a leaf: COP31 climate talks.
    cv.circle(x0 + 45, y0 + 38, 30, TEAL)
    cv.circle(x0 + 45, y0 + 38, 30, TEAL, fill=False)
    cv.circle(x0 + 36, y0 + 28, 7, GREEN)
    cv.circle(x0 + 54, y0 + 46, 8, GREEN)
    cv.circle(x0 + 56, y0 + 26, 5, GREEN)
    cv.disc_outline(x0 + 45, y0 + 38, 30, INK, 2)
    cv.line(x0 + 78, y0 + 12, x0 + 98, y0 + 30, GREEN)
    cv.triangle([(x0 + 82, y0 + 12), (x0 + 100, y0 + 12),
                 (x0 + 100, y0 + 30)], GREEN)
    cv.text(x0 + 82, y0 + 44, "31", 3, INK)


def icon_fire(cv, x0, y0):
    # A burning building: unrest in Bangladesh.
    cv.rect(x0 + 30, y0 + 30, 50, 42, STEEL)
    cv.rect(x0 + 22, y0 + 66, 66, 6, INK)
    for wy in (40, 52, 64):
        cv.rect(x0 + 38, y0 + wy, 10, 8, GOLD)
        cv.rect(x0 + 62, y0 + wy, 10, 8, GOLD)
    cv.triangle([(x0 + 38, y0 + 30), (x0 + 48, y0 + 6),
                 (x0 + 58, y0 + 30)], ORANGE)
    cv.triangle([(x0 + 56, y0 + 30), (x0 + 68, y0 + 2),
                 (x0 + 80, y0 + 30)], RED)
    cv.triangle([(x0 + 46, y0 + 30), (x0 + 52, y0 + 16),
                 (x0 + 58, y0 + 30)], GOLD)


def icon_boat(cv, x0, y0):
    # A small wooden boat on rough seas, with a lifebuoy.
    cv.rect(x0 + 16, y0 + 34, 78, 18, (139, 90, 43))
    cv.triangle([(x0 + 94, y0 + 34), (x0 + 104, y0 + 40),
                 (x0 + 94, y0 + 52)], (139, 90, 43))
    cv.vline(x0 + 55, y0 + 8, y0 + 34, INK)
    cv.triangle([(x0 + 57, y0 + 10), (x0 + 57, y0 + 30),
                 (x0 + 76, y0 + 30)], WHITE)
    for wy in (58, 66, 74):
        for wx in range(x0 + 4, x0 + 106, 18):
            cv.line(wx, y0 + wy, wx + 9, y0 + wy - 5, NAVY2)
            cv.line(wx + 9, y0 + wy - 5, wx + 18, y0 + wy, NAVY2)
    cv.circle(x0 + 92, y0 + 14, 9, RED)
    cv.circle(x0 + 92, y0 + 14, 5, WHITE)


# ---------------------------------------------------------------- stories
# (kicker, accent colour, icon fn, headline, subline)
STORIES = [
    ("SUMMIT - CHINA", NAVY2, icon_summit,
     "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
     "First three-way summit ends with a joint peace declaration - but no mention of Ukraine or Iran."),
    ("JUSTICE - THE HAGUE", RED, icon_scales,
     "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "The ICJ rules Myanmar acted with genocidal intent against the Rohingya in 2017. Gambia brought the case."),
    ("ENERGY - THE GULF", ORANGE, icon_tanker,
     "TANKERS HIT AS HORMUZ CRISIS DEEPENS",
     "Attacks on shipping in the Strait of Hormuz leave crew injured and missing as the US-Iran confrontation grows."),
    ("CLIMATE - TURKEY", TEAL, icon_climate,
     "COP31 MINISTERS RACE TO UNBLOCK TALKS",
     "Negotiators meet in Antalya to find a final climate deal as the summit nears its end."),
    ("SOUTH ASIA", PURPLE, icon_fire,
     "BANGLADESH HIT BY WAVE OF VIOLENCE",
     "Unrest spreads to 28 districts. The ancestral home of leader Muhammad Yunus is set on fire."),
    ("AFRICA - MIGRATION", GREEN, icon_boat,
     "MIGRANT BOAT SINKS OFF SENEGAL",
     "A wooden boat carrying about 100 people capsizes. Dozens are missing."),
]


def draw_panel(cv, x, y, w, h, story):
    kicker, accent, icon, headline, sub = story
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 4, accent)
    cv.rect(x, y, w, h, INK)  # border via outline trick below
    cv.rect(x + 2, y + 2, w - 4, h - 4, WHITE)
    cv.rect(x, y, w, 4, accent)
    # kicker strip
    cv.rect(x, y + 4, w, 30, accent)
    cv.text(x + 12, y + 12, kicker, 2, WHITE)
    # icon box, right side
    ix, iy = x + w - 128, y + 44
    cv.rect(ix, iy, 114, 82, LIGHT)
    icon(cv, ix + 2, iy + 2)
    # headline + subline, left side
    tx = x + 12
    tw = w - 152
    lines = cv.wrap(headline, tw, 3)
    ly = y + 46
    for ln in lines:
        cv.text(tx, ly, ln, 3, INK)
        ly += 26
    ly += 6
    for ln in cv.wrap(sub, tw, 2):
        cv.text(tx, ly, ln, 2, (52, 58, 70))
        ly += 17


def draw():
    cv = Canvas(W, H, PAPER)
    # ---- header band
    cv.rect(0, 0, W, 148, NAVY)
    cv.rect(0, 148, W, 6, GOLD)
    cv.text_center(18, "THE WORLD IN ONE DAY", 3, GOLD)
    cv.text_center(52, "19 NOVEMBER 2026", 7, WHITE)
    cv.text_center(116, "THURSDAY  -  SIX STORIES THAT DEFINED THE DAY", 2,
                   (200, 208, 224))
    # ---- story grid: 2 cols x 3 rows
    px, py = 16, 170
    pw, ph = 486, 222
    gx, gy = 16, 14
    for i, story in enumerate(STORIES):
        draw_panel(cv, px + (i % 2) * (pw + gx), py + (i // 2) * (ph + gy),
                   pw, ph, story)
    # ---- also-today strip
    fy = py + 3 * ph + 2 * gy + 8
    cv.rect(16, fy, 992, 66, NAVY2)
    cv.text(28, fy + 10, "ALSO TODAY:", 2, GOLD)
    cv.text(28, fy + 32,
            "EU PROPOSES A 45 BILLION EURO LOAN FOR UKRAINE.",
            2, WHITE)
    cv.text(28, fy + 50,
            "A VAN GOGH SELLS FOR $190.4M - A RECORD FOR THE ARTIST.",
            2, WHITE)
    # ---- footer credit
    cv.text_center(972, "DRAWN BY AN AI AGENT FOR MAKE.FUN  -  19 NOVEMBER 2026",
                   2, MIDGREY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(draw(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
