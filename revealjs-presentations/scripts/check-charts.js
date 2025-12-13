#!/usr/bin/env node

/**
 * Validates chart configurations in a reveal.js presentation.
 * Checks for valid JSON syntax and required properties.
 *
 * Usage: node check-charts.js <path-to-html>
 */

const fs = require('fs');
const path = require('path');
const cheerio = require('cheerio');

const VALID_CHART_TYPES = ['line', 'bar', 'pie', 'doughnut', 'radar', 'polarArea', 'bubble', 'scatter'];

function extractCharts(html) {
  const $ = cheerio.load(html);
  const charts = [];

  $('canvas[data-chart]').each((index, element) => {
    const $el = $(element);
    const chartType = $el.attr('data-chart');
    const externalSrc = $el.attr('data-chart-src') || null;

    // Get the raw HTML content inside the canvas to extract the comment
    const innerHtml = $el.html() || '';

    // Extract JSON/CSV from HTML comment
    const commentMatch = innerHtml.match(/<!--([\s\S]*?)-->/);
    const configText = commentMatch ? commentMatch[1].trim() : null;

    // Calculate line number by finding position in original HTML
    // Get the outer HTML and find it in the source
    const outerHtml = $.html(element);
    const position = html.indexOf(outerHtml.substring(0, 50));
    const lineNumber = position >= 0
      ? (html.substring(0, position).match(/\n/g) || []).length + 1
      : -1;

    charts.push({
      type: chartType,
      configText,
      externalSrc,
      lineNumber,
      preview: outerHtml.substring(0, 80) + '...'
    });
  });

  return charts;
}

function validateChart(chart, index) {
  const errors = [];
  const warnings = [];
  const lineInfo = chart.lineNumber > 0 ? `line ${chart.lineNumber}` : 'unknown line';
  const prefix = `Chart ${index + 1} (${lineInfo}, type: ${chart.type})`;

  // Check chart type
  if (!VALID_CHART_TYPES.includes(chart.type)) {
    errors.push(`${prefix}: Invalid chart type '${chart.type}'. Valid types: ${VALID_CHART_TYPES.join(', ')}`);
  }

  // If there's no config and no external source, that's an error
  if (!chart.configText && !chart.externalSrc) {
    errors.push(`${prefix}: No chart configuration found. Add JSON in HTML comment or use data-chart-src attribute.`);
    return { errors, warnings };
  }

  // If using external source, just note it
  if (chart.externalSrc) {
    warnings.push(`${prefix}: Uses external data source '${chart.externalSrc}' - ensure file exists`);
  }

  // If there's config text, try to parse it
  if (chart.configText) {
    // Check if it looks like CSV (no opening brace)
    const trimmed = chart.configText.trim();
    if (!trimmed.startsWith('{')) {
      // Looks like CSV data - basic validation
      const lines = trimmed.split('\n').filter(l => l.trim());
      if (lines.length < 2) {
        errors.push(`${prefix}: CSV data should have at least a header row and one data row`);
      } else {
        const headerCols = lines[0].split(',').length;
        for (let i = 1; i < lines.length; i++) {
          const dataCols = lines[i].split(',').length;
          if (dataCols !== headerCols) {
            warnings.push(`${prefix}: CSV row ${i + 1} has ${dataCols} columns, header has ${headerCols}`);
          }
        }
      }
    } else {
      // Try to parse as JSON
      try {
        const config = JSON.parse(trimmed);

        // Check for required properties
        if (!config.data && !chart.externalSrc) {
          errors.push(`${prefix}: Missing required 'data' property in chart configuration`);
        }

        if (config.data) {
          // Check for labels (required for most chart types)
          if (!config.data.labels && !['scatter', 'bubble'].includes(chart.type)) {
            warnings.push(`${prefix}: Missing 'data.labels' - chart may not display correctly`);
          }

          // Check for datasets
          if (!config.data.datasets || !Array.isArray(config.data.datasets)) {
            errors.push(`${prefix}: Missing or invalid 'data.datasets' array`);
          } else if (config.data.datasets.length === 0) {
            errors.push(`${prefix}: 'data.datasets' array is empty`);
          } else {
            // Check each dataset
            config.data.datasets.forEach((dataset, i) => {
              if (!dataset.data && !chart.externalSrc) {
                errors.push(`${prefix}: Dataset ${i + 1} is missing 'data' property`);
              }
            });
          }
        }

        // Check for maintainAspectRatio: false (recommended)
        if (!config.options || config.options.maintainAspectRatio !== false) {
          warnings.push(`${prefix}: Missing 'options.maintainAspectRatio: false' - chart may overflow`);
        }
      } catch (e) {
        errors.push(`${prefix}: Invalid JSON syntax - ${e.message}`);

        // Try to give helpful hints
        if (e.message.includes('Unexpected token')) {
          errors.push(`  Hint: Check for missing commas, quotes, or brackets`);
        }
      }
    }
  }

  return { errors, warnings };
}

function main() {
  const htmlPath = process.argv[2];

  if (!htmlPath) {
    console.error('Usage: node check-charts.js <path-to-html>');
    process.exit(1);
  }

  if (!fs.existsSync(htmlPath)) {
    console.error(`Error: File not found: ${htmlPath}`);
    process.exit(1);
  }

  const html = fs.readFileSync(htmlPath, 'utf-8');
  const charts = extractCharts(html);

  console.log(`Checking charts in: ${htmlPath}\n`);

  if (charts.length === 0) {
    console.log('No charts found in presentation.');
    return;
  }

  console.log(`Found ${charts.length} chart(s)\n`);

  let totalErrors = 0;
  let totalWarnings = 0;

  charts.forEach((chart, index) => {
    const { errors, warnings } = validateChart(chart, index);

    if (errors.length === 0 && warnings.length === 0) {
      console.log(`✓ Chart ${index + 1} (line ${chart.lineNumber}, type: ${chart.type}): OK`);
    } else {
      if (errors.length > 0) {
        errors.forEach(e => console.log(`✗ ${e}`));
        totalErrors += errors.length;
      }
      if (warnings.length > 0) {
        warnings.forEach(w => console.log(`⚠ ${w}`));
        totalWarnings += warnings.length;
      }
    }
  });

  console.log(`\n${'─'.repeat(50)}`);
  console.log(`Total: ${charts.length} charts, ${totalErrors} errors, ${totalWarnings} warnings`);

  if (totalErrors > 0) {
    process.exit(1);
  }
}

main();
