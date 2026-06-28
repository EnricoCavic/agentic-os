#!/usr/bin/env python3
"""Render the pre-clone proof GIF: the real credential gate firing.

Depicts the actual output of `bash demo/run.sh` (the runnable credential-scan
gate) so a visitor can watch a machine block a corner-cut BEFORE deciding to
clone. The leaked key is the redacted form the real scanner emits; nothing here
stores a real secret. This is a recording aid mirroring real output, not a
runnable script -- the runnable proof is `bash demo/run.sh` itself.

Needs Pillow (not a framework dependency). Regenerate: python demo/render_demo_gif.py
Output: docs/assets/demo-gate.gif
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BG, BAR_C = (13, 17, 23), (22, 27, 34)
FG, DIM, WHITE = (201, 209, 217), (139, 148, 158), (240, 246, 252)
GREEN, YELLOW, RED = (63, 185, 80), (210, 153, 34), (248, 81, 73)
DOTS = [(247, 95, 86), (245, 191, 79), (98, 197, 84)]

FS, LH, PAD, BAR = 18, 30, 28, 36
W = 820


def _font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except Exception:
            continue
    return ImageFont.load_default()


REG = _font(["C:/Windows/Fonts/consola.ttf", "consola.ttf", "DejaVuSansMono.ttf"], FS)
BOLD = _font(["C:/Windows/Fonts/consolab.ttf", "consolab.ttf", "DejaVuSansMono-Bold.ttf"], FS)

# (segments=[(text,color)...], bold)
LINES = [
    ([("$ ", GREEN), ("bash demo/run.sh", FG)], False),
    ([], False),
    ([("  agent wrote config.env: ", DIM), ('"Done - config added."', WHITE)], False),
    ([("    aws_access_key_id = ", DIM), ("AKIA****************", FG)], False),
    ([], False),
    ([("  $ ", GREEN), ("scan_credentials.py config.env", FG)], False),
    ([("  CREDENTIAL PATTERN(S) DETECTED ", RED), ("(values redacted)", DIM)], False),
    ([("    config.env:2: aws-access-key-id", RED)], False),
    ([], False),
    ([("  Commit BLOCKED. ", RED), ('agent said "done"; the machine said no.', FG)], True),
    ([("  Real scanner, your machine. Reproduce: ", DIM), ("bash demo/run.sh", DIM)], False),
]
H = BAR + PAD + len(LINES) * LH + PAD - 6

# (lines_shown, duration_ms, cursor)
STEPS = [
    (1, 700, True),
    (4, 1100, False),
    (6, 900, True),
    (8, 1500, False),
    (10, 2600, False),
    (11, 2200, False),
]


def render(n, cursor):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, BAR], fill=BAR_C)
    cy = BAR // 2
    for i, c in enumerate(DOTS):
        cx = 22 + i * 19
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=c)
    d.text((W // 2, cy), "agentic-os  -  demo/run.sh", font=REG, fill=DIM, anchor="mm")
    y = BAR + PAD - 4
    for li in range(n):
        segs, bold = LINES[li]
        f = BOLD if bold else REG
        x = PAD
        for text, color in segs:
            d.text((x, y), text, font=f, fill=color)
            x += d.textlength(text, font=f)
        if cursor and li == n - 1:
            d.rectangle([x + 3, y + 2, x + 13, y + FS + 2], fill=FG)
        y += LH
    return img


frames = [render(n, c) for (n, _, c) in STEPS]
durs = [d for (_, d, _) in STEPS]
out = Path(__file__).resolve().parent.parent / "docs" / "assets"
out.mkdir(parents=True, exist_ok=True)
frames[0].save(out / "demo-gate.gif", save_all=True, append_images=frames[1:],
               duration=durs, loop=0, optimize=True, disposal=2)
print(f"wrote {out/'demo-gate.gif'}  ({W}x{H}, {len(frames)} frames)")
