from pathlib import Path
from io import BytesIO
from collections import deque
import textwrap

import cairosvg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'exports' / 'hr-onboarding-v5'
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
CTA_PNG = ROOT / 'assets' / 'ui' / 'book-discovery-call-cta-v5.png'


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


def png_to_image(path, out_w, out_h):
    img = Image.open(path).convert('RGBA')
    return img.resize((out_w, out_h), Image.Resampling.LANCZOS)


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
    # dots
    start_x, y, r, gap = px(884), px(104), px(10), px(4)
    for i in range(4):
        cx = start_x + r + i*(2*r+gap)
        d.ellipse((cx-r, y, cx+r, y+2*r), fill=ORANGE if i == page-1 else DARK)
    if footer == 'center':
        img.alpha_composite(logo, ((W-logo.width)//2, px(982)))
    elif footer == 'left':
        img.alpha_composite(logo, (px(66), px(982)))
    return img, d


def draw_inline_centered_by_ink(draw, center_y, parts, gap=8):
    """Center a mixed-font line and align by visible ink center, not raw y offsets."""
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


def draw_cta_png(base, xy, width=393):
    cta_raw = Image.open(CTA_PNG).convert('RGBA')
    aspect = cta_raw.height / cta_raw.width
    cta = cta_raw.resize((px(width), int(px(width) * aspect)), Image.Resampling.LANCZOS)
    base.alpha_composite(cta, (px(xy[0]), px(xy[1])))


def draw_footer_strip(draw):
    # Match the sample footer: full-width soft peach band, two centered lines, no floating box.
    y = px(974)
    draw.rectangle((0, y, W, H), fill=(249, 238, 234, 255))
    top_f = inter(25)
    url_f = inter(22)
    top = 'Let someone handle the rest.'
    url = 'https://hireai.bot'
    tw, th = text_size(draw, top, top_f)
    uw, uh = text_size(draw, url, url_f)
    draw.text(((W - tw) // 2, y + px(28)), top, font=top_f, fill=BLACK)
    draw.text(((W - uw) // 2, y + px(56)), url, font=url_f, fill=ORANGE)


def draw_blob(img, box, rotate=0):
    x,y,w,h = [px(v) for v in box]
    blob = Image.new('RGBA', (w,h), (0,0,0,0)); bd = ImageDraw.Draw(blob, 'RGBA')
    bd.ellipse((px(20), px(18), w-px(20), h-px(22)), fill=PEACH)
    blob = blob.filter(ImageFilter.GaussianBlur(px(1.2))).rotate(rotate, expand=True, resample=Image.Resampling.BICUBIC)
    img.alpha_composite(blob, (x,y))


def slide1():
    img,d = base(1, footer='left')
    draw_h1(d, (0, 220), '“How many leave days\ndo I have left?”', 72, 8, align='center')

    # Centered support copy. Inter lines are consistent; Caveat is tuned visually to match Inter size.
    support_f = inter(34)
    accent_f = caveat(48)
    line1 = 'Your HR team answered that'
    w1, h1 = text_size(d, line1, support_f)
    d.text(((W-w1)//2, px(416)), line1, font=support_f, fill=BLACK)
    draw_inline_centered_by_ink(d, 474, [('17 times', accent_f, ORANGE), ('this week.', support_f, BLACK)], gap=8)

    draw_blob(img, (568, 610, 275, 195), -6)
    ill = load_illustration('slide-1-phone-chat-volume.png', (875,875))
    # intentional crop/oversize to remove dead lower-left space and make the layout feel centered
    paste_with_shadow(img, ill, ((W-ill.width)//2 + px(38), px(505)))
    return img

def slide2():
    img,d = base(2)
    draw_h1(d, (86, 202), 'And before lunch,\nthey also:', 74, 8)
    draw_blob(img, (455, 452, 485, 390), 5)
    ill = load_illustration('slide-2-overflowing-inbox-sara.png', (690,690))
    paste_with_shadow(img, ill, (px(430), px(390)))

    # Floating task cards, integrated around the overflowing inbox visual.
    cards = [
        (84, 470, 465, 65, '6', 'onboarding checklists'),
        (120, 555, 405, 62, '4', 'unsigned contracts'),
        (80, 642, 388, 62, '3', 'payslip questions'),
        (116, 730, 460, 66, 'Again.', 'reimbursement policy'),
    ]
    for x,y,w,h,num,txt in cards:
        d.rounded_rectangle((px(x), px(y), px(x+w), px(y+h)), radius=px(18), fill=(255,255,255,225), outline=(17,17,17,55), width=px(2))
        nf = caveat(54 if num != 'Again.' else 48)
        tf = inter(25)
        gap = px(12)
        nb = d.textbbox((0, 0), num, font=nf)
        tb = d.textbbox((0, 0), txt, font=tf)
        nw, nh = nb[2]-nb[0], nb[3]-nb[1]
        tw, th = tb[2]-tb[0], tb[3]-tb[1]
        group_w = nw + gap + tw
        start_x = px(x) + (px(w) - group_w)//2 + px(10)
        visual_cy = px(y + h/2 + 5)
        num_y = visual_cy - nh//2 - nb[1] + px(1)
        txt_y = visual_cy - th//2 - tb[1]
        d.text((start_x - nb[0], num_y), num, font=nf, fill=ORANGE)
        d.text((start_x + nw + gap - tb[0], txt_y), txt, font=tf, fill=BLACK)
    return img

def slide3():
    img,d = base(3, footer='left')
    draw_h1(d, (0, 205), "HR's job is", 82, 0, align='center')
    people_f = caveat(110)
    word = 'people.'
    ww, wh = text_size(d, word, people_f)
    x = (W-ww)//2; y = px(268)
    d.text((x,y), word, font=people_f, fill=ORANGE)
    d.rounded_rectangle((x+px(10), y+px(112), x+ww-px(10), y+px(119)), radius=px(8), fill=ORANGE)
    draw_h1(d, (0, 402), 'Not paperwork\nthat repeats itself.', 58, 6, align='center')
    draw_blob(img, (162, 585, 760, 350), -2)
    ill = load_illustration('slide-3-people-vs-paperwork-v2.png', (760,500))
    paste_with_shadow(img, ill, ((W-ill.width)//2, px(590)), 18)
    return img

def slide4():
    img,d = base(4, footer='none')
    draw_h1(d, (72, 200), 'HireAI answers\nthe repeat questions.', 74, 6)
    d.text((px(72), px(386)), 'HR handles what actually matters.', font=caveat(70), fill=ORANGE)
    draw_wrapped(d, (72, 492), 'Leave balances, policy FAQs, onboarding checklists, and document reminders — handled automatically.', inter(30), BLACK, 415, 9)

    # Lowered so it no longer intrudes into the orange "matters" line.
    draw_blob(img, (615, 575, 290, 230), -3)
    ill = load_illustration('slide-4-hr-automation-resolution.png', (620,620))
    paste_with_shadow(img, ill, (px(555), px(520)))

    draw_cta_png(img, (62, 832), width=393)
    draw_footer_strip(d)
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
