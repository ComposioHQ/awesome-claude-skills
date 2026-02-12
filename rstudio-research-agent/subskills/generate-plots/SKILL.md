---
name: generate-publication-plots
description: Create publication-quality figures using ggplot2 and other R visualization libraries, with support for multiple export formats and journal-specific formatting guidelines.
---

# Generate Publication-Quality Plots

A specialized sub-skill for creating professional, publication-ready figures in R that meet journal standards and scientific visualization best practices.

## Overview

This sub-skill generates high-quality figures using `ggplot2` and other R visualization libraries. It supports multiple export formats (PDF, PNG, SVG, TIFF) and follows common journal formatting guidelines including resolution, color space, and font specifications.

Use this sub-skill when the user wants to:
- Create publication-quality figures from data
- Export plots in specific formats for journals
- Generate multi-panel composite figures
- Apply journal-specific formatting guidelines
- Create consistent figure styles across publications

---

## What This Sub-Skill Does

When invoked, this sub-skill will:

1. **Analyze data and requirements**
   - Examine data structure and variables
   - Determine appropriate plot type
   - Identify journal formatting requirements
   - Check for categorical vs continuous variables

2. **Create ggplot2 visualizations**
   - Apply theme customization
   - Use color-blind friendly palettes
   - Set appropriate figure dimensions
   - Add proper annotations and labels

3. **Export to publication formats**
   - PDF (vector format for journals)
   - PNG (raster, 300-600 DPI)
   - SVG (scalable vector graphics)
   - TIFF (high-quality raster)

4. **Follow journal guidelines**
   - Nature (single column, 89mm or 183mm width)
   - Science (specific dimensions)
   - PLOS ONE (300+ DPI TIFF/PNG)
   - IEEE (vector preferred)

---

## Supported Plot Types

| Plot Type | Description | Use Case |
|-----------|-------------|----------|
| **Scatter plots** | Point clouds with regression lines | Correlation analysis |
| **Bar plots** | Grouped, stacked, or error bars | Group comparisons |
| **Box/Violin plots** | Distribution visualization | Statistical summaries |
| **Line plots** | Time series, trends | Longitudinal data |
| **Heatmaps** | Color-coded matrices | Expression data |
| **Volcano plots** | -log10(p) vs fold change | Differential expression |
| **PCA plots** | Principal components | Dimensionality reduction |
| **Forest plots** | Effect sizes | Meta-analysis |
| **Survival curves** | Kaplan-Meier | Time-to-event data |
| **Multi-panel figures** | Combined plots | Complex results |

---

## Example User Requests

- "Create a publication-quality scatter plot with regression line"
- "Generate a volcano plot for my differential expression results"
- "Make a bar plot with error bars for Nature journal format"
- "Export this plot as 600 DPI PNG and vector PDF"
- "Create a multi-panel figure combining PCA and heatmap"

---

## Journal Formatting Guidelines

### Nature
- Single column: 89mm width
- Double column: 183mm width
- Preferred: PDF, EPS, SVG (vector)
- Minimum: 600 DPI for raster
- Fonts: Arial, Helvetica, or Symbol

### Science
- Width: 5.5cm (single) or 11.4cm (double)
- Height: Maximum 22.5cm
- Preferred: TIFF, EPS
- Resolution: 300-600 DPI
- Fonts: Helvetica or Arial

### PLOS ONE
- Width: 150-300 pixels per inch
- Preferred: TIFF, PNG, PDF
- Resolution: Minimum 300 DPI
- Color: RGB or CMYK accepted

### IEEE
- Column width: 3.5 inches (single column)
- Page width: 7.5 inches (double column)
- Preferred: PDF, EPS
- Fonts: Times New Roman, Helvetica, Arial

---

## Color Palettes

### Color-blind Friendly Palettes
```r
# Okabe-Ito palette (8 colors)
c("#E69F00", "#56B4E9", "#009E73", "#F0E442",
  "#0072B2", "#D55E00", "#CC79A7", "#999999")

# Viridis (perceptually uniform)
viridis::viridis(8)

# ColorBrewer palettes
RColorBrewer::brewer.pal(8, "Set2")
```

### Diverging Palettes
- Red-Blue (for heatmaps, volcano plots)
- RdYlBu, RdBu, BrBG

### Sequential Palettes
- Blues, Greens, PuBuGn

---

## Template Functions

### Base Publication Theme
```r
theme_publication <- function(base_size = 12, base_family = "Arial") {
  theme_bw(base_size = base_size, base_family = base_family) +
  theme(
    legend.position = "top",
    panel.border = element_rect(size = 0.5),
    panel.grid.major = element_line(color = "grey90"),
    panel.grid.minor = element_blank(),
    axis.text = element_text(size = rel(0.8)),
    legend.key = element_rect(color = "grey90"),
    legend.key.size = unit(0.4, "cm"),
    legend.margin = margin(0, 0, 0, 0, "cm")
  )
}
```

### Export Function
```r
save_publication_figure <- function(plot, filename,
                                    width = 89, height = 89,
                                    dpi = 600, units = "mm") {
  ggsave(filename, plot = plot,
         width = width, height = height,
         dpi = dpi, units = units,
         device = "pdf")
}
```

---

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `plot_type` | Type of plot to create | Required |
| `data` | Data frame for plotting | Required |
| `x_var` | Variable for x-axis | Required |
| `y_var` | Variable for y-axis | Required |
| `journal` | Target journal format | `generic` |
| `output_format` | Export format (pdf, png, svg, tiff) | `pdf` |
| `width` | Figure width in mm | `89` |
| `height` | Figure height in mm | `89` |
| `dpi` | Resolution for raster formats | `600` |
| `color_palette` | Color scheme | `Okabe-Ito` |

---

## Example Workflows

### Simple Scatter Plot
```r
# Input data: df with columns x, y, group
# Output: scatter_with_regression.pdf

p <- ggplot(df, aes(x = x, y = y, color = group)) +
  geom_point(size = 3, alpha = 0.7) +
  geom_smooth(method = "lm", se = TRUE) +
  scale_color_okabe_ito() +
  theme_publication() +
  labs(x = "X Variable", y = "Y Variable")

save_publication_figure(p, "scatter_with_regression.pdf",
                       width = 89, height = 89, dpi = 600)
```

### Volcano Plot
```r
# Input data: de_results with log2FC, pvalue
# Output: volcano.pdf

p <- ggplot(de_results, aes(x = log2FC, y = -log10(pvalue))) +
  geom_point(aes(color = significant), alpha = 0.6) +
  scale_color_manual(values = c("grey", "#D55E00", "#0072B2")) +
  theme_publication() +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed") +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed") +
  labs(x = expression(log[2]~Fold~Change),
       y = expression(-log[10]~p~value))

save_publication_figure(p, "volcano.pdf")
```

### Multi-Panel Figure
```r
# Combine multiple plots using patchwork
library(patchwork)

combined <- (p1 | p2) / (p3 | p4)

ggsave("multipanel.pdf", combined,
       width = 183, height = 183,
       dpi = 600)
```

---

## Output Specifications

### PDF (Vector)
- Recommended for journals
- Scalable without quality loss
- File extension: `.pdf`

### PNG (Raster)
- 300-600 DPI
- Good for web/PPT
- File extension: `.png`

### SVG (Vector)
- Web-friendly vector
- Editable in Inkscape/Illustrator
- File extension: `.svg`

### TIFF (Raster)
- High-quality for publication
- Lossless compression
- File extension: `.tiff`

---

## Font Options

| Font | Usage | Availability |
|------|-------|--------------|
| Arial | Most common | System font |
| Helvetica | Classic | System font |
| Times New Roman | Traditional | System font |
| CM Roman | LaTeX-style | Extrafont package |
| Latin Modern | LaTeX-style | Extrafont package |

---

## Best Practices

1. **Use vector formats when possible** - PDF for publication
2. **Check color blindness** - Use color-blind friendly palettes
3. **Maintain aspect ratio** - Avoid distorted figures
4. **Label clearly** - Self-explanatory axis labels and legends
5. **Keep it simple** - Remove chart junk and unnecessary decorations
6. **Use consistent style** - Same theme across all figures in paper
7. **Export at correct DPI** - 600 for most journals

---

## Notes

- Color-blind friendly palettes used by default
- Font family can be customized per journal requirements
- Multi-panel figures use `patchwork` package
- All plots use publication-quality theme by default
- Resolution and dimensions match common journal standards

---

## Related Sub-Skills

- **create-project**: Set up projects before creating plots
- **run-analysis**: Generate analysis results for plotting
