from PIL import Image, ImageDraw
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'exports' / 'hireai-light-page-1-proof.png'
W = H = 1080
orange = (232, 83, 40, 255)
dark = (63, 65, 66, 255)
bg = (255, 255, 255, 255)
dot = (234, 236, 240, 108)

img = Image.new('RGBA', (W, H), bg)
d = ImageDraw.Draw(img, 'RGBA')

spacing = 27
radius = 2.55
for y in range(14, H + spacing, spacing):
    for x in range(14, W + spacing, spacing):
        d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=dot)

# Proof render uses the exact exported PNG logos from the supplied SVG assets.
# HTML/CSS source uses the exact SVG files under assets/logos/.
box = Image.open('/root/.openclaw/media/inbound/HireAI_Box_Logo---f4193e74-81b4-46da-b1ef-93b3d90d7460.png').convert('RGBA')
text = Image.open('/root/.openclaw/media/inbound/HireAI_Text_Logo---fcf1ebd1-936a-43ae-87a1-b163dd8d2916.png').convert('RGBA')
img.alpha_composite(box, (66, 57))

start_x, y, r, gap = 884, 104, 10, 4
for i in range(4):
    cx = start_x + r + i * (2*r + gap)
    color = orange if i == 0 else dark
    d.ellipse((cx-r, y, cx+r, y+2*r), fill=color)

img.alpha_composite(text, ((W - text.width)//2, 982))
OUT.parent.mkdir(parents=True, exist_ok=True)
img.convert('RGB').save(OUT, quality=100)
print(OUT)
