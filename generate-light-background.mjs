import { writeFileSync } from 'node:fs';
import { deflateSync } from 'node:zlib';

const width = 1080;
const height = 1080;
const spacing = 27;
const radius = 2.55;
const bg = [255, 255, 255];
const dot = [234, 236, 240]; // subtle cool gray circles, slightly more visible
const opacity = 0.64;

function crc32(buf) {
  let c = ~0;
  for (let i = 0; i < buf.length; i++) {
    c ^= buf[i];
    for (let k = 0; k < 8; k++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1));
  }
  return ~c >>> 0;
}

function chunk(type, data = Buffer.alloc(0)) {
  const typeBuf = Buffer.from(type);
  const out = Buffer.alloc(12 + data.length);
  out.writeUInt32BE(data.length, 0);
  typeBuf.copy(out, 4);
  data.copy(out, 8);
  out.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 8 + data.length);
  return out;
}

function blend(base, color, alpha) {
  return Math.round(base * (1 - alpha) + color * alpha);
}

const raw = Buffer.alloc((width * 3 + 1) * height);
for (let y = 0; y < height; y++) {
  const row = y * (width * 3 + 1);
  raw[row] = 0; // PNG filter type: none
  for (let x = 0; x < width; x++) {
    let r = bg[0], g = bg[1], b = bg[2];

    // Dots start slightly inside the canvas, matching the reference image.
    const gx = ((x - 14) % spacing + spacing) % spacing;
    const gy = ((y - 14) % spacing + spacing) % spacing;
    const dx = Math.min(gx, spacing - gx);
    const dy = Math.min(gy, spacing - gy);
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist <= radius + 0.85) {
      // Soft edge anti-aliasing so dots feel printed, not harsh.
      const edge = Math.max(0, Math.min(1, radius + 0.85 - dist));
      const a = opacity * Math.min(1, edge);
      r = blend(r, dot[0], a);
      g = blend(g, dot[1], a);
      b = blend(b, dot[2], a);
    }

    const i = row + 1 + x * 3;
    raw[i] = r;
    raw[i + 1] = g;
    raw[i + 2] = b;
  }
}

const ihdr = Buffer.alloc(13);
ihdr.writeUInt32BE(width, 0);
ihdr.writeUInt32BE(height, 4);
ihdr[8] = 8;  // bit depth
ihdr[9] = 2;  // truecolor RGB
ihdr[10] = 0; // compression
ihdr[11] = 0; // filter
ihdr[12] = 0; // interlace

const png = Buffer.concat([
  Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]),
  chunk('IHDR', ihdr),
  chunk('IDAT', deflateSync(raw, { level: 9 })),
  chunk('IEND')
]);

writeFileSync('/root/Documents/social-creative-system/light-background-1080.png', png);
console.log('Generated /root/Documents/social-creative-system/light-background-1080.png');
