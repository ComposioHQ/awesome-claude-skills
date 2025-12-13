# Adding Charts to Reveal.js Presentations

Charts are added using the [reveal.js-plugins/chart](https://github.com/rajgoel/reveal.js-plugins) plugin, which integrates Chart.js into your slides.

## Setup

The chart plugin is included by default in the scaffold. It adds these to your HTML:

```html
<!-- In <head> -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- Before Reveal.initialize() -->
<script src="https://cdn.jsdelivr.net/npm/reveal.js-plugins@latest/chart/plugin.js"></script>

<!-- In Reveal.initialize() -->
Reveal.initialize({
  plugins: [ RevealChart ],
  chart: {
    defaults: {
      color: 'lightgray',
      borderColor: 'lightgray'
    }
  }
});
```

## Chart Types

**Supported types:** `line`, `bar`, `pie`, `doughnut`, `radar`, `polarArea`, `bubble`, `scatter`

For most presentations, you'll use:
- **bar** - Comparing categories
- **line** - Trends over time
- **pie/doughnut** - Parts of a whole
- **scatter** - Relationships between variables

## Chart Sizing (IMPORTANT)

Charts MUST use one of these four layout options to properly fill their space without overflow:

1. **Full slide** - Chart fills entire slide below title
2. **Half slide (horizontal)** - Chart on left or right, content on the other side
3. **Half slide (vertical)** - Chart on top or bottom, content on the other half
4. **Quarter slide** - Chart in one quadrant, other content in remaining three

### Required CSS Pattern

Every chart needs:
1. **Flexbox section** with `display: flex; flex-direction: column; height: 100%;`
2. **Container div** with `flex: 1; position: relative; min-height: 0;` (and `min-width: 0` for grid layouts)
3. **`maintainAspectRatio: false`** in chart options

### Full Slide Layout

```html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>Chart Title</h2>
  <div style="flex: 1; position: relative; min-height: 0;">
    <canvas data-chart="bar">
    <!--
    {
      "data": {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [{
          "label": "Revenue",
          "data": [45, 52, 61, 78],
          "backgroundColor": "#2196F3"
        }]
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

### Half Slide - Horizontal (Left/Right)

Chart on right, content on left:

```html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>Chart Title</h2>
  <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; min-height: 0; min-width: 0;">
    <div style="display: flex; flex-direction: column; justify-content: center; background: #f5f5f5; padding: 20px; border-radius: 8px;">
      <p><strong>Key Points</strong></p>
      <ul>
        <li>First insight</li>
        <li>Second insight</li>
        <li>Third insight</li>
      </ul>
    </div>
    <div style="position: relative; min-height: 0; min-width: 0;">
      <canvas data-chart="pie">
      <!--
      {
        "data": {
          "labels": ["A", "B", "C"],
          "datasets": [{
            "data": [45, 35, 20],
            "backgroundColor": ["#2196F3", "#4caf50", "#ff9800"]
          }]
        },
        "options": {
          "maintainAspectRatio": false
        }
      }
      -->
      </canvas>
    </div>
  </div>
</section>
```

### Half Slide - Vertical (Top/Bottom)

Content on top, chart on bottom (equal halves):

```html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>Chart Title</h2>
  <div style="flex: 1; display: grid; grid-template-rows: 1fr 1fr; gap: 20px; min-height: 0; min-width: 0;">
    <div style="display: flex; align-items: center; justify-content: center; background: #f5f5f5; padding: 20px; border-radius: 8px;">
      <div>
        <p><strong>Analysis Summary</strong></p>
        <p>Description of what the chart shows and key takeaways.</p>
      </div>
    </div>
    <div style="position: relative; min-height: 0; min-width: 0;">
      <canvas data-chart="line">
      <!--
      {
        "data": {
          "labels": ["Jan", "Feb", "Mar", "Apr"],
          "datasets": [{
            "label": "Trend",
            "data": [10, 25, 35, 50],
            "borderColor": "#2196F3",
            "fill": false
          }]
        },
        "options": {
          "maintainAspectRatio": false
        }
      }
      -->
      </canvas>
    </div>
  </div>
</section>
```

### Content Header + Chart Below (Unequal Split)

Small content area on top (1/4 or 1/3), chart fills the rest. Use explicit fractions for predictable sizing:

**1/4 content, 3/4 chart:**
```html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>Chart Title</h2>
  <div style="flex: 1; display: grid; grid-template-rows: 1fr 3fr; gap: 20px; min-height: 0; min-width: 0;">
    <div style="display: flex; align-items: center; background: #f5f5f5; padding: 15px 20px; border-radius: 8px;">
      <p><strong>Key insight:</strong> Revenue grew 25% quarter-over-quarter, exceeding targets.</p>
    </div>
    <div style="position: relative; min-height: 0; min-width: 0;">
      <canvas data-chart="bar">
      <!--
      {
        "data": {
          "labels": ["Q1", "Q2", "Q3", "Q4"],
          "datasets": [{
            "label": "Revenue",
            "data": [45, 52, 61, 78],
            "backgroundColor": "#2196F3"
          }]
        },
        "options": {
          "maintainAspectRatio": false
        }
      }
      -->
      </canvas>
    </div>
  </div>
</section>
```

**1/3 content, 2/3 chart:**
```html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>Chart Title</h2>
  <div style="flex: 1; display: grid; grid-template-rows: 1fr 2fr; gap: 20px; min-height: 0; min-width: 0;">
    <div style="display: flex; flex-direction: column; justify-content: center; background: #f5f5f5; padding: 15px 20px; border-radius: 8px;">
      <p><strong>Summary</strong></p>
      <ul style="margin: 10px 0 0 0;">
        <li>Strong Q4 performance</li>
        <li>All regions exceeded targets</li>
      </ul>
    </div>
    <div style="position: relative; min-height: 0; min-width: 0;">
      <canvas data-chart="line">
      <!--
      {
        "data": {
          "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          "datasets": [{
            "label": "Growth",
            "data": [100, 120, 135, 150, 180, 210],
            "borderColor": "#2196F3",
            "fill": false
          }]
        },
        "options": {
          "maintainAspectRatio": false
        }
      }
      -->
      </canvas>
    </div>
  </div>
</section>
```

**Common row fractions:**
- `1fr 3fr` - 25% content / 75% chart (minimal text)
- `1fr 2fr` - 33% content / 67% chart (short paragraph or bullet list)
- `1fr 1fr` - 50% / 50% equal split

### Quarter Slide (Quadrant)

Chart in one quadrant (bottom-right), other content in remaining three:

```html
<section style="display: flex; flex-direction: column; height: 100%;">
  <h2>Dashboard View</h2>
  <div style="flex: 1; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 15px; min-height: 0; min-width: 0;">
    <div style="display: flex; align-items: center; justify-content: center; background: #e3f2fd; padding: 15px; border-radius: 8px;">
      <div style="text-align: center;">
        <p style="font-size: 2em; margin: 0; color: #1565c0;">$2.4M</p>
        <p style="margin: 0; color: #666;">Total Revenue</p>
      </div>
    </div>
    <div style="display: flex; align-items: center; justify-content: center; background: #e8f5e9; padding: 15px; border-radius: 8px;">
      <div style="text-align: center;">
        <p style="font-size: 2em; margin: 0; color: #2e7d32;">+18%</p>
        <p style="margin: 0; color: #666;">Growth Rate</p>
      </div>
    </div>
    <div style="display: flex; align-items: center; justify-content: center; background: #fff3e0; padding: 15px; border-radius: 8px;">
      <div style="text-align: center;">
        <p style="font-size: 2em; margin: 0; color: #ef6c00;">847</p>
        <p style="margin: 0; color: #666;">New Customers</p>
      </div>
    </div>
    <div style="position: relative; min-height: 0; min-width: 0;">
      <canvas data-chart="doughnut">
      <!--
      {
        "data": {
          "labels": ["Product A", "Product B", "Product C"],
          "datasets": [{
            "data": [40, 35, 25],
            "backgroundColor": ["#2196F3", "#4caf50", "#ff9800"]
          }]
        },
        "options": {
          "maintainAspectRatio": false,
          "plugins": {
            "legend": { "position": "bottom" }
          }
        }
      }
      -->
      </canvas>
    </div>
  </div>
</section>
```

## Why This Pattern Works

Chart.js by default maintains a 2:1 aspect ratio, which causes overflow in constrained slide layouts. The flexbox/grid pattern solves this by:

1. **`height: 100%` on section** - Makes the slide fill available space
2. **`flex: 1` on container** - Expands to fill remaining space after title
3. **`min-height: 0; min-width: 0`** - Allows flex/grid children to shrink below content size (critical for preventing overflow)
4. **`position: relative`** - Required by Chart.js for responsive sizing
5. **`maintainAspectRatio: false`** - Tells Chart.js to fill container instead of maintaining ratio

## Styling Charts

### Colors

Set colors in the JSON configuration:

```json
"datasets": [{
  "data": [12, 19, 8, 15],
  "backgroundColor": ["#2196F3", "#ff9800", "#4caf50", "#e91e63"]
}]
```

### Common color arrays for charts

```javascript
// Blues
["#1565c0", "#1976d2", "#1e88e5", "#2196f3", "#42a5f5"]

// Warm palette
["#c62828", "#ef6c00", "#f9a825", "#2e7d32", "#1565c0"]

// Grayscale
["#212121", "#424242", "#616161", "#757575", "#9e9e9e"]

// Categorical (distinct)
["#2196F3", "#ff9800", "#4caf50", "#e91e63", "#9c27b0"]
```

## Common Options

### Hide Legend

```json
"options": {
  "maintainAspectRatio": false,
  "plugins": {
    "legend": { "display": false }
  }
}
```

### Custom Axis Labels

```json
"options": {
  "maintainAspectRatio": false,
  "scales": {
    "y": {
      "title": { "display": true, "text": "Revenue ($)" }
    },
    "x": {
      "title": { "display": true, "text": "Quarter" }
    }
  }
}
```

### Start Y-Axis at Zero

```json
"options": {
  "maintainAspectRatio": false,
  "scales": {
    "y": { "beginAtZero": true }
  }
}
```

### Legend Position

```json
"options": {
  "maintainAspectRatio": false,
  "plugins": {
    "legend": { "position": "bottom" }
  }
}
```

## CSV Data Format

You can define data using CSV format (simpler than JSON):

```html
<canvas data-chart="line">
<!--
Month, Sales, Expenses
Jan, 40, 30
Feb, 50, 35
Mar, 60, 40
Apr, 55, 38
May, 70, 45
-->
</canvas>
```

The first row becomes labels, subsequent columns become datasets.

## External CSV Files

For larger datasets, use external CSV files:

```html
<canvas data-chart="line" data-chart-src="data/sales.csv">
<!--
{
  "options": {
    "maintainAspectRatio": false,
    "plugins": { "legend": { "position": "bottom" } }
  }
}
-->
</canvas>
```

## Validation

Run the overflow check script to verify charts don't overflow:

```bash
node scripts/check-overflow.js presentation.html
```

## Tips

1. **Always use the flexbox pattern** - Never set fixed height on canvas directly
2. **Always include `maintainAspectRatio: false`** in chart options
3. **Keep charts simple** - Presentations aren't dashboards
4. **Use consistent colors** - Match your presentation's color palette
5. **Limit data points** - 4-8 points is ideal for readability
6. **Test overflow** - Run `check-overflow.js` after adding charts
