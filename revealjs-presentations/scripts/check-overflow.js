/** Checks reveal.js slides for content overflow using Puppeteer */
const puppeteer = require('puppeteer');
const path = require('path');

async function checkSlideOverflow(htmlPath) {
  const absolutePath = path.resolve(htmlPath);
  const fileUrl = `file://${absolutePath}`;

  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Set viewport to standard presentation size
  await page.setViewport({ width: 1920, height: 1080 });

  await page.goto(fileUrl, { waitUntil: 'networkidle0' });

  // Wait for reveal.js to initialize
  await page.waitForFunction(() => typeof Reveal !== 'undefined' && Reveal.isReady());

  // Get all slides using DOM query (includes vertical slides)
  const results = await page.evaluate(() => {
    const allSlides = document.querySelectorAll('.slides > section, .slides > section > section');
    const slides = [];

    allSlides.forEach((slide, i) => {
      // Skip stack parents (sections that contain nested sections)
      const isStackParent = slide.parentElement.classList.contains('slides') && slide.querySelector('section');
      if (isStackParent) return;

      const id = slide.id || `slide-${i}`;
      const scrollHeight = slide.scrollHeight;
      const scrollWidth = slide.scrollWidth;
      const clientHeight = slide.clientHeight;
      const clientWidth = slide.clientWidth;

      const hasVerticalOverflow = scrollHeight > clientHeight;
      const hasHorizontalOverflow = scrollWidth > clientWidth;

      slides.push({
        index: i,
        id,
        hasOverflow: hasVerticalOverflow || hasHorizontalOverflow,
        hasVerticalOverflow,
        hasHorizontalOverflow,
        dimensions: {
          scrollHeight,
          clientHeight,
          scrollWidth,
          clientWidth,
          verticalDiff: scrollHeight - clientHeight,
          horizontalDiff: scrollWidth - clientWidth
        }
      });
    });

    return slides;
  });

  await browser.close();
  return results;
}

async function main() {
  const htmlPath = process.argv[2];
  if (!htmlPath) {
    console.error('Usage: node check-overflow.js <path-to-html>');
    process.exit(1);
  }

  console.log(`Checking slides for overflow: ${htmlPath}\n`);

  const results = await checkSlideOverflow(htmlPath);

  let hasAnyOverflow = false;

  for (const slide of results) {
    if (slide.hasOverflow) {
      hasAnyOverflow = true;
      console.log(`OVERFLOW: Slide ${slide.index} (${slide.id})`);
      if (slide.hasVerticalOverflow) {
        console.log(`  - Vertical overflow: ${slide.dimensions.verticalDiff}px (content: ${slide.dimensions.scrollHeight}px, container: ${slide.dimensions.clientHeight}px)`);
      }
      if (slide.hasHorizontalOverflow) {
        console.log(`  - Horizontal overflow: ${slide.dimensions.horizontalDiff}px (content: ${slide.dimensions.scrollWidth}px, container: ${slide.dimensions.clientWidth}px)`);
      }
    }
  }

  if (!hasAnyOverflow) {
    console.log('No overflow detected on any slides.');
  }

  console.log(`\nTotal slides checked: ${results.length}`);
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
