import { chromium } from 'playwright';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs/promises';

const [,, htmlPath, outDir, prefix = 'slide'] = process.argv;

if (!htmlPath || !outDir) {
  console.error('Usage: node scripts/render-html-carousel.mjs <htmlPath> <outDir> [prefix]');
  process.exit(1);
}

await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1200, height: 1200 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(path.resolve(htmlPath)).href, { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; });

  const slides = await page.$$('.slide, .hireai-creative');
  if (slides.length === 0) {
    throw new Error('No slides found. Expected elements with class .slide or .hireai-creative');
  }

  for (let i = 0; i < slides.length; i += 1) {
    await slides[i].screenshot({ path: path.join(outDir, `${prefix}-${i + 1}-1080.png`) });
  }

  console.log(`Rendered ${slides.length} slide(s) to ${outDir}`);
} finally {
  await browser.close();
}
