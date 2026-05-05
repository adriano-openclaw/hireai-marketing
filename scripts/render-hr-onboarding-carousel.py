from pathlib import Path
from io import BytesIO
from collections import deque
import textwrap

import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'exports' / 'hr-onboarding'
GEN_DIR = ROOT / 'assets' / 'generated' / 'hr-onboarding'
W = H = 2160
S = 2
ORANGE = (232, 83, 40, 255)
BLACK = (0, 0, 0, 255)
DARK = (63, 65, 66, 255)
GRAY = (124, 124, 124, 255)
BG = (255, 255, 255, 255)
DOT = (226, 229, 235, 132)
PEACH = (247, 198, 181, 142)

FONT_DIR = ROOT / 'assets' / 'fonts'
FRAUNCES = FONT_DIR / 'Fraunces.ttf'
CAVEAT = FONT_DIR / 'Caveat.ttf'
INTER = FONT_DIR / 'Inter.ttf'
BOX_SVG = ROOT / 'assets' / 'logos' / 'hireai-box-logo.svg'
TEXT_SVG = ROOT / 'assets' / 'logos' / 'hireai-text-logo.svg'


def px(v): return int(round(v * S))

def font(path, size, axes=None):
    f = ImageFont.truetype(str(path), px(size))
    if axes and hasattr(f, 'set_variation_by_axes'):
        try:
            f.set_variation_by_axes(axes)
        except Exception:
            pass
    return f

# Axes are best-effort for variable fonts. Fallback is still the correct family.
def fraunces(size): return font(FRAUNCES, size, [0, 0, 72, 800])
def caveat(size): return font(CAVEAT, size, [700])
def inter(size): return font(INTER, size, [14, 700])
def inter_regular(size): return font(INTER, size, [14, 400])


def svg_to_image(path, out_w, out_h):
    png = cairosvg.svg2png(url=str(path), output_width=out_w, output_height=out_h)
    return Image.open(BytesIO(png)).convert('RGBA')


def text_size(draw, text, f):
    if text == '': return (0, 0)
    b = draw.textbbox((0, 0), text, font=f)
    return b[2] - b[0], b[3] - b[1]


def draw_centered(draw, y, parts, gap=10):
    widths = [text_size(draw, t, f)[0] for t, f, c in parts]
    total = sum(widths) + px(gap) * (len(parts) - 1)
    x = (W - total) // 2
    for (t, f, c), w in zip(parts, widths):
        draw.text((x, px(y)), t, font=f, fill=c)
        x += w + px(gap)


def draw_h1(draw, xy, text, size=78, line_gap=10, fill=BLACK, align='left'):
    f = fraunces(size)
    x, y = px(xy[0]), px(xy[1])
    lines = text.split('\n')
    for line in lines:
        w, h = text_size(draw, line, f)
        xx = x if align == 'left' else (W - w) // 2
        draw.text((xx, y), line, font=f, fill=fill)
        y += h + px(line_gap)
    return y


def draw_body(draw, xy, text, size=28, fill=BLACK, line_gap=8):
    f = inter(size)
    x, y = px(xy[0]), px(xy[1])
    for line in text.split('\n'):
        draw.text((x, y), line, font=f, fill=fill)
        y += text_size(draw, line, f)[1] + px(line_gap)
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


def transparent_border_background(img, tolerance=24):
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


def paste_with_shadow(base, img, xy, shadow_alpha=22):
    shadow = Image.new('RGBA', img.size, (0,0,0,0))
    sp, ip = shadow.load(), img.load()
    for yy in range(img.height):
        for xx in range(img.width):
            if ip[xx,yy][3] > 0:
                sp[xx,yy] = (232,83,40,shadow_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(px(9)))
    base.alpha_composite(shadow, (xy[0]+px(18), xy[1]+px(30)))
    base.alpha_composite(img, xy)


def base(page):
    img = Image.new('RGBA', (W,H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    spacing, radius = px(27), px(2.5)
    for y in range(px(14), H+spacing, spacing):
        for x in range(px(14), W+spacing, spacing):
            d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=DOT)
    box = svg_to_image(BOX_SVG, px(100), px(100))
    logo = svg_to_image(TEXT_SVG, px(123), px(27))
    img.alpha_composite(box, (px(66), px(57)))
    # dots
    start_x, y, r, gap = px(884), px(104), px(10), px(4)
    for i in range(4):
        cx = start_x + r + i*(2*r+gap)
        d.ellipse((cx-r, y, cx+r, y+2*r), fill=ORANGE if i == page-1 else DARK)
    img.alpha_composite(logo, ((W-logo.width)//2, px(982)))
    return img, d


def draw_blob(img, box, rotate=0):
    x,y,w,h = [px(v) for v in box]
    blob = Image.new('RGBA', (w,h), (0,0,0,0)); bd = ImageDraw.Draw(blob, 'RGBA')
    bd.ellipse((px(20), px(18), w-px(20), h-px(22)), fill=PEACH)
    blob = blob.filter(ImageFilter.GaussianBlur(px(1.2))).rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
    img.alpha_composite(blob, (x,y))


def slide1():
    img,d = base(1)
    draw_h1(d, (96, 190), '“How many leave days\ndo I have left?”', 72, 8)
    y = draw_body(d, (96, 390), 'Your HR team answered that', 30)
    d.text((px(96), y+px(4)), '17 times', font=caveat(82), fill=ORANGE)
    w17 = text_size(d, '17 times', caveat(82))[0]
    d.text((px(96)+w17+px(8), y+px(25)), 'this week.', font=inter(30), fill=BLACK)
    draw_blob(img, (330, 500, 690, 450), -6)
    ill = load_illustration('slide-1-phone-chat-volume.png', (690,690))
    paste_with_shadow(img, ill, (px(365), px(445)))
    return img


def slide2():
    img,d = base(2)
    draw_h1(d, (86, 184), 'And before\nlunch, they also:', 69, 8)
    items = [('6', 'onboarding checklists'), ('4', 'unsigned contracts'), ('3', 'payslip questions'), ('Again.', 'reimbursement policy')]
    y = px(430)
    for num, txt in items:
        d.rounded_rectangle((px(86), y, px(500), y+px(64)), radius=px(18), fill=(255,255,255,230), outline=(17,17,17,80), width=px(2))
        d.text((px(112), y+px(4)), num, font=caveat(48), fill=ORANGE)
        nx = px(112) + text_size(d, num, caveat(48))[0] + px(11)
        d.text((nx, y+px(20)), txt, font=inter(21), fill=BLACK)
        y += px(74)
    draw_blob(img, (515, 430, 560, 470), 7)
    ill = load_illustration('slide-2-overflowing-inbox-sara.png', (600,600))
    paste_with_shadow(img, ill, (px(520), px(438)))
    return img


def slide3():
    img,d = base(3)
    draw_h1(d, (0, 176), "HR's job is", 76, 0, align='center')
    people_f = caveat(102)
    word = 'people.'
    ww, wh = text_size(d, word, people_f)
    x = (W-ww)//2; y = px(262)
    d.text((x,y), word, font=people_f, fill=ORANGE)
    # underline, intentionally below the word (not strikethrough)
    d.rounded_rectangle((x+px(8), y+px(100), x+ww-px(8), y+px(110)), radius=px(8), fill=ORANGE)
    draw_h1(d, (0, 384), 'Not paperwork\nthat repeats itself.', 54, 6, align='center')

    panel_y, panel_h = px(610), px(286)
    left = (px(80), panel_y, px(520), panel_y+panel_h)
    right = (px(560), panel_y, px(1000), panel_y+panel_h)
    d.rounded_rectangle(left, radius=px(24), fill=(255,255,255,242), outline=(232,83,40,170), width=px(4))
    d.rounded_rectangle(right, radius=px(24), fill=(255,255,255,242), outline=(17,17,17,120), width=px(3))
    d.text((px(116), panel_y+px(32)), 'What HR\nShould Do', font=fraunces(32), fill=BLACK, spacing=px(4))
    d.text((px(596), panel_y+px(32)), 'What They\nActually Do', font=fraunces(32), fill=BLACK, spacing=px(4))

    # simple illustration/icon marks inside the panels, keeping text readable
    for cx, cy, col in [(162, 768, ORANGE), (202, 794, BLACK), (242, 768, ORANGE)]:
        d.ellipse((px(cx-15), px(cy-15), px(cx+15), px(cy+15)), fill=col)
    d.arc((px(128), px(804), px(276), px(874)), 195, 345, fill=BLACK, width=px(5))
    for i,t in enumerate(['coaching','culture','hiring strategy']):
        d.text((px(305), panel_y+px(146+i*39)), t, font=inter_regular(22), fill=GRAY)

    for i in range(3):
        y0 = panel_y + px(140+i*42)
        d.rounded_rectangle((px(602), y0, px(680), y0+px(26)), radius=px(6), outline=BLACK, width=px(3), fill=(255,255,255,255))
        d.line((px(616), y0+px(13), px(666), y0+px(13)), fill=ORANGE, width=px(3))
    for i,t in enumerate(['repeat FAQs','forms','policy reminders']):
        d.text((px(710), panel_y+px(145+i*39)), t, font=inter_regular(22), fill=GRAY)
    return img

def slide4():
    img,d = base(4)
    draw_h1(d, (86, 180), 'HireAI answers\nthe repeat questions.', 62, 6)
    d.text((px(86), px(332)), 'HR handles what actually matters.', font=caveat(66), fill=ORANGE)
    draw_wrapped(d, (86, 421), 'Leave balances, policy FAQs, onboarding checklists, and document reminders — handled automatically.', inter(23), BLACK, 355, 7)
    draw_blob(img, (455, 450, 610, 450), -3)
    ill = load_illustration('slide-4-hr-automation-resolution.png', (620,620))
    paste_with_shadow(img, ill, (px(505), px(455)))
    d.text((px(796), px(1000)), 'hireai.bot', font=inter_regular(22), fill=GRAY)
    return img

SLIDES = [slide1, slide2, slide3, slide4]
OUT_DIR.mkdir(parents=True, exist_ok=True)
for idx, fn in enumerate(SLIDES, 1):
    img = fn()
    hq = OUT_DIR / f'option-c-hr-onboarding-slide-{idx}-2160.png'
    pv = OUT_DIR / f'option-c-hr-onboarding-slide-{idx}-1080.png'
    img.convert('RGB').save(hq, quality=100)
    img.resize((1080,1080), Image.Resampling.LANCZOS).convert('RGB').save(pv, quality=100)
    print(hq)
    print(pv)
