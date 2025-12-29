---
name: revealjs-presentations
description: Create polished, professional reveal.js presentations. Use when the user asks to create slides, a presentation, a deck, or a slideshow. Supports themes, multi-column layouts, callout boxes, code highlighting, animations, speaker notes, and custom styling. Generates HTML + CSS with no build step required.
---

# Reveal.js Presentations

Create polished, professional HTML presentations using reveal.js. No build step required - just open the generated HTML in a browser. Can also be exported as PDF.

## When to Use This Skill

- When you need to create a slide deck or presentation
- When you want professional-looking slides without PowerPoint or Keynote
- When you need data visualizations (charts) in your presentation
- When you want a portable HTML file you can share or host anywhere
- When you need speaker notes for presenting

## What This Skill Does

1. **Generates Complete Presentations**: Creates HTML and CSS files for reveal.js presentations with professional styling
2. **Applies Creative Themes**: Selects color palettes and typography that match your content and brand
3. **Supports Rich Layouts**: Multi-column layouts, callout boxes, blockquotes, and Font Awesome icons
4. **Adds Data Visualization**: Chart.js integration for bar, line, pie, and other chart types
5. **Checks Quality**: Automated overflow detection and screenshot review to catch visual issues

## How to Use

### Basic Usage

```
Create a 10-slide presentation about renewable energy trends
```

### Advanced Usage

```
Create a quarterly business review presentation with:
- Executive summary slide
- Revenue charts comparing Q3 vs Q4
- Key metrics in a 3-column layout
- Next quarter goals
Use a professional blue and gray color scheme
```

## Example

**User**: "Create a 5-slide pitch deck for a mobile app called FitTrack"

**Output**: Claude generates:
- `presentation.html` - Complete reveal.js presentation with 5 slides
- `styles.css` - Custom theme with fitness-inspired colors
- Screenshots of each slide for review

**Inspired by:** [reveal.js](https://revealjs.com/) presentation framework

## Tips

- Provide context about your topic so Claude can choose appropriate colors and styling
- Mention any brand colors you want incorporated
- Request specific chart types if you have data to visualize
- Ask for speaker notes if you'll be presenting live

## Common Use Cases

- Pitch decks and investor presentations
- Quarterly business reviews
- Educational lectures and training materials
- Conference talks and meetup presentations
- Product launches and feature announcements

---

## Technical Implementation

The following sections contain detailed instructions for Claude on how to create presentations.

## What You Create

A reveal.js presentation consists of:

1. **HTML file** - Contains slides and loads reveal.js from CDN
2. **CSS file** - Custom styles for layouts, colors, typography, and components

## Design Principles

**CRITICAL**: Before creating any presentation, analyze the content and choose appropriate design elements:

1. **Consider the subject matter**: What is this presentation about? What tone, industry, or mood does it suggest?
2. **Check for branding**: If the user mentions a company/organization, consider their brand colors and identity
3. **Match palette to content**: Select colors that reflect the subject
4. **State your approach**: Explain your design choices before writing code

**Requirements**:
- ✅ State your content-informed design approach BEFORE writing code
- ✅ Use web-safe fonts (Arial, Helvetica, Georgia, Verdana, etc.) or Google Fonts via `@import` in CSS
- ✅ Create clear visual hierarchy through size, weight, and color
- ✅ Ensure readability: strong contrast, appropriately sized text, clean alignment
- ✅ Be consistent: repeat patterns, spacing, and visual language across slides
- ✅ **Always use `pt` (points) for font sizes** - slides are fixed-size, so `pt` is predictable and familiar (like PowerPoint/Keynote). Never use `em`, `rem`, or `px` for font sizes.

### Color Palette Selection

**Choosing colors creatively**:
- **Think beyond defaults**: What colors genuinely match this specific topic? Avoid autopilot choices.
- **Consider multiple angles**: Topic, industry, mood, energy level, target audience, brand identity (if mentioned)
- **Be adventurous**: Try unexpected combinations - a healthcare presentation doesn't have to be green, finance doesn't have to be navy
- **Build your palette**: Pick 3-5 colors that work together (dominant colors + supporting tones + accent)
- **Ensure contrast**: Text must be clearly readable on backgrounds

**Example color palettes** (use these to spark creativity - choose one, adapt it, or create your own):

1. **Classic Blue**: Deep navy (#1C2833), slate gray (#2E4053), silver (#AAB7B8), off-white (#F4F6F6)
2. **Teal & Coral**: Teal (#5EA8A7), deep teal (#277884), coral (#FE4447), white (#FFFFFF)
3. **Bold Red**: Red (#C0392B), bright red (#E74C3C), orange (#F39C12), yellow (#F1C40F), green (#2ECC71)
4. **Warm Blush**: Mauve (#A49393), blush (#EED6D3), rose (#E8B4B8), cream (#FAF7F2)
5. **Burgundy Luxury**: Burgundy (#5D1D2E), crimson (#951233), rust (#C15937), gold (#997929)
6. **Deep Purple & Emerald**: Purple (#B165FB), dark blue (#181B24), emerald (#40695B), white (#FFFFFF)
7. **Cream & Forest Green**: Cream (#FFE1C7), forest green (#40695B), white (#FCFCFC)
8. **Pink & Purple**: Pink (#F8275B), coral (#FF574A), rose (#FF737D), purple (#3D2F68)
9. **Lime & Plum**: Lime (#C5DE82), plum (#7C3A5F), coral (#FD8C6E), blue-gray (#98ACB5)
10. **Black & Gold**: Gold (#BF9A4A), black (#000000), cream (#F4F6F6)
11. **Sage & Terracotta**: Sage (#87A96B), terracotta (#E07A5F), cream (#F4F1DE), charcoal (#2C2C2C)
12. **Charcoal & Red**: Charcoal (#292929), red (#E33737), light gray (#CCCBCB)
13. **Vibrant Orange**: Orange (#F96D00), light gray (#F2F2F2), charcoal (#222831)
14. **Forest Green**: Black (#191A19), green (#4E9F3D), dark green (#1E5128), white (#FFFFFF)
15. **Retro Rainbow**: Purple (#722880), pink (#D72D51), orange (#EB5C18), amber (#F08800), gold (#DEB600)
16. **Vintage Earthy**: Mustard (#E3B448), sage (#CBD18F), forest green (#3A6B35), cream (#F4F1DE)
17. **Coastal Rose**: Old rose (#AD7670), beaver (#B49886), eggshell (#F3ECDC), ash gray (#BFD5BE)
18. **Orange & Turquoise**: Light orange (#FC993E), grayish turquoise (#667C6F), white (#FCFCFC)

### Slide Content Principles

**Diverse presentation is key.** Even when slides have similar content types, vary the visual presentation:

- Use **different layouts** across slides: columns on one, stacked boxes on another, callouts with icons on a third
- Mix container styles: plain text, boxes, callouts, blockquotes
- Use **visual hierarchy**: `<strong>` for key terms, different colors to distinguish categories
- Break up lists with other elements (quotes, callouts, columns)
- Don't repeat the same layout pattern on consecutive slides

**Keep it scannable:**
- Short bullet points, not paragraphs
- One main idea per slide when possible
- Use icons (Font Awesome) to add visual interest

**When a slide has less content, make it bigger** - don't leave empty space with tiny text.

## Workflow

### Step 1: Plan the Structure

Based on the user's content, determine:
- How many slides are needed
- Which slides should be section dividers (centered, larger text)
- Where to use vertical slide stacks for drill-down content

### Step 2: Generate the Scaffold

Use the `create-presentation.js` script (located in the `scripts/` directory next to this SKILL.md file) to generate the HTML scaffold.

```bash
node <path-to-skill>/scripts/create-presentation.js --structure 1,1,d,3,1,d,1 --title "My Presentation" --output presentation.html
```

**Finding the script path:** The script is at `scripts/create-presentation.js` relative to where this SKILL.md file is located. Common locations:
- Project skill: `.claude/skills/revealjs/scripts/create-presentation.js`
- User skill: `~/.claude/skills/revealjs/scripts/create-presentation.js`

**Options:**
- `--slides N` - Create N horizontal slides (simple mode)
- `--structure <list>` - Mixed layout with comma-separated values:
  - `1` = single horizontal slide
  - `N` (where N > 1) = vertical stack of N slides
  - `d` = section divider slide (centered, no content wrapper)
- `--output <file>` - Output filename (default: presentation.html)
- `--title <text>` - Presentation title
- `--styles <file>` - Custom CSS filename (default: styles.css)

**Examples:**
```bash
# 10 horizontal slides
node <path-to-skill>/scripts/create-presentation.js --slides 10 --output presentation.html

# Mixed structure: intro, 2 content slides, divider, 3-slide vertical stack, divider, closing
node <path-to-skill>/scripts/create-presentation.js --structure 1,1,1,d,3,d,1 --title "Q4 Review" --output presentation.html
```

### Step 3: Customize the CSS

The scaffold script automatically copies `base-styles.css` to your presentation directory as `styles.css`. Now customize the CSS variables (especially colors) for your presentation theme.

**Using Google Fonts:** Add an `@import` at the top of your CSS file:
```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;600&display=swap');

:root {
  --heading-font: "Playfair Display", Georgia, serif;
  --body-font: "Lato", Helvetica, sans-serif;
  /* ... */
}
```

The base file includes:

1. **CSS Variables** for easy customization:
```css
:root {
  /* ===========================================
     BACKGROUND COLOR - Set this first!
     =========================================== */
  --background-color: #ffffff;  /* Change for dark themes (e.g., #1a1a2e) */

  /* Typography - ALWAYS use pt for font sizes */
  --heading-font: "Source Sans Pro", Helvetica, sans-serif;
  --body-font: "Source Sans Pro", Helvetica, sans-serif;
  --base-font-size: 32px;  /* Only px value - sets reveal.js base */
  --text-size: 16pt;       /* Base body text - intentionally small */
  --h1-size: 48pt;
  --h2-size: 36pt;
  --h3-size: 24pt;

  /* Colors - customize these for each presentation */
  --primary-color: #2196F3;
  --secondary-color: #ff9800;
  --text-color: #222;       /* Use light color (e.g., #FAF7F2) for dark backgrounds */
  --muted-color: #666;      /* Adjust for dark backgrounds too */
  --box-bg: #f5f5f5;
  --box-border: #ddd;
}
```

2. **Override reveal.js styles** using `.reveal` prefix:
```css
.reveal {
  font-family: var(--body-font);
}

.reveal h1, .reveal h2, .reveal h3 {
  font-family: var(--heading-font);
  text-transform: none;
  color: var(--text-color);
}

.reveal p, .reveal li {
  font-size: var(--text-size);
  color: var(--text-color);
}
```

3. **Slide layout styles** - control padding and positioning:
```css
.reveal .slides section {
  padding: 40px 60px;
  text-align: left;
}
```

4. **Component classes** - boxes, callouts, etc. (see [CSS Components Reference](#css-components-reference))

5. **Text size utilities** (use these to scale up text when slides have less content):
```css
/* Base text is 16pt - use these classes to increase size when needed */
.text-lg { font-size: 18pt; }    /* Slightly larger */
.text-xl { font-size: 20pt; }    /* Medium emphasis */
.text-2xl { font-size: 24pt; }   /* Strong emphasis */
.text-3xl { font-size: 28pt; }   /* Very large */
.text-4xl { font-size: 32pt; }   /* Maximum body text */
.text-muted { color: var(--muted-color); }
.text-center { text-align: center; }
```

**Typography guidance:**
- Base text (`--text-size: 16pt`) is intentionally small to fit more content
- When a slide has less content, use `.text-lg`, `.text-xl`, etc. to fill space appropriately
- This approach prevents overflow on content-heavy slides while allowing flexibility on lighter slides

### Step 4: Fill in the HTML Content

Edit the generated HTML file to add content to each slide. Follow these patterns:

**Standard slide structure:**
```html
<section id="unique-slide-id">
  <h2>Slide Title</h2>
  <div class="content">
    <!-- Content here -->
  </div>
</section>
```

**Multi-column layouts** - always use inline CSS grid (do NOT create utility classes like `.grid-2`):
```html
<!-- Equal columns -->
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 30px;">
  <div>Column 1</div>
  <div>Column 2</div>
</div>

<!-- Three columns -->
<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px;">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>

<!-- Unequal columns -->
<div style="display: grid; grid-template-columns: 1fr 2fr; gap: 30px;">
  <div>Narrow sidebar</div>
  <div>Wide main content</div>
</div>
```

Why inline styles for grids? Each slide's layout needs vary - column ratios, gaps, etc. Inline styles give you full control per-slide without creating dozens of utility classes.

**Important HTML patterns:**
- Every `<section>` should have a unique `id` attribute for stable identification
- Use `class="section-divider"` for centered section title slides
- Wrap main content in `<div class="content">` for consistent spacing. This is a flexbox container that fills the remaining vertical space below the title, ensuring content flows properly.
- Use `<div class="footnote">` for attribution or source text at bottom

### Step 5: Check for Content Overflow

Run the overflow checker to ensure no slides have content that extends beyond boundaries:

```bash
node scripts/check-overflow.js presentation.html
```

The script checks each slide for:
- **Vertical overflow**: Content taller than slide height
- **Horizontal overflow**: Content wider than slide width

If overflow is detected, reduce content or adjust font sizes on affected slides.

### Step 6: Visual Review with Screenshots

**CRITICAL: You MUST review screenshots of EVERY SINGLE SLIDE.** Do not skip slides or review only a sample. Visual issues are common and can only be caught by examining each slide individually.

Capture screenshots of all slides:

```bash
cd <presentation-directory>
npx decktape reveal "presentation.html?export" output.pdf \
  --screenshots \
  --screenshots-directory "screenshots/$(date +%Y%m%d_%H%M%S)"
```

**Note:** The `?export` query parameter disables chart animations for cleaner PDF rendering. Charts will still animate when viewing the HTML directly in a browser.

This creates a timestamped folder (e.g., `screenshots/20241210_143052/`) so you can track versions and compare before/after fixes.

Then use the Read tool to examine each screenshot image file.

#### What to Look For

The overflow script catches most layout issues, but these problems require visual inspection:

1. **Color inheritance in containers**: Text inside boxes or callouts may inherit the wrong color from parent elements. If you have light text on a dark page background, text inside a light-colored `.box` or `.callout` will be unreadable unless you explicitly set dark text color for that container.

   **Fix pattern** - explicitly set text and bullet colors for light containers:
   ```css
   .box-light p,
   .box-light li {
     color: var(--text-dark);
   }

   .box-light ul li::before {
     background: var(--primary-color);  /* bullet color */
   }
   ```

2. **Custom bullet/list styling**: If you override default list styles, bullets may not contrast well on all container backgrounds.

3. **Icons not rendering**: If Font Awesome fails to load, you'll see empty squares or nothing where icons should be.

4. **Overflow edge cases**: The script catches most overflow, but complex nested layouts occasionally slip through.

5. **Unexpected text wrap**: Text that you expected to fit on one line actually overflows to two lines. This is especially common in column layouts, where the header of one column may wrap while the rest don't, making things uneven.

**Re-capture specific slides after fixes:**
```bash
npx decktape reveal "presentation.html?export" output.pdf \
  --screenshots \
  --screenshots-directory "screenshots/$(date +%Y%m%d_%H%M%S)" \
  --slides 2,5,7-9
```

Then re-examine the updated screenshots to verify fixes. The new timestamped folder makes it easy to compare with the previous version.

## CSS Components Reference

### Boxes
```css
.box {
  background: var(--box-bg);
  border: 1px solid var(--box-border);
  border-radius: 8px;
  padding: 20px;
}

.box-outlined {
  border: 1px solid var(--box-border);
  border-radius: 8px;
  padding: 20px;
  background: transparent;
}
```

### Callouts
```css
.callout {
  border-left: 6px solid var(--primary-color);
  padding: 15px 20px;
  margin: 15px 0;
  background: #f9f9f9;
  border-radius: 8px;
}

/* Color variants */
.callout-blue { border-left-color: #2196F3; background: #e3f2fd; }
.callout-orange { border-left-color: #ff9800; background: #fff3e0; }
.callout-green { border-left-color: #4caf50; background: #e8f5e9; }
.callout-gray { border-left-color: #666; background: #f5f5f5; }
```

### Blockquotes
```css
.reveal blockquote {
  border-left: 4px solid var(--primary-color);
  padding-left: 20px;
  margin: 20px 0;
  font-style: italic;
  background: none;
  box-shadow: none;
  width: 100%;
}

.reveal blockquote cite {
  display: block;
  margin-top: 10px;
  font-style: normal;
  color: var(--muted-color);
}
```

### Icons (Font Awesome)

Font Awesome is included in the scaffold. Usage:
```html
<i class="fa-solid fa-lightbulb"></i>
<i class="fa-solid fa-check"></i>
<i class="fa-solid fa-gears"></i>
```

## Advanced Features

For fragments (progressive reveal), speaker notes, custom backgrounds, auto-animate, and transitions, see [references/advanced-features.md](references/advanced-features.md).

## Reveal.js Configuration

```javascript
Reveal.initialize({
  controls: true,          // Show navigation arrows
  progress: true,          // Show progress bar
  slideNumber: true,       // Show slide numbers
  hash: true,              // Update URL hash for each slide
  transition: 'slide',     // none/fade/slide/convex/concave/zoom
  center: false,           // Vertical centering of slide content
  autoSlide: 0,            // Auto-advance (ms), 0 to disable
  loop: false,             // Loop presentation
});
```

**Note on `center`:** Default is `false` (content aligns to top), which works best for content-heavy slides. Set to `true` for minimal/creative presentations where you want content vertically centered.

## Built-in Reveal.js Classes

Use these directly without custom CSS:

- `r-fit-text` - Auto-size text to fill slide
- `r-stretch` - Stretch element to fill remaining vertical space
- `r-stack` - Layer elements on top of each other

```html
<h1 class="r-fit-text">BIG TEXT</h1>
<img class="r-stretch" src="image.jpg">
```

## Adding Charts

**IMPORTANT: Before adding ANY chart, you MUST read [references/charts.md](references/charts.md).** Charts require specific flexbox/grid patterns to size correctly and avoid overflow. Do not attempt to add charts without reading the full documentation first.

The scaffold includes the Chart.js plugin for adding bar, line, pie, doughnut, and scatter charts to slides.

**Required pattern** - charts need flexbox containers and `maintainAspectRatio: false`:

```html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>Chart Title</h2>
  <div style="flex: 1; position: relative; min-height: 0;">
    <canvas data-chart="bar">
    <!--
    {
      "data": {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [{ "label": "Revenue", "data": [12, 19, 8, 15] }]
      },
      "options": {
        "maintainAspectRatio": false
      }
    }
    -->
    </canvas>
  </div>
</section>
```

**[references/charts.md](references/charts.md) covers (required reading):**
- Layout patterns: full slide, half (horizontal/vertical), quarter, unequal splits (1fr 2fr, 1fr 3fr)
- Why the flexbox pattern is required (Chart.js aspect ratio behavior)
- All chart types (bar, line, pie, doughnut, scatter, etc.)
- Styling and color options
- CSV data format (simpler alternative to JSON)

## Dependencies

Required for the scripts, should be already installed:
- **Node.js** (for running scripts)
- **Puppeteer** (for overflow checking): `npm install puppeteer`
- **Decktape** (for screenshots): `npx decktape` (runs directly)
