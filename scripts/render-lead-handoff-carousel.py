from pathlib import Path
from collections import deque
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'exports' / 'lead-handoff-dryrun'
GEN_DIR = ROOT / 'assets' / 'generated' / 'lead-handoff-dryrun'
SAMPLE = ROOT / 'samples' / 'creatives' / 'hr-onboarding-carousel-v5' / '1080' / 'option-c-hr-onboarding-slide-1-1080.png'
W = H = 1080
ORANGE = (232, 83, 40, 255)
BLACK = (0, 0, 0, 255)
DARK = (63, 65, 66, 255)
DOT = (226, 229, 235, 132)
BG = (255, 255, 255, 255)
PEACH = (249, 238, 234, 255)

FONT_DIR = ROOT / 'assets' / 'fonts'
FRAUNCES = FONT_DIR / 'Fraunces.ttf'
CAVEAT = FONT_DIR / 'Caveat.ttf'
INTER = FONT_DIR / 'Inter.ttf'
CTA_PNG = ROOT / 'assets' / 'ui' / 'book-discovery-call-cta-v5.png'


def font(path, size):
    f = ImageFont.truetype(str(path), size)
    try:
        f.set_variation_by_name('Bold')
    except Exception:
        pass
    return f


def fraunces(size): return font(FRAUNCES, size)
def caveat(size): return font(CAVEAT, size)
def inter(size): return font(INTER, size)


def text_size(draw, text, f):
    if text == '': return (0, 0)
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
        for y in (0, h - 1):
            if is_bg(x, y): seen.add((x, y)); q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(x, y) and (x, y) not in seen:
                seen.add((x, y)); q.append((x, y))
    while q:
        x, y = q.popleft()
        r, g, b, a = pix[x, y]
        pix[x, y] = (r, g, b, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and is_bg(nx, ny):
                seen.add((nx, ny)); q.append((nx, ny))
    return rgba


def load_art(name, max_w, max_h):
    img = Image.open(GEN_DIR / name).convert('RGBA')
    img = transparent_border_background(img)
    bbox = img.split()[-1].getbbox()
    if bbox: img = img.crop(bbox)
    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    return img


def sample_logo(kind):
    sample = Image.open(SAMPLE).convert('RGBA')
    if kind == 'box':
        return sample.crop((66, 57, 166, 157))
    return sample.crop((66, 982, 189, 1010))


def base(page, text_logo=True):
    img = Image.new('RGBA', (W, H), BG)
    d = ImageDraw.Draw(img, 'RGBA')
    spacing, radius = 27, 2.5
    for y in range(14, H + spacing, spacing):
        for x in range(14, W + spacing, spacing):
            d.ellipse((x - radius, y - radius, x + radius, y + radius), fill=DOT)
    img.alpha_composite(sample_logo('box'), (66, 57))
    start_x, y, r, gap = 884, 104, 10, 4
    for i in range(4):
        cx = start_x + r + i * (2 * r + gap)
        d.ellipse((cx - r, y, cx + r, y + 2 * r), fill=ORANGE if i == page - 1 else DARK)
    if text_logo:
        img.alpha_composite(sample_logo('text'), (66, 982))
    return img, d


def paste_shadow(base_img, art, x, y, alpha=16):
    shadow = Image.new('RGBA', art.size, (0, 0, 0, 0))
    sp, ip = shadow.load(), art.load()
    for yy in range(art.height):
        for xx in range(art.width):
            if ip[xx, yy][3] > 0:
                sp[xx, yy] = (232, 83, 40, alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    base_img.alpha_composite(shadow, (x + 10, y + 16))
    base_img.alpha_composite(art, (x, y))


def draw_h1(draw, x, y, lines, size=70, gap=6, align='left'):
    f = fraunces(size)
    yy = y
    for line in lines:
        w, h = text_size(draw, line, f)
        xx = x if align == 'left' else (W - w) // 2
        draw.text((xx, yy), line, font=f, fill=BLACK)
        yy += h + gap
    return yy


def draw_wrapped(draw, x, y, text, f, fill, max_width, gap=7, center=False):
    words = text.split()
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_size(draw, trial, f)[0] <= max_width:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    yy = y
    for line in lines:
        w, h = text_size(draw, line, f)
        xx = x if not center else (W - w) // 2
        draw.text((xx, yy), line, font=f, fill=fill)
        yy += h + gap
    return yy


def footer(draw):
    y = 948
    draw.rectangle((0, y, W, H), fill=PEACH)
    top_f, url_f = inter(24), inter(22)
    top, url = 'Let someone handle the rest.', 'https://hireai.bot'
    tw, th = text_size(draw, top, top_f)
    uw, uh = text_size(draw, url, url_f)
    yy = y + 23
    draw.text(((W - tw) // 2, yy), top, font=top_f, fill=BLACK)
    draw.text(((W - uw) // 2, yy + th + 10), url, font=url_f, fill=ORANGE)


def slide1():
    img, d = base(1)
    draw_h1(d, 0, 205, ['The lead', 'didn’t ghost you.'], 70, 6, 'center')
    f = caveat(76); text = 'Your follow-up did.'
    tw, _ = text_size(d, text, f)
    d.text(((W - tw) // 2, 368), text, font=f, fill=ORANGE)
    d.text(((W - text_size(d, 'Missed replies usually start as tiny dropped handoffs.', inter(26))[0]) // 2, 464), 'Missed replies usually start as tiny dropped handoffs.', font=inter(26), fill=BLACK)
    art = load_art('slide-1-missed-followup.png', 700, 430)
    paste_shadow(img, art, (W - art.width) // 2, 535, 14)
    return img


def slide2():
    img, d = base(2)
    draw_h1(d, 84, 190, ['Every handoff', 'adds one more', 'place to drop it.'], 64, 4)
    labels = ['Inbox', 'CRM', 'Sheet', 'Calendar']
    y0 = 445
    for idx, label in enumerate(labels):
        yy = y0 + idx * 64
        d.rounded_rectangle((84, yy, 365, yy + 42), radius=18, fill=(249, 238, 234, 255))
        d.text((110, yy + 9), label, font=inter(22), fill=BLACK)
    art = load_art('slide-2-handoff-chaos.png', 560, 500)
    paste_shadow(img, art, 466, 415, 14)
    return img


def slide3():
    img, d = base(3)
    draw_h1(d, 0, 205, ['HireAI remembers', 'the next step.'], 72, 6, 'center')
    f = caveat(72); txt = 'Even when your team is busy.'
    tw, _ = text_size(d, txt, f)
    d.text(((W - tw) // 2, 385), txt, font=f, fill=ORANGE)
    body = 'It checks the context, drafts the reply, updates the system, and nudges the right owner.'
    draw_wrapped(d, 0, 485, body, inter(27), BLACK, 790, 7, center=True)
    art = load_art('slide-3-ai-workflow-hub.png', 690, 410)
    paste_shadow(img, art, (W - art.width) // 2, 602, 12)
    return img


def slide4():
    img, d = base(4, text_logo=False)
    draw_h1(d, 72, 185, ['No more', '“who owns this?”'], 69, 6)
    d.text((72, 352), 'Just clear next actions.', font=caveat(70), fill=ORANGE)
    draw_wrapped(d, 72, 460, 'HireAI keeps leads, requests, and follow-ups moving across the tools your team already uses.', inter(26), BLACK, 440, 7)
    art = load_art('slide-4-clear-owner.png', 520, 420)
    paste_shadow(img, art, 535, 420, 12)
    cta = Image.open(CTA_PNG).convert('RGBA')
    cta.thumbnail((380, 90), Image.Resampling.LANCZOS)
    img.alpha_composite(cta, (62, 785))
    img.alpha_composite(sample_logo('text'), (72, 900))
    footer(d)
    return img


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    slides = [slide1(), slide2(), slide3(), slide4()]
    for i, img in enumerate(slides, 1):
        img.convert('RGB').save(OUT_DIR / f'lead-handoff-slide-{i}-1080.png', quality=95)


if __name__ == '__main__':
    main()
