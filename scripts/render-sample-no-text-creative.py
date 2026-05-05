from pathlib import Path
from io import BytesIO
from collections import deque

import cairosvg
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
W = H = 2160
S = W / 1080
ORANGE = (232, 83, 40, 255)
DARK = (63, 65, 66, 255)
BG = (255, 255, 255, 255)
DOT = (226, 229, 235, 132)
PEACH = (247, 198, 181, 174)

OUT = ROOT / "exports" / "hireai-sample-no-text-creative-2160.png"
PREVIEW = ROOT / "exports" / "hireai-sample-no-text-creative-1080.png"
ILLUSTRATION = ROOT / "assets" / "generated" / "hireai-sample-ai-recruiting-illustration.png"
BOX_SVG = ROOT / "assets" / "logos" / "hireai-box-logo.svg"
TEXT_SVG = ROOT / "assets" / "logos" / "hireai-text-logo.svg"


def px(v: float) -> int:
    return int(round(v * S))


def svg_to_image(path: Path, out_w: int, out_h: int) -> Image.Image:
    png = cairosvg.svg2png(url=str(path), output_width=out_w, output_height=out_h)
    return Image.open(BytesIO(png)).convert("RGBA")


def transparent_border_background(img: Image.Image, tolerance: int = 22) -> Image.Image:
    """Make only the connected near-white border background transparent, preserving enclosed white fills."""
    rgba = img.convert("RGBA")
    pix = rgba.load()
    w, h = rgba.size
    seen = set()
    q = deque()

    def is_bg(x, y):
        r, g, b, a = pix[x, y]
        return a > 0 and r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance

    for x in range(w):
        for y in (0, h - 1):
            if is_bg(x, y):
                q.append((x, y))
                seen.add((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(x, y) and (x, y) not in seen:
                q.append((x, y))
                seen.add((x, y))

    while q:
        x, y = q.popleft()
        r, g, b, a = pix[x, y]
        pix[x, y] = (r, g, b, 0)
        for nx, ny in ((x+1,y), (x-1,y), (x,y+1), (x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and is_bg(nx, ny):
                seen.add((nx, ny))
                q.append((nx, ny))
    return rgba


def alpha_bbox(img: Image.Image):
    return img.split()[-1].getbbox()


img = Image.new("RGBA", (W, H), BG)
d = ImageDraw.Draw(img, "RGBA")

# Approved cool-gray circular dot pattern, scaled from the 1080 template.
spacing = px(27)
radius = px(2.5)
for y in range(px(14), H + spacing, spacing):
    for x in range(px(14), W + spacing, spacing):
        d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=DOT)

# Pale orange organic support blob behind the generated illustration.
blob = Image.new("RGBA", (px(760), px(590)), (0, 0, 0, 0))
bd = ImageDraw.Draw(blob, "RGBA")
bd.ellipse((px(28), px(24), px(732), px(562)), fill=PEACH)
blob = blob.filter(ImageFilter.GaussianBlur(px(1.2))).rotate(-8, expand=True, resample=Image.Resampling.BICUBIC)
img.alpha_composite(blob, (px(165), px(282)))

# Generated HireAI-style illustration, trimmed to sit naturally on the branded background.
ill = Image.open(ILLUSTRATION).convert("RGBA")
ill = transparent_border_background(ill)
bbox = alpha_bbox(ill)
if bbox:
    ill = ill.crop(bbox)
ill.thumbnail((px(790), px(790)), Image.Resampling.LANCZOS)
shadow = Image.new("RGBA", ill.size, (0, 0, 0, 0))
sp = shadow.load(); ip = ill.load()
for yy in range(ill.height):
    for xx in range(ill.width):
        if ip[xx, yy][3] > 0:
            sp[xx, yy] = (232, 83, 40, 25)
shadow = shadow.filter(ImageFilter.GaussianBlur(px(8)))
ix = (W - ill.width) // 2 + px(14)
iy = px(236)
img.alpha_composite(shadow, (ix + px(18), iy + px(30)))
img.alpha_composite(ill, (ix, iy))

# Exact SVG logo assets.
box = svg_to_image(BOX_SVG, px(100), px(100))
text = svg_to_image(TEXT_SVG, px(123), px(27))
img.alpha_composite(box, (px(66), px(57)))

# Four-dot pagination, page 1 active.
start_x, y, r, gap = px(884), px(104), px(10), px(4)
for i in range(4):
    cx = start_x + r + i * (2 * r + gap)
    color = ORANGE if i == 0 else DARK
    d.ellipse((cx-r, y, cx+r, y+2*r), fill=color)

# Bottom-left wordmark to echo the provided sample creative layouts.
img.alpha_composite(text, (px(66), px(982)))

OUT.parent.mkdir(parents=True, exist_ok=True)
img.convert("RGB").save(OUT, quality=100)
img.resize((1080, 1080), Image.Resampling.LANCZOS).convert("RGB").save(PREVIEW, quality=100)
print(OUT)
print(PREVIEW)
