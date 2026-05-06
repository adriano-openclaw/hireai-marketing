from pathlib import Path
from io import BytesIO
from collections import deque

import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'exports' / 'dev-about-page-carousel'
GEN_DIR = ROOT / 'assets' / 'generated' / 'dev-about-page'
W = H = 2160
S = 2
ORANGE = (232, 83, 40, 255)
BLACK = (0, 0, 0, 255)
DARK = (63, 65, 66, 255)
GRAY = (124, 124, 124, 255)
BG = (255, 255, 255, 255)
DOT = (226, 229, 235, 132)
PEACH = (247, 198, 181, 142)
SOFT_BAND = (249, 238, 234, 255)

FONT_DIR = ROOT / 'assets' / 'fonts'
FRAUNCES = FONT_DIR / 'Fraunces.ttf'
CAVEAT = FONT_DIR / 'Caveat.ttf'
INTER = FONT_DIR / 'Inter.ttf'
BOX_SVG = ROOT / 'assets' / 'logos' / 'hireai-box-logo.svg'
TEXT_SVG = ROOT / 'assets' / 'logos' / 'hireai-text-logo.svg'
CTA_PNG = ROOT / 'assets' / 'ui' / 'book-discovery-call-cta-v5.png'
UNDERLINE_SVG = ROOT / 'assets' / 'ui' / 'squiggly-underline.svg'


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


def inter_regular(size):
    f = font(INTER, size)
    try: f.set_variation_by_name('Regular')
    except Exception: pass
    return f


def svg_to_image(path, out_w, out_h):
    png = cairosvg.svg2png(url=str(path), output_width=out_w, output_height=out_h)
    return Image.open(BytesIO(png)).convert('RGBA')


def text_size(draw, text, f):
    if not text: return (0, 0)
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def transparent_border_background(img, tolerance=18):
    rgba = img.convert('RGBA')
    pix = rgba.load(); w, h = rgba.size
    seen, q = set(), deque()
    def is_bg(x, y):
        r, g, b, a = pix[x, y]
        return a > 0 and r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance
    for x in range(w):
        for y in (0, h-1):
            if is_bg(x,y): seen.add((x,y)); q.append((x,y))
    for y in range(h):
        for x in (0, w-1):
            if is_bg(x,y) and (x,y) not in seen: seen.add((x,y)); q.append((x,y))
    while q:
        x, y = q.popleft()
        r, g, b, a = pix[x, y]
        pix[x, y] = (r, g, b, 0)
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in seen and is_bg(nx,ny):
                seen.add((nx,ny)); q.append((nx,ny))
    return rgba


def load_illustration(name, max_size):
    img = Image.open(GEN_DIR / name).convert('RGBA')
    img = transparent_border_background(img)
    bbox = img.split()[-1].getbbox()
    if bbox: img = img.crop(bbox)
    img.thumbnail((px(max_size[0]), px(max_size[1])), Image.Resampling.LANCZOS)
    return img


def paste_with_shadow(base, img, xy, shadow_alpha=20):
    shadow = Image.new('RGBA', img.size, (0,0,0,0))
    sp, ip = shadow.load(), img.load()
    for yy in range(img.height):
        for xx in range(img.width):
            if ip[xx,yy][3] > 0:
                sp[xx,yy] = (232,83,40,shadow_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(px(9)))
    base.alpha_composite(shadow, (xy[0]+px(18), xy[1]+px(28)))
    base.alpha_composite(img, xy)


def base(page, footer='center'):
    img = Image.new('RGBA', (W,H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    spacing, radius = px(27), px(2.5)
    for y in range(px(14), H+spacing, spacing):
        for x in range(px(14), W+spacing, spacing):
            d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=DOT)
    box = svg_to_image(BOX_SVG, px(100), px(100))
    logo = svg_to_image(TEXT_SVG, px(123), px(27))
    img.alpha_composite(box, (px(66), px(57)))
    start_x, y, r, gap = px(884), px(104), px(10), px(4)
    for i in range(4):
        cx = start_x + r + i*(2*r+gap)
        d.ellipse((cx-r, y, cx+r, y+2*r), fill=ORANGE if i == page-1 else DARK)
    if footer == 'center':
        img.alpha_composite(logo, ((W-logo.width)//2, px(982)))
    elif footer == 'left':
        img.alpha_composite(logo, (px(66), px(982)))
    return img, d


def draw_h1(draw, xy, text, size=76, line_gap=8, fill=BLACK, align='left'):
    f = fraunces(size)
    x, y = px(xy[0]), px(xy[1])
    for line in text.split('\n'):
        w, h = text_size(draw, line, f)
        xx = x if align == 'left' else (W - w) // 2
        draw.text((xx, y), line, font=f, fill=fill)
        y += h + px(line_gap)
    return y


def draw_wrapped(draw, xy, text, f, fill, max_width, line_gap=8):
    x, y = px(xy[0]), px(xy[1])
    words = text.split()
    lines, cur = [], ''
    for word in words:
        test = word if not cur else cur + ' ' + word
        if text_size(draw, test, f)[0] <= px(max_width):
            cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += text_size(draw, line, f)[1] + px(line_gap)
    return y


def draw_inline_centered(draw, center_y, parts, gap=8):
    metrics = []
    total = 0
    for text, f, fill in parts:
        bbox = draw.textbbox((0, 0), text, font=f)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        metrics.append((text, f, fill, bbox, w, h))
        total += w
    total += px(gap) * (len(parts) - 1)
    x = (W - total) // 2
    cy = px(center_y)
    for text, f, fill, bbox, w, h in metrics:
        y = cy - h // 2 - bbox[1]
        draw.text((x - bbox[0], y), text, font=f, fill=fill)
        x += w + px(gap)


def draw_blob(img, box, rotate=0):
    x,y,w,h = [px(v) for v in box]
    blob = Image.new('RGBA', (w,h), (0,0,0,0)); bd = ImageDraw.Draw(blob, 'RGBA')
    bd.ellipse((px(20), px(18), w-px(20), h-px(22)), fill=PEACH)
    blob = blob.filter(ImageFilter.GaussianBlur(px(1.2))).rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
    img.alpha_composite(blob, (x,y))


def draw_cta_png(base, xy, width=393):
    cta_raw = Image.open(CTA_PNG).convert('RGBA')
    aspect = cta_raw.height / cta_raw.width
    cta = cta_raw.resize((px(width), int(px(width) * aspect)), Image.Resampling.LANCZOS)
    base.alpha_composite(cta, (px(xy[0]), px(xy[1])))


def draw_footer_strip(draw):
    y = px(966)
    draw.rectangle((0, y, W, H), fill=SOFT_BAND)
    top_f = inter(25)
    url_f = inter(22)
    top = 'Let someone handle the rest.'
    url = 'https://hireai.bot'
    tw, _ = text_size(draw, top, top_f)
    uw, _ = text_size(draw, url, url_f)
    draw.text(((W - tw) // 2, y + px(28)), top, font=top_f, fill=BLACK)
    draw.text(((W - uw) // 2, y + px(54)), url, font=url_f, fill=ORANGE)


def draw_squiggly_underline(base_img, x, y, width, height=27, rotate=0):
    underline = svg_to_image(UNDERLINE_SVG, px(width), px(height))
    if rotate:
        underline = underline.rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
    base_img.alpha_composite(underline, (px(x), px(y)))


def highlight_underline(base_img, draw, x, y, text, f, underline_y_offset=72, underline_width_pad=24):
    draw.text((px(x), px(y)), text, font=f, fill=ORANGE)
    w, _ = text_size(draw, text, f)
    underline_w = max(120, int(w / S) + underline_width_pad)
    draw_squiggly_underline(base_img, x - underline_width_pad / 2, y + underline_y_offset, underline_w, 27, rotate=-1)


def highlight_crossout(draw, x, y, text, f):
    draw.text((px(x), px(y)), text, font=f, fill=ORANGE)
    w, h = text_size(draw, text, f)
    # Cross/strikethrough treatment is intentionally distinct from the squiggly underline rule.
    left = px(x + 2)
    right = px(x) + w - px(4)
    y1 = px(y + 51)
    y2 = px(y + 68)
    draw.line((left, y1, right, y2), fill=ORANGE, width=px(5))
    draw.line((left + px(6), y2 + px(8), right - px(6), y1 - px(3)), fill=ORANGE, width=px(4))


def draw_centered_wrapped(draw, y, lines, f, fill=BLACK, line_gap=9):
    yy = px(y)
    for line in lines:
        w, h = text_size(draw, line, f)
        draw.text(((W-w)//2, yy), line, font=f, fill=fill)
        yy += h + px(line_gap)
    return yy


def wrap_lines(draw, text, f, max_width):
    words = text.split()
    lines, cur = [], ''
    for word in words:
        test = word if not cur else cur + ' ' + word
        if text_size(draw, test, f)[0] <= px(max_width):
            cur = test
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines


def draw_centered_wrapped_text(draw, center_x, y, text, f, fill, max_width, line_gap=9):
    yy = px(y)
    for line in wrap_lines(draw, text, f, max_width):
        w, h = text_size(draw, line, f)
        draw.text((px(center_x) - w//2, yy), line, font=f, fill=fill)
        yy += h + px(line_gap)
    return yy


def slide1():
    img, d = base(1, footer='left')
    draw_h1(d, (0, 175), 'Your landing page\nneeds an', 74, 8, align='center')
    accent = caveat(96)
    about = 'About page.'
    ww, _ = text_size(d, about, accent)
    d.text((px((1080 - ww/S) / 2), px(325)), about, font=accent, fill=ORANGE)
    draw_centered_wrapped(d, 444, ['But matching the existing design, copy,', 'and feel turns into another dev task.'], inter(29), BLACK, 9)
    draw_blob(img, (360, 605, 360, 250), -5)
    ill = load_illustration('slide-1-problem-clean.png', (780, 610))
    paste_with_shadow(img, ill, ((W-ill.width)//2 + px(20), px(535)))
    return img


def slide2():
    img, d = base(2, footer='left')
    draw_h1(d, (84, 175), 'One prompt:', 80, 6)
    prompt_f = inter(28)

    # Send-message UI component: tighter parent padding, cleaner input and send button.
    shell = (78, 308, 925, 138)
    d.rounded_rectangle(tuple(px(v) for v in (shell[0], shell[1], shell[0]+shell[2], shell[1]+shell[3])), radius=px(30), fill=(255,255,255,244), outline=(17,17,17,45), width=px(2))
    d.rounded_rectangle((px(105), px(332), px(892), px(422)), radius=px(23), fill=(248,248,246,255), outline=(17,17,17,28), width=px(2))
    draw_wrapped(d, (132, 359), 'Add an About page to this landing page.', prompt_f, BLACK, 705, 8)
    cx, cy, rr = px(942), px(377), px(34)
    d.ellipse((cx-rr, cy-rr, cx+rr, cy+rr), fill=ORANGE)
    # Paper-plane send icon: white outline with stable proportions.
    plane = [(cx-px(14), cy-px(3)), (cx+px(16), cy-px(18)), (cx+px(5), cy+px(17)), (cx-px(2), cy+px(3))]
    d.polygon(plane, fill=(255,255,255,255))
    d.polygon([(cx-px(2), cy+px(3)), (cx+px(16), cy-px(18)), (cx+px(3), cy+px(6))], fill=(246,246,242,255))

    d.text((px(118), px(470)), 'That’s enough context.', font=caveat(58), fill=ORANGE)
    draw_blob(img, (575, 605, 300, 225), 4)
    ill = load_illustration('slide-2-one-prompt.png', (615, 500))
    paste_with_shadow(img, ill, ((W-ill.width)//2 + px(145), px(560)))
    return img


def slide3():
    img, d = base(3, footer='left')
    # All-centered layout, matching Slide 1's hierarchy and rhythm.
    draw_h1(d, (0, 175), 'HireAI reads\nyour existing', 72, 6, align='center')
    style_f = caveat(82)
    style = 'style system'
    sw, _ = text_size(d, style, style_f)
    sx = (1080 - sw / S) / 2
    d.text((px(sx), px(318)), style, font=style_f, fill=ORANGE)
    draw_squiggly_underline(img, sx - 10, 400, (sw / S) + 20, 27, rotate=-1)
    draw_centered_wrapped(d, 462, ['Colors, sections, spacing, components, tone.', 'Then it builds the new page like', 'it belonged there from day one.'], inter(27), BLACK, 9)
    draw_blob(img, (350, 625, 380, 260), -2)
    ill = load_illustration('slide-3-matching-style.png', (680, 540))
    paste_with_shadow(img, ill, ((W-ill.width)//2 + px(10), px(585)))
    return img


def slide4():
    img, d = base(4, footer='none')
    draw_h1(d, (74, 165), 'New page.\nSame brand.', 78, 8)
    d.text((px(76), px(345)), 'Automatically updated.', font=caveat(72), fill=ORANGE)
    draw_wrapped(d, (76, 455), 'Your landing page gets the About section without starting from scratch or breaking the design.', inter(29), BLACK, 475, 9)
    draw_blob(img, (595, 490, 320, 245), 2)
    ill = load_illustration('slide-4-result.png', (610, 610))
    paste_with_shadow(img, ill, (px(535), px(470)))
    draw_cta_png(img, (62, 730), width=393)
    draw_footer_strip(d)
    return img


SLIDES = [slide1, slide2, slide3, slide4]
OUT_DIR.mkdir(parents=True, exist_ok=True)
for idx, fn in enumerate(SLIDES, 1):
    img = fn()
    hq = OUT_DIR / f'hireai-dev-about-slide-{idx}-2160.png'
    pv = OUT_DIR / f'hireai-dev-about-slide-{idx}-1080.png'
    img.convert('RGB').save(hq, quality=100)
    img.resize((1080,1080), Image.Resampling.LANCZOS).convert('RGB').save(pv, quality=100)
    print(hq)
    print(pv)
