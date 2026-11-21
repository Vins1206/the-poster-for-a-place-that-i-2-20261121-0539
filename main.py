#!/usr/bin/env python3
"""LUMARIS - a vintage travel poster for a place that does not exist.

Draws one 1024x1024 PNG to /output/entry.png using only the Python
standard library.  Every pixel is produced by this file: a hand-written
PNG writer, a small 5x7 bitmap font, and flat vector-style shapes.
No network, no files read, no randomness, no time dependence, so the
output is byte-identical on every run.

The place: LUMARIS, a floating archipelago above a sea of clouds.
One landmark (the great floating isle with its lighthouse and its
waterfalls falling into the clouds), warm ever-spring light, an
airship arriving from the lowlands.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
CREAM = (246, 234, 210)
CREAM_BRIGHT = (255, 247, 224)
PAPER = (248, 235, 203)
TEAL = (20, 66, 78)
TEAL_DARK = (12, 43, 51)
TEAL_MID = (46, 110, 126)
GOLD = (242, 201, 121)
GOLD_DEEP = (230, 168, 74)
SUN = (255, 223, 142)
SUN_CORE = (255, 233, 168)
SKY_MID = (143, 191, 176)
SKY_LOW = (247, 208, 138)
GREEN = (62, 125, 78)
GREEN_DARK = (38, 92, 58)
GREEN_LIGHT = (96, 158, 96)
ROCK = (122, 82, 48)
ROCK_DARK = (92, 58, 34)
ROCK_LIGHT = (150, 108, 66)
WHITE = (255, 255, 255)
HOUSE_WHITE = (250, 244, 228)
ROOF = (201, 69, 44)
AIRSHIP = (200, 69, 44)
AIRSHIP_DARK = (150, 48, 32)
GONDOLA = (90, 58, 40)
WATER = (191, 230, 232)
WATER_DARK = (140, 200, 205)
CLOUD = (255, 247, 224)
CLOUD_SHADE = (253, 239, 200)
INK = (24, 48, 54)

# ------------------------------------------------------------------- font
# A 5x7 bitmap font, drawn from scratch for this poster.  "#" is ink.
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
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
}


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return (
        int(round(lerp(c1[0], c2[0], t))),
        int(round(lerp(c1[1], c2[1], t))),
        int(round(lerp(c1[2], c2[2], t))),
    )


class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)

    def fill_rect(self, x0, y0, x1, y1, color):
        """Fill [x0, x1) x [y0, y1), clipped.  x1/y1 are exclusive."""
        x0 = max(0, int(x0))
        y0 = max(0, int(y0))
        x1 = min(self.w, int(x1))
        y1 = min(self.h, int(y1))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        base = y0 * self.w * 3 + x0 * 3
        stride = self.w * 3
        for y in range(y0, y1):
            off = base + (y - y0) * stride
            self.buf[off:off + len(row)] = row

    def fill_circle(self, cx, cy, r, color):
        r = int(r)
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        rx = int(rx)
        ry = int(ry)
        if rx <= 0 or ry <= 0:
            return
        for dy in range(-ry, ry + 1):
            t = dy / ry
            dx = int(rx * math.sqrt(max(0.0, 1.0 - t * t)))
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)

    def fill_polygon(self, points, color):
        """Scanline fill for a simple polygon given as [(x, y), ...]."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        y0 = max(0, int(min(ys)))
        y1 = min(self.h - 1, int(max(ys)))
        n = len(points)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x1, y1p = points[i]
                x2, y2p = points[(i + 1) % n]
                if (y1p <= y < y2p) or (y2p <= y < y1p):
                    if y2p != y1p:
                        x = x1 + (y - y1p) * (x2 - x1) / (y2p - y1p)
                        xs.append(x)
            if len(xs) >= 2:
                xs.sort()
                self.fill_rect(int(xs[0]), y, int(xs[-1]) + 1, y + 1, color)

    def thick_line(self, x0, y0, x1, y1, width, color):
        """A short straight stroke drawn as a chain of small discs."""
        steps = max(abs(x1 - x0), abs(y1 - y0), 1) + 1
        r = max(1, width // 2)
        for i in range(steps + 1):
            t = i / steps
            x = int(round(x0 + (x1 - x0) * t))
            y = int(round(y0 + (y1 - y0) * t))
            self.fill_circle(x, y, r, color)

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, text, x, y, scale, color):
        """Draw upper-case text; x, y are the top-left of the first glyph."""
        cx = int(x)
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(
                            cx + col * scale,
                            int(y) + row * scale,
                            cx + (col + 1) * scale,
                            int(y) + (row + 1) * scale,
                            color,
                        )
            cx += 6 * scale

    def draw_text_center(self, text, cx, y, scale, color):
        x = cx - self.text_width(text, scale) // 2
        self.draw_text(text, x, y, scale, color)


# ------------------------------------------------------------- the poster
def draw_sky(c, x0, y0, x1, y1):
    """Three-stop vertical sky: deep teal at the top, warm gold low."""
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0 - 1))
        if t < 0.55:
            col = mix(TEAL_MID, SKY_MID, t / 0.55)
        else:
            col = mix(SKY_MID, SKY_LOW, (t - 0.55) / 0.45)
        c.fill_rect(x0, y, x1, y + 1, col)


def draw_cloud(c, cx, cy, s):
    """A soft flat cloud built from overlapping ellipses."""
    c.fill_ellipse(cx, cy, int(70 * s), int(20 * s), CLOUD)
    c.fill_ellipse(cx - int(48 * s), cy + int(6 * s), int(42 * s), int(14 * s), CLOUD)
    c.fill_ellipse(cx + int(50 * s), cy + int(7 * s), int(44 * s), int(14 * s), CLOUD)
    c.fill_ellipse(cx, cy - int(8 * s), int(38 * s), int(16 * s), CLOUD_SHADE)


def draw_island(c, cx, cy, rx, ry, rock_depth, water=False):
    """One floating island: green top, rocky inverted underside."""
    # Rocky underside first, then the green cap sits on top of it.
    top_y = cy
    bot_y = cy + rock_depth
    mid_x = cx
    c.fill_polygon(
        [
            (cx - rx, top_y),
            (cx + rx, top_y),
            (cx + int(rx * 0.42), bot_y),
            (cx - int(rx * 0.42), bot_y),
        ],
        ROCK,
    )
    # Strata: two darker bands across the rock.
    c.fill_polygon(
        [
            (cx - int(rx * 0.88), top_y + int(rock_depth * 0.28)),
            (cx + int(rx * 0.88), top_y + int(rock_depth * 0.28)),
            (cx + int(rx * 0.62), top_y + int(rock_depth * 0.44)),
            (cx - int(rx * 0.62), top_y + int(rock_depth * 0.44)),
        ],
        ROCK_DARK,
    )
    c.fill_polygon(
        [
            (cx - int(rx * 0.66), top_y + int(rock_depth * 0.58)),
            (cx + int(rx * 0.66), top_y + int(rock_depth * 0.58)),
            (cx + int(rx * 0.48), top_y + int(rock_depth * 0.72)),
            (cx - int(rx * 0.48), top_y + int(rock_depth * 0.72)),
        ],
        ROCK_LIGHT,
    )
    # Green cap.
    c.fill_ellipse(cx, cy, rx, ry, GREEN)
    c.fill_ellipse(cx, cy - 4, int(rx * 0.82), int(ry * 0.72), GREEN_LIGHT)
    if water:
        # A waterfall spilling off the left edge into the clouds.
        wx = cx - rx + 18
        c.fill_rect(wx, top_y + 4, wx + 20, top_y + 150, WATER)
        c.fill_rect(wx + 5, top_y + 4, wx + 10, top_y + 150, WHITE)
        c.fill_rect(wx + 14, top_y + 30, wx + 17, top_y + 150, WATER_DARK)
        wx2 = cx + rx - 38
        c.fill_rect(wx2, top_y + 4, wx2 + 14, top_y + 110, WATER)
        c.fill_rect(wx2 + 4, top_y + 4, wx2 + 8, top_y + 110, WHITE)


def draw_house(c, x, y, w, h):
    c.fill_rect(x, y, x + w, y + h, HOUSE_WHITE)
    c.fill_polygon(
        [(x - 4, y), (x + w + 4, y), (x + w // 2, y - 14)], ROOF
    )
    c.fill_rect(x + w // 2 - 3, y + h - 12, x + w // 2 + 3, y + h, TEAL_DARK)


def draw_lighthouse(c, x, y):
    # Tower, gallery and lamp on the great isle.
    c.fill_rect(x, y, x + 22, y + 78, HOUSE_WHITE)
    c.fill_rect(x - 3, y + 30, x + 25, y + 36, ROOF)
    c.fill_rect(x - 3, y + 62, x + 25, y + 68, ROOF)
    c.fill_rect(x + 3, y - 14, x + 19, y, TEAL_DARK)
    c.fill_circle(x + 11, y - 18, 9, GOLD)
    c.fill_circle(x + 11, y - 18, 5, SUN_CORE)


def draw_airship(c, cx, cy):
    # Envelope, stripe, tail fins and gondola.
    c.fill_polygon([(cx + 88, cy - 4), (cx + 118, cy - 22), (cx + 118, cy + 14)], AIRSHIP_DARK)
    c.fill_ellipse(cx, cy, 96, 30, AIRSHIP)
    c.fill_ellipse(cx, cy + 6, 96, 12, CREAM_BRIGHT)
    c.fill_rect(cx - 96, cy - 2, cx + 96, cy + 4, GOLD)
    for wx in range(cx - 64, cx + 65, 28):
        c.fill_circle(wx, cy - 12, 5, CREAM_BRIGHT)
    c.fill_rect(cx - 34, cy + 30, cx + 34, cy + 48, GONDOLA)
    c.fill_rect(cx - 40, cy + 28, cx + 40, cy + 32, TEAL_DARK)
    c.thick_line(cx - 30, cy + 48, cx - 44, cy + 58, 3, GONDOLA)
    c.thick_line(cx + 30, cy + 48, cx + 44, cy + 58, 3, GONDOLA)


def draw_bird(c, x, y, s):
    c.thick_line(x - 9 * s, y, x, y - 6 * s, 3, INK)
    c.thick_line(x, y - 6 * s, x + 9 * s, y, 3, INK)


def build():
    c = Canvas(W, H)
    # Paper ground and double frame.
    c.fill_rect(0, 0, W, H, CREAM)
    c.fill_rect(18, 18, W - 18, H - 18, TEAL_DARK)
    c.fill_rect(26, 26, W - 26, H - 26, CREAM)
    c.fill_rect(34, 34, W - 34, H - 34, TEAL)

    # --- header band: the name, then the promise -----------------------
    c.fill_rect(36, 36, W - 36, 196, TEAL)
    c.fill_rect(36, 192, W - 36, 196, GOLD)
    c.draw_text_center("LUMARIS", 512, 62, 13, TEAL_DARK)
    c.draw_text_center("LUMARIS", 512, 58, 13, PAPER)
    c.draw_text_center("WHERE THE SKY KEEPS ITS ISLANDS", 512, 160, 3, GOLD)

    # --- central picture panel -----------------------------------------
    px0, py0, px1, py1 = 36, 204, 988, 860
    draw_sky(c, px0, py0, px1, py1)

    # Low sun, upper right, warming the whole scene.
    c.fill_circle(796, 330, 108, GOLD_DEEP)
    c.fill_circle(796, 330, 90, SUN)
    c.fill_circle(796, 330, 66, SUN_CORE)

    # High thin clouds.
    draw_cloud(c, 210, 268, 0.8)
    draw_cloud(c, 620, 248, 0.65)
    draw_cloud(c, 880, 430, 0.7)

    # The airship arriving from the lowlands.
    draw_airship(c, 268, 352)

    # Birds over the great isle.
    draw_bird(c, 470, 300, 1)
    draw_bird(c, 520, 282, 1)
    draw_bird(c, 566, 306, 1)
    draw_bird(c, 700, 470, 1)

    # Three floating isles: one great landmark, two companions.
    draw_island(c, 218, 452, 118, 30, 96, water=False)
    draw_island(c, 838, 500, 104, 26, 84, water=False)
    draw_island(c, 540, 528, 232, 48, 196, water=True)

    # Life on the great isle: houses, trees, lighthouse.
    draw_house(c, 420, 482, 34, 26)
    draw_house(c, 468, 488, 28, 20)
    draw_house(c, 648, 484, 32, 24)
    c.fill_circle(392, 496, 14, GREEN_DARK)
    c.fill_circle(612, 500, 12, GREEN_DARK)
    c.fill_circle(700, 498, 13, GREEN_DARK)
    c.fill_circle(392, 488, 9, GREEN_LIGHT)
    c.fill_circle(700, 490, 8, GREEN_LIGHT)
    draw_lighthouse(c, 556, 442)

    # Warm glow on the horizon behind the cloud sea.
    c.fill_ellipse(512, 792, 430, 58, GOLD)
    c.fill_ellipse(512, 800, 340, 44, SUN)

    # A sea of clouds the waterfalls fall into, hiding the rock tips.
    draw_cloud(c, 200, 760, 1.5)
    draw_cloud(c, 470, 800, 1.9)
    draw_cloud(c, 760, 770, 1.6)
    draw_cloud(c, 920, 830, 1.1)
    draw_cloud(c, 90, 830, 1.0)
    c.fill_rect(px0, 836, px1, py1, CLOUD)
    c.fill_ellipse(300, 852, 180, 26, CLOUD_SHADE)
    c.fill_ellipse(700, 854, 200, 24, CLOUD_SHADE)

    # Gold rule closing the picture.
    c.fill_rect(px0, py1 - 4, px1, py1, GOLD)

    # --- footer band: how to get there ---------------------------------
    c.fill_rect(36, 868, W - 36, 988, TEAL)
    c.fill_rect(36, 868, W - 36, 872, GOLD)
    c.draw_text_center("BY AIRSHIP FROM THE LOWLANDS", 512, 888, 3, PAPER)
    c.draw_text_center("EVERSPRING - FARE FROM 12 CROWNS", 512, 928, 3, GOLD)
    return c


# -------------------------------------------------------------------- PNG
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.buf[start:start + stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        return os.path.join(out_dir, "entry.png")
    return "/output/entry.png"


def main():
    canvas = build()
    path = output_path()
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        size = write_png(path, canvas)
    except OSError:
        path = os.path.join("output", "entry.png")
        os.makedirs("output", exist_ok=True)
        size = write_png(path, canvas)
    print("wrote %s (%dx%d, %d bytes)" % (path, W, H, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
