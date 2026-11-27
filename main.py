#!/usr/bin/env python3
"""News front page for Friday 27 November 2026.

Draws a newspaper front page (1024x1024) that sums up the day's world
news, using only the Python standard library. The PNG encoder and the
5x7 bitmap font are both implemented here by hand; there is no network
access, no randomness and no clock use, so every run writes identical
bytes to /output/entry.png.
"""

import binascii
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (250, 246, 238)
INK = (18, 18, 18)
RED = (166, 30, 30)
BLUE = (30, 58, 95)
GREY = (112, 107, 96)
LIGHT_RULE = (190, 184, 172)

# ---------------------------------------------------------------- font ----
# Compact 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink.
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
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "=": ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}

ADVANCE = 6  # glyph width (5) + 1 column of spacing, in font units


# ------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, w * h * 3, 3):
            self.pix[i] = r
            self.pix[i + 1] = g
            self.pix[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i] = color[0]
            self.pix[i + 1] = color[1]
            self.pix[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pix[i] = color[0]
                self.pix[i + 1] = color[1]
                self.pix[i + 2] = color[2]

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.fill_rect(x0, y + t, x1 - x0, 1, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.fill_rect(x + t, y0, 1, y1 - y0, color)

    def line(self, x0, y0, x1, y1, color):
        # Bresenham's line algorithm.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, thick=2):
        # Midpoint circle, drawn thick by stacking radii.
        for rr in range(r, r + thick):
            x = 0
            y = rr
            d = 1 - rr
            while x <= y:
                for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                               (x, -y), (y, -x), (-x, -y), (-y, -x)):
                    self.set(cx + sx, cy + sy, color)
                if d < 0:
                    d += 2 * x + 3
                else:
                    d += 2 * (x - y) + 5
                    y -= 1
                x += 1

    def ellipse(self, cx, cy, rx, ry, color):
        # Parametric ellipse outline, sampled finely and deterministically.
        steps = 360
        for i in range(steps + 1):
            # Fixed-point style angle via integer table-free trig is not
            # available in stdlib-free form, so use math with a fixed
            # step count: identical on every run for the same inputs.
            import math
            a = 2.0 * math.pi * i / steps
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            self.set(x, y, color)
            self.set(x + 1, y, color)

    def blob(self, cx, cy, rx, ry, color):
        # Filled ellipse blob (a stylised landmass on the globe).
        for yy in range(cy - ry, cy + ry + 1):
            t = (yy - cy) / float(ry)
            half = int(rx * (1.0 - t * t) ** 0.5)
            self.fill_rect(cx - half, yy, half * 2 + 1, 1, color)


# -------------------------------------------------------------- text ------
def text_width(s, scale):
    return len(s) * ADVANCE * scale - scale


def draw_text(cv, s, x, y, scale, color, bold=False):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.fill_rect(cx + col * scale, y + row * scale,
                                 scale, scale, color)
                    if bold:
                        cv.fill_rect(cx + col * scale + 1,
                                     y + row * scale, scale, scale, color)
        cx += ADVANCE * scale
    return cx


def draw_text_centered(cv, s, cx, y, scale, color, bold=False):
    x = cx - text_width(s, scale) // 2
    draw_text(cv, s, x, y, scale, color, bold=bold)


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines = []
    for paragraph in s.split("\n"):
        words = paragraph.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def draw_block(cv, lines, x, y, scale, color, leading, bold=False):
    for line in lines:
        draw_text(cv, line, x, y, scale, color, bold=bold)
        y += 7 * scale + leading
    return y


# -------------------------------------------------------------- globe -----
def draw_globe(cv, cx, cy, r):
    cv.circle(cx, cy, r, INK, thick=3)
    # Meridians and parallels.
    cv.ellipse(cx, cy, r // 3, r, INK)
    cv.ellipse(cx, cy, (2 * r) // 3, r, INK)
    for dy in (-r // 2, 0, r // 2):
        half = int((r * r - dy * dy) ** 0.5)
        cv.hline(cx - half, cx + half, cy + dy, INK)
    # Stylised landmasses, clipped by hand to sit inside the circle.
    cv.blob(cx - r // 3, cy - r // 3, r // 4, r // 5, BLUE)
    cv.blob(cx + r // 4, cy + r // 5, r // 5, r // 4, BLUE)
    cv.blob(cx + r // 10, cy - r // 2, r // 6, r // 7, BLUE)
    cv.blob(cx - r // 2, cy + r // 3, r // 6, r // 6, BLUE)
    # Small star marker for Kuwait on the globe's right side.
    sx, sy = cx + r // 2, cy - r // 6
    cv.fill_rect(sx - 1, sy - 4, 3, 9, RED)
    cv.fill_rect(sx - 4, sy - 1, 9, 3, RED)


# --------------------------------------------------------------- png ------
def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    row_len = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        start = y * row_len
        raw += cv.pix[start:start + row_len]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", ihdr)
            + png_chunk(b"IDAT", idat)
            + png_chunk(b"IEND", b""))


# ------------------------------------------------------------ layout ------
MARGIN = 36
CW = W - 2 * MARGIN  # 952


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.hline(MARGIN, W - MARGIN, 22, INK, thick=3)
    draw_text_centered(cv, "THE WORLD TODAY", W // 2, 36, 8, INK, bold=True)
    cv.hline(MARGIN, W - MARGIN, 104, INK, thick=3)
    cv.hline(MARGIN, W - MARGIN, 108, INK, thick=1)
    draw_text_centered(cv, "FRIDAY 27 NOVEMBER 2026", W // 2, 120, 2, INK,
                       bold=True)
    draw_text(cv, "THE DAY IN WORLD NEWS", MARGIN, 120, 2, GREY)
    draw_text(cv, "ONE DAY, ONE PAGE", W - MARGIN - text_width(
        "ONE DAY, ONE PAGE", 2), 120, 2, GREY)
    cv.hline(MARGIN, W - MARGIN, 144, INK, thick=1)

    # ---- lead story ----
    lead_x = MARGIN
    lead_w = 640
    y = 160
    draw_text(cv, "THE LEAD STORY", lead_x, y, 2, RED, bold=True)
    y += 30
    headline = "TWO ITALIANS KILLED IN IRANIAN DRONE STRIKE IN KUWAIT"
    lines = wrap_text(headline, lead_w, 4)
    y = draw_block(cv, lines, lead_x, y, 4, INK, 8, bold=True)
    y += 10
    deck = ("IRAN DENIES RESPONSIBILITY FOR THE ATTACK, WHICH KILLED "
            "TWO ITALIAN NATIONALS IN KUWAIT.")
    y = draw_block(cv, wrap_text(deck, lead_w, 2), lead_x, y, 2, INK, 6)
    y += 4
    draw_text(cv, "TOP STORY: NYT - BBC - NDTV", lead_x, y, 1, GREY)

    # Globe motif beside the lead story.
    draw_globe(cv, 872, 260, 78)
    draw_text_centered(cv, "THE WORLD", 872, 352, 2, GREY)
    draw_text_centered(cv, "AT A GLANCE", 872, 370, 2, GREY)

    # ---- section divider ----
    cv.hline(MARGIN, W - MARGIN, 396, INK, thick=2)
    draw_text(cv, "MORE FROM AROUND THE WORLD", MARGIN, 408, 2, RED,
              bold=True)
    cv.hline(MARGIN, W - MARGIN, 432, LIGHT_RULE, thick=1)

    # ---- secondary stories, three columns ----
    stories = [
        ("GAZA",
         "HAMAS WEIGHS RESPONSE AFTER ISRAEL KILLS 10 IN GAZA",
         "TEN PEOPLE WERE KILLED IN THE STRIKE. HAMAS IS NOW WEIGHING "
         "ITS RESPONSE, REUTERS REPORTS."),
        ("UNITED STATES",
         "THANKSGIVING STORM FLOODS US AS MACY'S PARADE IS POSTPONED",
         "FLOODING AND FLIGHT DELAYS SPREAD ACROSS THE US. MORE THAN "
         "500,000 HOMES ARE WITHOUT POWER."),
        ("SPAIN",
         "DIESEL TANKER CAPSIZES NEAR IBIZA; ONE KILLED",
         "THE TANKER WAS CARRYING UP TO 7,000 TONNES OF DIESEL WHEN IT "
         "WENT DOWN, THE BBC REPORTS."),
        ("FRANCE",
         "DEPARDIEU TO STAND TRIAL OVER ALLEGED 2018 RAPE",
         "A COURT RULES THE ACTOR MUST FACE TRIAL OVER THE ALLEGED RAPE "
         "OF AN ACTRESS, THE BBC REPORTS."),
        ("UKRAINE",
         "ZELENSKY: US TOO FOCUSED ON MIDDLE EAST",
         "UKRAINE'S PRESIDENT TELLS THE BBC THAT WASHINGTON IS NOT "
         "PUSHING RUSSIA HARD ENOUGH."),
        ("UNITED KINGDOM",
         "UK NET MIGRATION FALLS TO LOWEST SINCE 1997",
         "THE FIGURE IS THE LOWEST SINCE 1997, EXCLUDING THE PANDEMIC "
         "YEARS."),
        ("PHILIPPINES",
         "MOUNT MAYON ERUPTS, ASH CLOUD 3,000M HIGH",
         "THE VOLCANO SENDS AN ASH CLOUD 3,000 METRES INTO THE SKY."),
        ("UNITED STATES",
         "TRUMP SEEKS PROBE INTO 'FAKE' GDP FIGURES",
         "THE PRESIDENT CALLS FOR A PROBE AFTER GROWTH IS REVISED UP "
         "TO 4.3%."),
    ]
    col_w = 301
    col_gap = 24
    col_x = [MARGIN,
             MARGIN + col_w + col_gap,
             MARGIN + 2 * (col_w + col_gap)]
    row_y = [448, 608, 768]
    row_h = 160
    for idx, (tag, head, deck) in enumerate(stories):
        col = idx % 3
        row = idx // 3
        x = col_x[col]
        y = row_y[row]
        draw_text(cv, tag, x, y, 2, RED, bold=True)
        y += 24
        y = draw_block(cv, wrap_text(head, col_w, 2), x, y, 2, INK, 5,
                       bold=True)
        y += 4
        draw_block(cv, wrap_text(deck, col_w, 2), x, y, 2, GREY, 4)
        if col < 2:
            cv.vline(x + col_w + col_gap // 2, row_y[row],
                     row_y[row] + row_h - 16, LIGHT_RULE, thick=1)

    # Third row has only two stories; fill the third cell with a briefs box.
    bx = col_x[2]
    by = row_y[2]
    cv.fill_rect(bx, by, col_w, row_h, (238, 232, 218))
    draw_text(cv, "ALSO TODAY", bx + 12, by + 10, 2, RED, bold=True)
    draw_text(cv, "CHESS: GUKESH AND", bx + 12, by + 34, 2, INK, bold=True)
    draw_text(cv, "SINDAROV DRAW", bx + 12, by + 50, 2, INK, bold=True)
    draw_text(cv, "MARATHON GAME 3", bx + 12, by + 66, 2, INK, bold=True)
    draw_text(cv, "IN THE WORLD CHESS", bx + 12, by + 88, 2, GREY)
    draw_text(cv, "CHAMPIONSHIP.", bx + 12, by + 104, 2, GREY)
    draw_text(cv, "BLACK FRIDAY SALES", bx + 12, by + 124, 2, INK, bold=True)
    draw_text(cv, "BEGIN TODAY.", bx + 12, by + 140, 2, INK, bold=True)

    # ---- footer ----
    cv.hline(MARGIN, W - MARGIN, 944, INK, thick=2)
    draw_text_centered(cv, "THE WORLD TODAY - FRIDAY 27 NOVEMBER 2026",
                       W // 2, 956, 2, INK, bold=True)
    draw_text_centered(cv, "SOURCES: NYT, BBC, REUTERS, NDTV",
                       W // 2, 978, 1, GREY)
    cv.hline(MARGIN, W - MARGIN, 1000, INK, thick=3)

    return cv


def main():
    cv = build()
    data = encode_png(cv)
    os.makedirs("/output", exist_ok=True)
    path = "/output/entry.png"
    with open(path, "wb") as f:
        f.write(data)
    try:
        os.chmod(path, 0o644)
    except OSError:
        pass


if __name__ == "__main__":
    main()
