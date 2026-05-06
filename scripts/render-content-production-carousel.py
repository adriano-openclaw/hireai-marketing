from pathlib import Path
from io import BytesIO
from collections import deque

import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'exports' / 'content-production-option-b'
GEN_DIR = ROOT / 'assets' / 'generated' / 'content-production-option-b'
W = H = 2160
S = 2
ORANGE = (232, 83, 40, 255)
BLACK = (0, 0, 0, 255)
DARK = (63, 65, 66, 255)
GRAY = (124, 124, 124, 255)
BG = (255, 255, 255, 255)
DOT = (226, 229, 235, 132)
PEACH = (249, 238, 234, 255)
PEACH_DEEP = (247, 198, 181, 142)

FONT_DIR = ROOT / 'assets' / 'fonts'
FRAUNCES = FONT_DIR / 'Fraunces.ttf'
CAVEAT = FONT_DIR / 'Caveat.ttf'
INTER = FONT_DIR / 'Inter.ttf'
BOX_SVG = ROOT / 'assets' / 'logos' / 'hireai-box-logo.svg'
TEXT_SVG = ROOT / 'assets' / 'logos' / 'hireai-text-logo.svg'
CTA_PNG = ROOT / 'assets' / 'ui' / 'book-discovery-call-cta-v5.png'


def px(v): return int(round(v * S))


def font(path, size):
    f = ImageFont.truetype(str(path), px(size))
    return f


def fraunces(size):
    f = font(FRAUNCES, size)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f


def caveat(size):
    f = font(CAVEAT, size)
    try: f.set_variation_by_name('Bold')
    except Exception: pass
    return f


def inter(size):
    f = font(INTER, size)
    try: f.set_variation_by_name('SemiBold')
    except Exception: pass
    return f


def svg_to_image(path, out_w, out_h):
    png = cairosvg.svg2png(url=str(path), output_width=out_w, output_height=out_h)
    return Image.open(BytesIO(png)).convert('RGBA')


def text_size(draw, text, f):
    if text == '': return (0, 0)
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def transparent_border_background(img, tolerance=20):
    rgba = img.convert('RGBA')
    pix = rgba.load(); w, h = rgba.size
    seen, q = set(), deque()
    def is_bg(x, y):
        r, g, b, a = pix[x, y]
        return a > 0 and r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance
    for x in range(w):
        for y in (0, h-1):
            if is_bg(x, y): seen.add((x, y)); q.append((x, y))
    for y in range(h):
        for x in (0, w-1):
            if is_bg(x, y) and (x, y) not in seen: seen.add((x, y)); q.append((x, y))
    while q:
        x, y = q.popleft()
        r, g, b, a = pix[x, y]
        pix[x, y] = (r, g, b, 0)
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in seen and is_bg(nx, ny):
                seen.add((nx,ny)); q.append((nx,ny))
    return rgba


def load_art(name, max_size):
    img = Image.open(GEN_DIR / name).convert('RGBA')
    img = transparent_border_background(img)
    bbox = img.split()[-1].getbbox()
    if bbox: img = img.crop(bbox)
    img.thumbnail((px(max_size[0]), px(max_size[1])), Image.Resampling.LANCZOS)
    return img


def paste_with_shadow(base, img, xy, alpha=20):
    shadow = Image.new('RGBA', img.size, (0,0,0,0))
    sp, ip = shadow.load(), img.load()
    for yy in range(img.height):
        for xx in range(img.width):
            if ip[xx, yy][3] > 0:
                sp[xx, yy] = (232, 83, 40, alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(px(9)))
    base.alpha_composite(shadow, (xy[0]+px(16), xy[1]+px(28)))
    base.alpha_composite(img, xy)


def base(page, footer='left'):
    img = Image.new('RGBA', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    spacing, radius = px(27), px(2.5)
    for y in range(px(14), H + spacing, spacing):
        for x in range(px(14), W + spacing, spacing):
            d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=DOT)
    box = svg_to_image(BOX_SVG, px(100), px(100))
    logo = svg_to_image(TEXT_SVG, px(123), px(27))
    img.alpha_composite(box, (px(66), px(57)))
    start_x, y, r, gap = px(884), px(104), px(10), px(4)
    for i in range(4):
        cx = start_x + r + i * (2*r + gap)
        d.ellipse((cx-r, y, cx+r, y+2*r), fill=ORANGE if i == page-1 else DARK)
    if footer == 'left':
        img.alpha_composite(logo, (px(66), px(982)))
    return img, d


def draw_footer_strip(draw):
    y = px(958)
    draw.rectangle((0, y, W, H), fill=PEACH)
    top_f = inter(25)
    url_f = inter(22)
    top = 'Let someone handle the rest.'
    url = 'https://hireai.bot'
    top_w, top_h = text_size(draw, top, top_f)
    url_w, url_h = text_size(draw, url, url_f)
    gap = px(5)
    group_h = top_h + gap + url_h
    yy = y + (H - y - group_h)//2 - px(5)
    draw.text(((W - top_w)//2, yy), top, font=top_f, fill=BLACK)
    draw.text(((W - url_w)//2, yy + top_h + gap), url, font=url_f, fill=ORANGE)


def draw_h1(draw, xy, text, size=74, line_gap=8, fill=BLACK, align='left'):
    f = fraunces(size)
    x, y = px(xy[0]), px(xy[1])
    for line in text.split('\n'):
        w, h = text_size(draw, line, f)
        xx = x if align == 'left' else (W - w)//2
        draw.text((xx, y), line, font=f, fill=fill)
        y += h + px(line_gap)
    return y


def draw_wrapped(draw, xy, text, f, fill, max_width, line_gap=8):
    x, y = px(xy[0]), px(xy[1])
    words = text.split()
    lines, cur = [], ''
    for word in words:
        test = word if not cur else cur + ' ' + word
        if text_size(draw, test, f)[0] <= px(max_width): cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += text_size(draw, line, f)[1] + px(line_gap)
    return y


def draw_centered_mixed(draw, center_y, parts, gap=8):
    metrics=[]; total=0
    for text, f, fill in parts:
        b=draw.textbbox((0,0), text, font=f); w=b[2]-b[0]; h=b[3]-b[1]
        metrics.append((text,f,fill,b,w,h)); total += w
    total += px(gap)*(len(parts)-1)
    x=(W-total)//2; cy=px(center_y)
    for text,f,fill,b,w,h in metrics:
        y=cy-h//2-b[1]
        draw.text((x-b[0], y), text, font=f, fill=fill)
        x += w + px(gap)


def slide1():
    img, d = base(1, footer='left')
    # Give the headline stack more breathing room while keeping the approved bold scale.
    draw_h1(d, (0, 162), 'Brief. Draft.\nRevise.', 78, 22, align='center')
    rep_f = caveat(88)
    rep = 'Repeat.'; rw, rh = text_size(d, rep, rep_f)
    d.text(((W-rw)//2, px(318)), rep, font=rep_f, fill=ORANGE)
    support = 'Your content team is stuck in a loop.'
    sf = inter(33); sw, _ = text_size(d, support, sf)
    d.text(((W-sw)//2, px(436)), support, font=sf, fill=BLACK)
    # Move the loop graphic up with the middle text stack, while preserving a clean gap under the support line.
    art = load_art('slide-1-loop-graphic.png', (855, 495))
    paste_with_shadow(img, art, ((W-art.width)//2, px(500)), 18)
    return img


def slide2():
    img, d = base(2, footer='left')
    draw_h1(d, (86, 186), 'Every piece of\ncontent costs you:', 72, 8)
    # Denser text stack creates room to restore illustration scale without collision.
    art = load_art('slide-2-time-blocks.png', (470, 520))
    paste_with_shadow(img, art, (px(590), px(625)), 14)
    rows = [
        (400, '1 hour', 'writing the brief', 56, 31),
        (465, '2 hours', 'on the first draft', 56, 31),
        (530, '45 mins', 'of revisions', 56, 31),
        (595, 'Another round', 'because “the tone is off”', 56, 31),
    ]
    lead_x = 78
    for cy, lead, rest, lead_size, rest_size in rows:
        lead_f = caveat(lead_size)
        rest_f = inter(rest_size)
        lb = d.textbbox((0, 0), lead, font=lead_f)
        rb = d.textbbox((0, 0), rest, font=rest_f)
        lh = lb[3] - lb[1]
        rh = rb[3] - rb[1]
        center = px(cy)
        # Visual alignment by eye: Inter sits just a hair lower so it reads as attached to Caveat,
        # not as a separate floating column.
        lead_y = center - lh//2 - lb[1] + px(1)
        rest_y = center - rh//2 - rb[1] + px(4)
        # Attach Inter directly after the visible script ink; the final row gets a tighter join to
        # reduce its long horizontal footprint without making it look squeezed.
        local_gap = 7 if lead == 'Another round' else 8
        local_rest_x = lead_x + ((lb[2] - lb[0]) / S) + local_gap
        d.text((px(lead_x)-lb[0], lead_y), lead, font=lead_f, fill=ORANGE)
        d.text((px(local_rest_x)-rb[0], rest_y), rest, font=rest_f, fill=BLACK)
    return img


def slide3():
    img, d = base(3, footer='left')
    draw_h1(d, (0, 190), "The bottleneck\nisn't your team.", 82, 6, align='center')
    proc_f = caveat(88)
    proc = "It's the process."
    pw, _ = text_size(d, proc, proc_f)
    # Move the Caveat line closer to the Fraunces headline and open more space before the art.
    d.text(((W-pw)//2, px(366)), proc, font=proc_f, fill=ORANGE)
    art = load_art('slide-3-funnel-bottleneck.png', (910, 575))
    paste_with_shadow(img, art, ((W-art.width)//2, px(500)), 16)
    return img


def slide4():
    img, d = base(4, footer='none')
    draw_h1(d, (72, 190), 'HireAI drafts\non brief.', 75, 6)
    d.text((px(72), px(360)), 'Every time. First time.', font=caveat(72), fill=ORANGE)
    draw_wrapped(d, (72, 474), 'Blog posts, captions, scripts, and reports, drafted to your tone, ready to review.', inter(27), BLACK, 420, 8)
    # Use the full generated review illustration here; the previous reference crop rendered too tiny
    # and floated awkwardly beside the copy.
    art = load_art('slide-4-johnny-document.png', (560, 410))
    paste_with_shadow(img, art, (px(500), px(430)), 12)
    cta = Image.open(CTA_PNG).convert('RGBA')
    aspect = cta.height / cta.width
    cta_w = 370
    cta = cta.resize((px(cta_w), int(px(cta_w)*aspect)), Image.Resampling.LANCZOS)
    # Keep CTA visually grouped with the Inter body copy instead of floating near the footer.
    img.alpha_composite(cta, (px(62), px(740)))
    draw_footer_strip(d)
    return img


SLIDES = [slide1, slide2, slide3, slide4]
OUT_DIR.mkdir(parents=True, exist_ok=True)
for idx, fn in enumerate(SLIDES, 1):
    img = fn()
    hq = OUT_DIR / f'option-b-content-production-slide-{idx}-2160.png'
    pv = OUT_DIR / f'option-b-content-production-slide-{idx}-1080.png'
    img.convert('RGB').save(hq, quality=100)
    img.resize((1080,1080), Image.Resampling.LANCZOS).convert('RGB').save(pv, quality=100)
    print(hq)
    print(pv)
