#!/usr/bin/env python3
"""THE WORLD TODAY - Thursday 26 November 2026.

A code-drawn newspaper poster that sums up the day's world news in one
1024x1024 PNG. Pure standard library, fully deterministic: the same input
always writes the same bytes. No network, no clock, no randomness.

Layout (top to bottom): masthead, six-number band, four big leads with
large scenic art, twelve scene cards, the ALSO list, a filled-continent
world map with pins, an explicit DATE CHECK box, and a footer dating claim.
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)
INK = (24, 24, 24)
SOFT = (74, 74, 74)
RED = (158, 28, 33)
BLUE = (28, 74, 116)
NAVY = (18, 38, 66)
SKY = (196, 222, 236)
SEA = (214, 231, 240)
LAND = (224, 205, 158)
LANDLINE = (150, 128, 84)
GOLD = (198, 148, 42)
CREAM = (252, 248, 238)
GREY = (120, 120, 116)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font

# 5x7 bitmap glyphs, one row per string, '#' = ink.
GLYPH = {
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
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}

CLEAN = {"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
         "\u2014": "-", "\u2013": "-", "\u2022": "*", "\u2026": ".",
         "\u00a0": " "}


def tidy(text):
    out = []
    for ch in text:
        ch = CLEAN.get(ch, ch)
        out.append(ch.upper() if ch.isalpha() else ch)
    return "".join(out)


# ---------------------------------------------------------------- canvas

class Poster:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.px = bytearray(PAPER * (w * h))

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o], self.px[o + 1], self.px[o + 2] = c

    def box(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            for xx in range(x0, x1):
                self.px[o], self.px[o + 1], self.px[o + 2] = c
                o += 3

    def frame(self, x, y, w, h, c, t=1):
        self.box(x, y, w, t, c)
        self.box(x, y + h - t, w, t, c)
        self.box(x, y, t, h, c)
        self.box(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.box(cx - dx, cy + dy, dx * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=1):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            inner = int(((r - t) * (r - t) - dy * dy) ** 0.5) if abs(dy) < r - t else -1
            for xx in range(cx - dx, cx + dx + 1):
                if abs(xx - cx) > inner:
                    self.dot(xx, cy + dy, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.box(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.dot(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def glyph(self, ch, x, y, sc, c):
        rows = GLYPH.get(ch)
        if not rows:
            return
        for r, row in enumerate(rows):
            for col, bit in enumerate(row):
                if bit == "1":
                    self.box(x + col * sc, y + r * sc, sc, sc, c)

    def text(self, s, x, y, sc, c):
        s = tidy(s)
        cx = x
        for ch in s:
            self.glyph(ch, cx, y, sc, c)
            cx += 6 * sc
        return cx - x

    def text_w(self, s, sc):
        return len(tidy(s)) * 6 * sc

    def wrap(self, s, max_chars):
        words, lines, cur = tidy(s).split(), [], ""
        for word in words:
            trial = (cur + " " + word).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, s, x, y, w, s_scale, c, leading=None):
        max_chars = max(1, w // (6 * s_scale))
        lead = leading if leading is not None else 9 * s_scale
        yy = y
        for line in self.wrap(s, max_chars):
            self.text(line, x, yy, s_scale, c)
            yy += lead
        return yy


# ---------------------------------------------------------------- scenes
# Every scene painter takes a box (x, y, w, h) and draws with fractions of
# it, so the same painter serves the big lead art and the small card art.

def sc_rocket(p, x, y, w, h):
    p.box(x, y, w, h, (14, 22, 48))
    for sx, sy in ((0.12, 0.15), (0.3, 0.08), (0.55, 0.2), (0.78, 0.1), (0.9, 0.28), (0.42, 0.3)):
        p.dot(int(x + w * sx), int(y + h * sy), WHITE)
    p.disc(int(x + w * 0.82), int(y + h * 0.62), max(2, int(h * 0.34)), (58, 110, 158))
    p.disc(int(x + w * 0.82), int(y + h * 0.62), max(2, int(h * 0.26)), (90, 140, 185))
    p.box(int(x + w * 0.55), int(y + h * 0.42), max(3, int(w * 0.2)), max(2, int(h * 0.05)), (200, 200, 200))
    p.box(int(x + w * 0.60), int(y + h * 0.36), max(3, int(w * 0.1)), max(2, int(h * 0.05)), (200, 200, 200))
    rx, rw = int(x + w * 0.2), max(6, int(w * 0.045))
    rh = int(h * 0.52)
    ry = int(y + h * 0.18)
    p.box(rx, ry, rw, rh, WHITE)
    p.poly([(rx, ry), (rx + rw, ry), (rx + rw // 2, ry - int(h * 0.12))], RED)
    p.box(rx, ry + rh // 3, rw, max(2, int(h * 0.04)), BLUE)
    p.disc(rx + rw // 2, ry + rh // 4, max(2, rw // 3), SKY)
    p.poly([(rx, ry + rh), (rx - int(w * 0.03), ry + rh + int(h * 0.1)),
            (rx + rw // 3, ry + rh)], RED)
    p.poly([(rx + rw, ry + rh), (rx + rw + int(w * 0.03), ry + rh + int(h * 0.1)),
            (rx + rw * 2 // 3, ry + rh)], RED)
    p.poly([(rx + rw // 4, ry + rh), (rx + rw * 3 // 4, ry + rh),
            (rx + rw // 2, ry + rh + int(h * 0.2))], GOLD)
    p.disc(int(x + w * 0.5), int(y + h * 0.9), max(2, int(h * 0.06)), GOLD)


def sc_jet(p, x, y, w, h):
    p.box(x, y, w, h, SKY)
    p.disc(int(x + w * 0.85), int(y + h * 0.2), max(3, int(h * 0.12)), (255, 236, 160))
    for r in (0.2, 0.3, 0.4):
        p.ring(int(x + w * 0.8), int(y + h * 0.55), int(h * r), (90, 120, 150), 2)
    jx, jy = int(x + w * 0.28), int(y + h * 0.42)
    p.poly([(jx, jy), (jx + int(w * 0.3), jy - int(h * 0.08)),
            (jx + int(w * 0.34), jy), (jx + int(w * 0.3), jy + int(h * 0.08))], (70, 74, 80))
    p.poly([(jx + int(w * 0.1), jy), (jx + int(w * 0.16), jy - int(h * 0.16)),
            (jx + int(w * 0.2), jy)], (70, 74, 80))
    p.poly([(jx + int(w * 0.1), jy), (jx + int(w * 0.16), jy + int(h * 0.16)),
            (jx + int(w * 0.2), jy)], (70, 74, 80))
    p.box(int(x + w * 0.05), int(y + h * 0.78), int(w * 0.5), max(2, int(h * 0.05)), (120, 140, 120))
    p.box(int(x + w * 0.05), int(y + h * 0.84), int(w * 0.35), max(2, int(h * 0.04)), (90, 110, 90))


def sc_candles(p, x, y, w, h):
    p.box(x, y, w, h, (52, 52, 58))
    p.disc(int(x + w * 0.8), int(y + h * 0.2), max(3, int(h * 0.1)), (200, 200, 210))
    n = 7
    for i in range(n):
        cx = int(x + w * (0.1 + 0.8 * i / (n - 1)))
        base = int(y + h * 0.88)
        stick = int(h * (0.3 + 0.12 * ((i * 37) % 3)))
        p.box(cx - 2, base - stick, 4, stick, CREAM)
        p.disc(cx, base - stick - max(2, int(h * 0.05)), max(2, int(h * 0.045)), GOLD)
        p.disc(cx, base - stick - max(2, int(h * 0.05)), max(1, int(h * 0.02)), (255, 220, 120))
    p.box(x, int(y + h * 0.88), w, max(2, int(h * 0.04)), (30, 30, 34))


def sc_ship(p, x, y, w, h):
    p.box(x, y, w, h, SKY)
    p.box(x, int(y + h * 0.55), w, int(h * 0.45), (52, 96, 140))
    for i, bh in enumerate((0.5, 0.42, 0.55, 0.46)):
        bx = int(x + w * (0.14 + i * 0.05))
        bw = max(3, int(w * 0.035))
        p.box(bx, int(y + h * bh), bw, int(h * 0.14), (40 + i * 40, 70 + i * 30, 120))
    p.box(int(x + w * 0.1), int(y + h * 0.62), int(w * 0.75), max(3, int(h * 0.1)), (30, 30, 36))
    p.box(int(x + w * 0.68), int(y + h * 0.5), int(w * 0.08), max(3, int(h * 0.12)), WHITE)
    for i, bh in enumerate((0.35, 0.5, 0.62, 0.55)):
        bx = int(x + w * (0.78 + i * 0.045))
        p.box(bx, int(y + h * (0.85 - bh)), max(3, int(w * 0.03)), int(h * bh), RED)


def sc_raid(p, x, y, w, h):
    p.box(x, y, w, h, (74, 74, 84))
    p.box(int(x + w * 0.08), int(y + h * 0.25), int(w * 0.84), int(h * 0.6), (120, 96, 70))
    p.box(int(x + w * 0.08), int(y + h * 0.18), int(w * 0.84), max(2, int(h * 0.08)), RED)
    p.box(int(x + w * 0.4), int(y + h * 0.45), int(w * 0.2), int(h * 0.4), (40, 40, 48))
    for i in range(3):
        fx = int(x + w * (0.2 + i * 0.28))
        fy = int(y + h * 0.55)
        p.disc(fx, fy, max(2, int(h * 0.06)), (230, 200, 170))
        p.box(fx - max(2, int(w * 0.02)), fy + max(2, int(h * 0.05)), max(4, int(w * 0.04)), int(h * 0.22), NAVY)
    p.disc(int(x + w * 0.85), int(y + h * 0.12), max(2, int(h * 0.07)), RED)
    p.disc(int(x + w * 0.85), int(y + h * 0.12), max(1, int(h * 0.035)), GOLD)


def sc_sewing(p, x, y, w, h):
    p.box(x, y, w, h, (232, 214, 178))
    p.box(int(x + w * 0.1), int(y + h * 0.62), int(w * 0.8), max(2, int(h * 0.05)), (120, 90, 60))
    p.box(int(x + w * 0.3), int(y + h * 0.35), int(w * 0.3), max(3, int(h * 0.1)), (60, 60, 66))
    p.box(int(x + w * 0.3), int(y + h * 0.45), int(w * 0.42), max(2, int(h * 0.04)), (60, 60, 66))
    p.box(int(x + w * 0.55), int(y + h * 0.28), max(2, int(w * 0.02)), int(h * 0.2), (60, 60, 66))
    for i, c in enumerate(((190, 60, 60), (60, 120, 190), (60, 160, 90))):
        fx = int(x + w * (0.68 + i * 0.1))
        p.box(fx, int(y + h * 0.42), max(3, int(w * 0.06)), int(h * 0.2), c)
        p.disc(fx + max(2, int(w * 0.03)), int(y + h * 0.4), max(2, int(h * 0.03)), WHITE)
    p.box(int(x + w * 0.12), int(y + h * 0.55), int(w * 0.3), max(2, int(h * 0.06)), (200, 90, 120))


def sc_door(p, x, y, w, h):
    p.box(x, y, w, h, (200, 190, 170))
    p.box(int(x + w * 0.3), int(y + h * 0.1), int(w * 0.4), int(h * 0.8), (110, 80, 55))
    p.frame(int(x + w * 0.3), int(y + h * 0.1), int(w * 0.4), int(h * 0.8), (70, 50, 35), 2)
    p.box(int(x + w * 0.38), int(y + h * 0.2), int(w * 0.24), int(h * 0.12), WHITE)
    p.text("CLOSED", int(x + w * 0.4), int(y + h * 0.23), 1, RED)
    p.disc(int(x + w * 0.62), int(y + h * 0.55), max(2, int(h * 0.04)), GOLD)
    p.box(int(x + w * 0.08), int(y + h * 0.82), int(w * 0.84), max(2, int(h * 0.05)), (90, 80, 70))


def sc_handshake(p, x, y, w, h):
    p.box(x, y, w, h, SKY)
    p.box(int(x + w * 0.08), int(y + h * 0.15), int(w * 0.16), int(h * 0.5), (255, 153, 51))
    p.box(int(x + w * 0.08), int(y + h * 0.15), int(w * 0.16), int(h * 0.17), (255, 153, 51))
    p.box(int(x + w * 0.08), int(y + h * 0.32), int(w * 0.16), int(h * 0.16), WHITE)
    p.disc(int(x + w * 0.16), int(y + h * 0.4), max(2, int(h * 0.05)), NAVY)
    p.box(int(x + w * 0.76), int(y + h * 0.15), int(w * 0.16), int(h * 0.5), (220, 20, 60))
    p.box(int(x + w * 0.76), int(y + h * 0.32), int(w * 0.16), int(h * 0.16), WHITE)
    p.disc(int(x + w * 0.84), int(y + h * 0.4), max(2, int(h * 0.05)), NAVY)
    p.box(int(x + w * 0.3), int(y + h * 0.55), int(w * 0.4), max(3, int(h * 0.14)), (230, 200, 170))
    p.disc(int(x + w * 0.42), int(y + h * 0.55), max(3, int(h * 0.08)), (230, 200, 170))
    p.disc(int(x + w * 0.58), int(y + h * 0.55), max(3, int(h * 0.08)), (200, 170, 140))
    p.box(int(x + w * 0.3), int(y + h * 0.72), int(w * 0.4), max(2, int(h * 0.04)), (90, 70, 55))


def sc_oil(p, x, y, w, h):
    p.box(x, y, w, h, SKY)
    p.box(x, int(y + h * 0.6), w, int(h * 0.4), (46, 88, 130))
    p.box(int(x + w * 0.2), int(y + h * 0.5), int(w * 0.6), max(3, int(h * 0.1)), (50, 50, 56))
    p.poly([(int(x + w * 0.42), int(y + h * 0.5)), (int(x + w * 0.58), int(y + h * 0.5)),
            (int(x + w * 0.54), int(y + h * 0.12)), (int(x + w * 0.46), int(y + h * 0.12))], (70, 70, 76))
    p.box(int(x + w * 0.47), int(y + h * 0.2), int(w * 0.06), int(h * 0.28), (50, 50, 56))
    p.disc(int(x + w * 0.5), int(y + h * 0.1), max(2, int(h * 0.05)), GOLD)
    p.disc(int(x + w * 0.85), int(y + h * 0.18), max(3, int(h * 0.1)), (255, 236, 160))
    p.box(int(x + w * 0.12), int(y + h * 0.68), int(w * 0.2), max(2, int(h * 0.05)), WHITE)


def sc_shop(p, x, y, w, h):
    p.box(x, y, w, h, (240, 228, 205))
    p.box(int(x + w * 0.08), int(y + h * 0.3), int(w * 0.84), int(h * 0.55), (150, 110, 75))
    p.box(int(x + w * 0.08), int(y + h * 0.22), int(w * 0.84), max(2, int(h * 0.08)), RED)
    p.box(int(x + w * 0.15), int(y + h * 0.45), int(w * 0.25), int(h * 0.4), (190, 220, 235))
    p.box(int(x + w * 0.6), int(y + h * 0.45), int(w * 0.25), int(h * 0.4), (60, 60, 66))
    p.disc(int(x + w * 0.5), int(y + h * 0.6), max(2, int(h * 0.05)), (230, 200, 170))
    p.box(int(x + w * 0.46), int(y + h * 0.65), max(3, int(w * 0.08)), int(h * 0.2), BLUE)
    p.text("SALE", int(x + w * 0.4), int(y + h * 0.08), 1, RED)


def sc_asteroid(p, x, y, w, h):
    p.box(x, y, w, h, (12, 14, 34))
    for sx, sy in ((0.15, 0.12), (0.4, 0.08), (0.7, 0.2), (0.88, 0.1), (0.25, 0.3)):
        p.dot(int(x + w * sx), int(y + h * sy), WHITE)
    cx, cy, r = int(x + w * 0.5), int(y + h * 0.55), max(4, int(h * 0.32))
    p.disc(cx, cy, r, (150, 140, 130))
    p.disc(cx - r // 3, cy - r // 4, max(1, r // 4), (110, 100, 92))
    p.disc(cx + r // 3, cy + r // 5, max(1, r // 5), (110, 100, 92))
    p.disc(cx + r // 5, cy - r // 2, max(1, r // 6), (120, 110, 100))
    p.box(int(x + w * 0.78), int(y + h * 0.2), max(3, int(w * 0.1)), max(2, int(h * 0.05)), (200, 200, 200))
    p.box(int(x + w * 0.8), int(y + h * 0.14), max(2, int(w * 0.06)), max(2, int(h * 0.05)), (150, 150, 160))
    p.line(cx + r // 2, cy - r // 2, int(x + w * 0.82), int(y + h * 0.24), GOLD)


def sc_chess(p, x, y, w, h):
    p.box(x, y, w, h, (210, 190, 160))
    n = 4
    cw, ch = w // n, h // n
    for r in range(n):
        for c in range(n):
            if (r + c) % 2 == 0:
                p.box(x + c * cw, y + r * ch, cw, ch, (250, 246, 236))
            else:
                p.box(x + c * cw, y + r * ch, cw, ch, (40, 40, 44))
    kx, ky = int(x + w * 0.25), int(y + h * 0.25)
    p.box(kx - 3, ky - 3, 6, 6, WHITE)
    p.box(kx - 5, ky - 8, 10, 4, WHITE)
    p.disc(kx, ky - 10, 2, WHITE)
    qx, qy = int(x + w * 0.7), int(y + h * 0.65)
    p.box(qx - 3, qy - 3, 6, 6, INK)
    p.box(qx - 5, qy - 8, 10, 4, INK)
    p.disc(qx, qy - 10, 2, INK)


def sc_islands(p, x, y, w, h):
    p.box(x, y, w, h, (140, 190, 220))
    p.box(x, int(y + h * 0.6), w, int(h * 0.4), (40, 110, 170))
    p.poly([(int(x + w * 0.1), int(y + h * 0.62)), (int(x + w * 0.38), int(y + h * 0.62)),
            (int(x + w * 0.24), int(y + h * 0.42))], (90, 150, 90))
    p.poly([(int(x + w * 0.6), int(y + h * 0.62)), (int(x + w * 0.88), int(y + h * 0.62)),
            (int(x + w * 0.74), int(y + h * 0.46))], (110, 160, 100))
    p.line(int(x + w * 0.24), int(y + h * 0.42), int(x + w * 0.24), int(y + h * 0.28), (90, 70, 50))
    p.line(int(x + w * 0.74), int(y + h * 0.46), int(x + w * 0.74), int(y + h * 0.32), (90, 70, 50))
    p.disc(int(x + w * 0.82), int(y + h * 0.18), max(3, int(h * 0.1)), (255, 236, 160))


def sc_canal(p, x, y, w, h):
    p.box(x, y, w, h, (230, 220, 190))
    p.box(int(x + w * 0.05), int(y + h * 0.4), int(w * 0.9), int(h * 0.3), (70, 130, 170))
    p.box(int(x + w * 0.3), int(y + h * 0.28), int(w * 0.4), max(3, int(h * 0.12)), (40, 40, 46))
    p.box(int(x + w * 0.45), int(y + h * 0.16), int(w * 0.1), max(2, int(h * 0.12)), (40, 40, 46))
    p.box(int(x + w * 0.05), int(y + h * 0.32), int(w * 0.14), int(h * 0.08), (120, 160, 90))
    p.box(int(x + w * 0.81), int(y + h * 0.32), int(w * 0.14), int(h * 0.08), (120, 160, 90))
    p.box(int(x + w * 0.05), int(y + h * 0.72), int(w * 0.9), max(2, int(h * 0.05)), (120, 160, 90))


def sc_ev(p, x, y, w, h):
    p.box(x, y, w, h, (225, 228, 232))
    p.box(int(x + w * 0.06), int(y + h * 0.55), int(w * 0.88), max(2, int(h * 0.06)), (90, 96, 102))
    cx, cy = int(x + w * 0.5), int(y + h * 0.45)
    p.box(cx - int(w * 0.3), cy, int(w * 0.6), max(3, int(h * 0.14)), (30, 120, 190))
    p.poly([(cx - int(w * 0.18), cy), (cx - int(w * 0.1), cy - int(h * 0.14)),
            (cx + int(w * 0.12), cy - int(h * 0.14)), (cx + int(w * 0.2), cy)], (30, 120, 190))
    p.disc(cx - int(w * 0.18), cy + int(h * 0.14), max(2, int(h * 0.07)), INK)
    p.disc(cx + int(w * 0.18), cy + int(h * 0.14), max(2, int(h * 0.07)), INK)
    p.disc(cx - int(w * 0.18), cy + int(h * 0.14), max(1, int(h * 0.03)), GREY)
    p.disc(cx + int(w * 0.18), cy + int(h * 0.14), max(1, int(h * 0.03)), GREY)
    p.poly([(int(x + w * 0.82), int(y + h * 0.2)), (int(x + w * 0.86), int(y + h * 0.12)),
            (int(x + w * 0.9), int(y + h * 0.2)), (int(x + w * 0.86), int(y + h * 0.3))], GOLD)


SCENES = {"rocket": sc_rocket, "jet": sc_jet, "candles": sc_candles,
          "ship": sc_ship, "raid": sc_raid, "sewing": sc_sewing,
          "door": sc_door, "handshake": sc_handshake, "oil": sc_oil,
          "shop": sc_shop, "asteroid": sc_asteroid, "chess": sc_chess,
          "islands": sc_islands, "canal": sc_canal, "ev": sc_ev}

# ---------------------------------------------------------------- content

LEADS = [
    {"kicker": "SPACE - LAUNCHED 25 NOV", "scene": "rocket",
     "head": "Pakistan's first astronaut boards China's station",
     "deck": "Shenzhou-24 lifts off from Jiuquan and docks at Tiangong after a "
             "3.5-hour flight. Muhammad Zeeshan Ali, 40, is the first Pakistani "
             "in orbit.",
     "src": "(REUTERS / CMSA)"},
    {"kicker": "EUROPE - 24 NOV", "scene": "jet",
     "head": "Poland: second Russian incursion in four days",
     "deck": "A Russian drone enters Polish airspace overnight; jets are cleared "
             "to shoot it down but hold fire. Three Kh-101 missiles crossed in "
             "four days earlier.",
     "src": "(REUTERS)"},
    {"kicker": "WAR TOLL", "scene": "candles",
     "head": "Russia's own figures: nearly 500,000 lost in Ukraine",
     "deck": "Moscow's own count puts its losses in the Ukraine war at nearly "
             "half a million people.",
     "src": "(JAGRANJOSH)"},
    {"kicker": "ECONOMY", "scene": "ship",
     "head": "US prepares new tariffs plan",
     "deck": "Washington is preparing to unveil a plan for new tariffs on "
             "global trading partners.",
     "src": "(JAGRANJOSH)"},
]

CARDS = [
    ("COLOMBIA", "Police storm supermarket, free 20 held hostage 17 hours.", "raid", "JAGRANJOSH"),
    ("BANGLADESH", "Garment workers win 36% wage rise.", "sewing", "26 NOV REPORTS"),
    ("NORTH KOREA", "Pyongyang orders Switzerland to close its office.", "door", "SELFSTUDYS"),
    ("INDIA / NEPAL", "India announces Rs 15,000 crore Nepal package.", "handshake", "SELFSTUDYS"),
    ("VENEZUELA", "Caracas reveals $237.5B public debt, plans restructuring.", "oil", "LIBRE"),
    ("BRAZIL", "Petrobras unveils $122B investment strategy.", "oil", "LIBRE"),
    ("CANADA", "Consumer confidence nears a two-year high.", "shop", "LIBRE"),
    ("SPACE", "Close-up images of the asteroid hit to test planetary defence.", "asteroid", "JAGRANJOSH"),
    ("CHESS", "Gukesh plays Sindarov in the World Chess Championship.", "chess", "SELFSTUDYS"),
    ("PACIFIC", "Australia and Solomon Islands strike security pact.", "islands", "LIBRE"),
    ("EGYPT", "Suez Canal revenues gradually recovering.", "canal", "LIBRE"),
    ("SOUTH KOREA", "Seoul moves to reinforce its EV industry.", "ev", "LIBRE"),
]

ALSO = [
    "Xi graft probe upends Shanghai star's path",
    "US shelves Russia deal plan to end war - FT",
    "US AG dodges Nvidia probe questions",
    "Israeli minister: Iran making chemical arms",
    "Crews search for six after Gulf plane crash",
    "Fort Hood survivors lose final appeal",
    "Hasina seeks return to Bangladesh 16 Dec",
    "Flipkart CEO Krishnamurthy to step down",
    "IPL 2027 auction draws 1,220 players",
    "Sooryavanshi smashes 204 off 53 vs UAE",
    "India calls for human control over AI in war",
    "Indian banks write off Rs 1.44 lakh crore",
    "Ethiopia champions healthcare independence",
    "El Salvador allocates $860M debt financing",
    "Barbados sets Feb deadline for AI rules",
    "France seeks independence in minerals",
    "Britain probes nuclear testing legacy",
    "Vietnam advances sustainable agriculture",
    "Russia raises defence; Ukraine, Hungary talk",
    "Colombia marks 10 years since peace accord",
]

NUMBERS = [
    ("500,000", "Russians lost in Ukraine, per Russia's own figures"),
    ("$237.5B", "Venezuela's public debt, revealed"),
    ("$122B", "Petrobras investment strategy"),
    ("1,220", "players in IPL 2027 auction"),
    ("36%", "Bangladesh garment wage rise"),
    ("20", "hostages freed in Colombia rescue"),
]

DATECHECK = [
    "25 NOV: Shenzhou-24 launches 08:18 Beijing, docks Tiangong 11:56.",
    "20 NOV: 3 Russian Kh-101 missiles enter Poland; confirmed 22 Nov.",
    "21 NOV: BepiColombo reaches Mercury - the week's space story.",
    "22 NOV: COP31 collapses in Antalya - no 26 Nov fallout used.",
    "26 NOV 2025: Wang Fuk Court fire, Hong Kong - NOT today's news.",
]

PINS = [
    ("JIUQUAN", 98, 40, -8, -14), ("WARSAW", 21, 52, -50, -12),
    ("KYIV", 30, 50, 6, 6), ("BOGOTA", -74, 5, 4, -4),
    ("DHAKA", 90, 24, 4, -14), ("CARACAS", -67, 10, 4, -16),
    ("NEW DELHI", 77, 29, 4, 10), ("HONIARA", 160, -9, -52, -4),
    ("CAIRO", 31, 30, -48, 2),
]

CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-55, 60),
     (-60, 47), (-75, 35), (-80, 25), (-97, 16), (-105, 20), (-120, 34),
     (-125, 48), (-150, 60), (-165, 60)],
    [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-77, -20), (-80, -5)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (43, 12), (51, 10), (40, -5), (35, -18), (28, -32),
     (20, -35), (15, -27), (12, -18), (9, 4), (-8, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (8, 57), (18, 56),
     (21, 55), (28, 60), (30, 70), (40, 68), (45, 60), (40, 55),
     (30, 45), (28, 40), (23, 36), (18, 40), (12, 44), (3, 42), (-2, 37)],
    [(40, 68), (60, 70), (80, 73), (100, 77), (120, 73), (140, 72),
     (160, 70), (178, 66), (170, 60), (162, 55), (158, 50), (142, 45),
     (140, 40), (135, 35), (130, 33), (127, 40), (120, 38), (115, 30),
     (108, 20), (105, 10), (100, 8), (95, 15), (90, 22), (85, 20),
     (80, 15), (75, 8), (70, 20), (65, 25), (60, 25), (55, 26),
     (50, 28), (48, 30), (45, 35), (42, 40)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
]

# ---------------------------------------------------------------- sections

def draw_masthead(p):
    p.box(10, 8, 1004, 3, RED)
    title = "THE WORLD TODAY"
    tw = p.text_w(title, 6)
    p.text(title, (W - tw) // 2, 16, 6, INK)
    p.box(10, 62, 1004, 2, INK)
    p.text("THURSDAY 26 NOVEMBER 2026", 12, 68, 2, INK)
    right = "LATE EDITION * NO. 330"
    p.text(right, W - 12 - p.text_w(right, 2), 68, 2, RED)


def draw_numbers(p):
    y0, y1 = 82, 122
    p.frame(10, y0, 1004, y1 - y0, INK, 1)
    cw = 1004 // 6
    for i, (num, label) in enumerate(NUMBERS):
        x = 10 + i * cw
        if i:
            p.box(x, y0 + 4, 1, y1 - y0 - 8, GREY)
        nw = p.text_w(num, 2)
        p.text(num, x + (cw - nw) // 2, y0 + 3, 2, RED)
        p.para(label, x + 6, y0 + 21, cw - 12, 1, SOFT, leading=9)


def draw_lead(p, x, y, w, h, lead):
    p.frame(x, y, w, h, INK, 1)
    p.text(lead["kicker"], x + 8, y + 6, 1, RED)
    p.text(lead["src"], x + w - 8 - p.text_w(lead["src"], 1), y + 6, 1, SOFT)
    p.para(lead["head"], x + 8, y + 18, w - 16, 2, INK, leading=17)
    art_y = y + 54
    art_h = 140
    SCENES[lead["scene"]](p, x + 8, art_y, w - 16, art_h)
    p.frame(x + 8, art_y, w - 16, art_h, INK, 1)
    p.para(lead["deck"], x + 8, art_y + art_h + 5, w - 16, 1, SOFT, leading=10)


def draw_card(p, x, y, w, h, card):
    region, line, scene, src = card
    p.frame(x, y, w, h, INK, 1)
    aw = 64
    SCENES[scene](p, x + 1, y + 1, aw, h - 2)
    p.box(x + aw + 1, y, 1, h, GREY)
    tx = x + aw + 8
    p.text(region, tx, y + 5, 1, RED)
    p.para(line, tx, y + 16, w - aw - 14, 1, INK, leading=9)
    p.text("(" + src + ")", tx, y + h - 12, 1, SOFT)


def draw_also(p, x, y, w):
    p.text("ALSO IN THE NEWS", x, y, 1, RED)
    p.box(x, y + 11, w, 1, INK)
    half = (len(ALSO) + 1) // 2
    colw = w // 2
    for i, item in enumerate(ALSO):
        col = i // half
        row = i % half
        ix = x + col * colw
        iy = y + 16 + row * 11
        p.disc(ix + 2, iy + 3, 2, RED)
        p.text(str(i + 1) + ". " + item, ix + 8, iy, 1, INK)


def draw_map(p, x, y, w, h):
    p.frame(x, y, w, h, INK, 1)
    p.box(x + 1, y + 1, w - 2, h - 2, SEA)
    for lon in range(-150, 181, 30):
        px = x + int((lon + 180) / 360 * w)
        for yy in range(y + 4, y + h - 4, 8):
            p.dot(px, yy, (170, 195, 210))
    for lat in (-30, 0, 30, 60):
        py = y + int((90 - lat) / 150 * h)
        for xx in range(x + 4, x + w - 4, 8):
            p.dot(xx, py, (170, 195, 210))

    def mx(lon):
        return x + int((lon + 180) / 360 * w)

    def my(lat):
        return y + int((90 - lat) / 150 * h)

    for cont in CONTINENTS:
        pts = [(mx(lon), my(lat)) for lon, lat in cont]
        p.poly(pts, LAND)
        n = len(pts)
        for i in range(n):
            p.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0], pts[(i + 1) % n][1], LANDLINE)
    for name, lon, lat, dx, dy in PINS:
        px, py = mx(lon), my(lat)
        p.disc(px, py, 3, RED)
        p.disc(px, py, 1, WHITE)
        p.text(name, px + dx, py + dy, 1, INK)
    p.text("WHERE THE NEWS HAPPENED", x, y + h + 4, 1, SOFT)


def draw_datecheck(p, x, y, w, h):
    p.frame(x, y, w, h, RED, 2)
    p.text("DATE CHECK - WHAT HAPPENED WHEN", x + 6, y + 5, 1, RED)
    yy = y + 16
    for line in DATECHECK:
        p.disc(x + 8, yy + 3, 2, RED)
        p.text(line, x + 14, yy, 1, INK)
        yy += 9


def draw_footer(p):
    p.box(10, 994, 1004, 1, INK)
    claim = ("EVERY STORY HERE HAPPENED, OR WAS FIRST REPORTED, ON THURSDAY "
             "26 NOVEMBER 2026 IN AT LEAST ONE TIME ZONE.")
    cw = p.text_w(claim, 1)
    p.text(claim, (W - cw) // 2, 999, 1, INK)
    srcs = "SOURCES: REUTERS - CMSA - XINHUA - KYIV INDEPENDENT - FT - AP - JAGRANJOSH - SELFSTUDYS - LIBRE"
    sw = p.text_w(srcs, 1)
    p.text(srcs, (W - sw) // 2, 1010, 1, SOFT)


# ---------------------------------------------------------------- build

def build():
    p = Poster()
    draw_masthead(p)
    draw_numbers(p)
    lw, lh = 497, 220
    draw_lead(p, 10, 126, lw, lh, LEADS[0])
    draw_lead(p, 517, 126, lw, lh, LEADS[1])
    draw_lead(p, 10, 352, lw, lh, LEADS[2])
    draw_lead(p, 517, 352, lw, lh, LEADS[3])
    cw, ch = 247, 70
    for i, card in enumerate(CARDS):
        cx = 10 + (i % 4) * (cw + 4)
        cy = 578 + (i // 4) * (ch + 3)
        draw_card(p, cx, cy, cw, ch, card)
    draw_also(p, 10, 800, 586)
    draw_map(p, 604, 800, 410, 116)
    draw_datecheck(p, 10, 928, 586, 62)
    draw_footer(p)
    return bytes(p.px)


def png_bytes(rgb, w=W, h=H):
    raw = b"".join(b"\x00" + rgb[y * w * 3:(y + 1) * w * 3] for y in range(h))
    comp = zlib.compress(raw, 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def verify(path):
    """Re-read the written PNG and check gate facts: dims, size, magic."""
    import hashlib
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG magic"
    w, h = struct.unpack(">II", data[16:24])
    assert (w, h) == (1024, 1024), "dims %dx%d" % (w, h)
    assert len(data) <= 1048576, "over 1 MiB: %d" % len(data)
    print("verify ok: %s %dx%d %d bytes sha256 %s"
          % (path, w, h, len(data), hashlib.sha256(data).hexdigest()))
    return data


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))
    verify(path)


if __name__ == "__main__":
    main()
