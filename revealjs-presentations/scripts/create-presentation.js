#!/usr/bin/env node

/**
 * Creates a reveal.js presentation scaffold with the specified options.
 * Usage: node create-presentation.js [options]
 */

const fs = require('fs');
const path = require('path');

// Path to the base styles file (relative to this script)
const BASE_STYLES_PATH = path.join(__dirname, '..', 'references', 'base-styles.css');

function parseArgs(args) {
  const options = {
    slides: null,
    structure: null,
    output: 'presentation.html',
    title: 'Presentation',
    stylesFile: 'styles.css',
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--slides' || arg === '-s') {
      options.slides = parseInt(args[++i], 10);
    } else if (arg === '--structure') {
      options.structure = args[++i].split(',').map(n => n === 'd' ? 'd' : parseInt(n, 10));
    } else if (arg === '--output' || arg === '-o') {
      options.output = args[++i];
    } else if (arg === '--title') {
      options.title = args[++i];
    } else if (arg === '--styles') {
      options.stylesFile = args[++i];
    } else if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    }
  }

  return options;
}

function printHelp() {
  console.log(`
create-presentation.js - Generate a reveal.js presentation scaffold

Usage: node create-presentation.js [options]

Options:
  --slides, -s <num>    Number of horizontal slides (simple mode)
  --structure <list>    Mixed layout: comma-separated values (e.g., "1,1,d,3,1,d,1")
                        - Number 1 = single horizontal slide
                        - Number >1 = vertical stack of that many slides
                        - 'd' = section divider slide
                        Cannot be used with --slides
  --output, -o <file>   Output HTML filename (default: presentation.html)
  --title <text>        Presentation title (default: Presentation)
  --styles <file>       Custom CSS filename (default: styles.css)
  --help, -h            Show this help message

Examples:
  node create-presentation.js --slides 10 -o my-deck.html
  node create-presentation.js --structure 1,1,d,3,1,d,1 -o my-deck.html
  node create-presentation.js --structure 1,1,1,d,3,d,1,1 --title "Q4 Review"
`);
}

/** Generates slides from a structure array (e.g., [1, 1, 'd', 5, 1, 2]) */
function generateSlides(structure) {
  let slides = '';
  let hIndex = 1; // Horizontal index (1-based for display)
  let dividerCount = 1;

  for (let colIndex = 0; colIndex < structure.length; colIndex++) {
    const item = structure[colIndex];

    if (item === 'd') {
      // Section divider
      slides += `
      <section id="divider-${dividerCount}" class="section-divider" data-state="is-section-divider">
        <h1>Section ${dividerCount} Title</h1>
      </section>
`;
      dividerCount++;
      hIndex++;
    } else if (item === 1) {
      // Single horizontal slide
      if (hIndex === 1) {
        slides += `
      <section id="title" class="section-divider" data-state="is-section-divider">
        <h1>Presentation Title</h1>
      </section>
`;
      } else {
        slides += `
      <section id="slide-${hIndex}">
        <h2>Slide ${hIndex} Title Here</h2>
      </section>
`;
      }
      hIndex++;
    } else {
      // Vertical stack
      slides += `
      <section>
`;
      for (let vIndex = 1; vIndex <= item; vIndex++) {
        slides += `        <section id="slide-${hIndex}-${vIndex}">
          <h2>Slide ${hIndex}.${vIndex} Title Here</h2>
        </section>
`;
      }
      slides += `      </section>
`;
      hIndex++;
    }
  }

  return slides;
}

function generateHTML(options) {
  const slidesContent = generateSlides(options.structure);

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${options.title}</title>

  <!-- Reveal.js core -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reset.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.css">

  <!-- Font Awesome for icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

  <!-- Custom styles -->
  <link rel="stylesheet" href="${options.stylesFile}">

  <!-- Chart.js for data visualization -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
  <div class="reveal">
    <div class="slides">
${slidesContent}
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.1.0/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>
  <script>
    Reveal.initialize({
      width: 1280,
      height: 720,
      margin: 0,
      controls: true,
      progress: true,
      slideNumber: false,
      hash: true,
      transition: 'slide',
      center: false,
      plugins: [ RevealChart ],
      chart: {
        defaults: Object.assign({
          color: 'rgba(0, 0, 0, 0.8)',
          borderColor: 'rgba(0, 0, 0, 0.8)',
          devicePixelRatio: 2
        }, window.location.search.includes('export') ? { animation: false } : {})
      }
    });
  </script>
</body>
</html>
`;
}

function main() {
  const args = process.argv.slice(2);
  const options = parseArgs(args);

  // Validate mutually exclusive options
  if (options.slides !== null && options.structure !== null) {
    console.error('Error: Cannot use both --slides and --structure. Choose one.');
    process.exit(1);
  }

  // Default to 5 horizontal slides if neither specified
  if (options.slides === null && options.structure === null) {
    options.structure = [1, 1, 1, 1, 1];
  } else if (options.slides !== null) {
    // Convert --slides N to structure of N ones
    if (options.slides < 1 || isNaN(options.slides)) {
      console.error('Error: Slide count must be at least 1.');
      process.exit(1);
    }
    options.structure = Array(options.slides).fill(1);
  } else {
    // Validate structure
    if (options.structure.some(n => n !== 'd' && (n < 1 || isNaN(n)))) {
      console.error('Error: Structure values must be positive integers or "d" for dividers.');
      process.exit(1);
    }
  }

  const totalSlides = options.structure.reduce((a, b) => a + (b === 'd' ? 1 : b), 0);

  // Determine output directory from the output path
  const outputDir = path.dirname(options.output);

  // Ensure output directory exists
  if (outputDir && outputDir !== '.') {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Generate and write HTML
  const html = generateHTML(options);
  fs.writeFileSync(options.output, html);
  console.log(`Created ${options.output}`);

  // Copy example-styles.css to output directory as styles.css (if it doesn't exist)
  const stylesOutputPath = outputDir && outputDir !== '.'
    ? path.join(outputDir, options.stylesFile)
    : options.stylesFile;

  if (!fs.existsSync(stylesOutputPath)) {
    if (fs.existsSync(BASE_STYLES_PATH)) {
      fs.copyFileSync(BASE_STYLES_PATH, stylesOutputPath);
      console.log(`Copied base-styles.css to ${stylesOutputPath}`);
    } else {
      console.warn(`Warning: Could not find ${BASE_STYLES_PATH}`);
      console.warn(`Please manually copy the base styles to ${stylesOutputPath}`);
    }
  } else {
    console.log(`${stylesOutputPath} already exists, skipping`);
  }

  console.log(`\nPresentation created with ${totalSlides} slides (structure: ${options.structure.join(',')}).`);
  console.log(`Customize colors in ${stylesOutputPath}, then open ${options.output} in a browser to view.`);
}

main();
