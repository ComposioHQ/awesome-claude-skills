# RStudio Research Agent

A Claude Code skill for comprehensive R-based research workflow automation. This skill enables Claude to interact with R and RStudio environments for scientific research tasks.

## Features

- **Create R Research Projects** - Scaffold new R projects with standard folder structure, Git initialization, and `renv` package management
- **Run Analyses** - Execute R scripts, RMarkdown, and Quarto documents with full output capture
- **Debug Environment** - Check for missing packages, resolve conflicts, and verify R version compatibility
- **Generate Publication-Quality Plots** - Create professional figures with journal-specific formatting guidelines
- **Generate Reports** - Create professional reports using RMarkdown and Quarto

## Quick Start

Invoke the skill by asking Claude to work with R:

```
Create a new R project for gene expression analysis
```

```
Run the analysis script in my R project and show results
```

```
Check if all required R packages are installed
```

```
Generate a volcano plot with Nature journal formatting
```

```
Create a scatter plot from my dataset and export as PDF
```

## Project Structure

Projects created by this skill follow standardized structure:

```
my-research-project/
├── data/
│   ├── raw/               # Original, immutable data files
│   └── processed/         # Cleaned, transformed data
├── scripts/               # Analysis and processing scripts
├── results/
│   ├── figures/           # Plots and visualizations
│   ├── tables/            # Summary tables
│   └── models/            # Saved model objects (.rds files)
├── reports/               # R Markdown/Quarto documents
├── renv.lock              # Package version lock file
├── .Rproj                 # RStudio project file
└── README.md              # Project documentation
```

## Sub-Skills

### create-project
Scaffold new R research projects with:
- Standard directory structure
- Git initialization (optional)
- `renv` package management
- Template scripts and reports
- RStudio project file

### run-analysis
Execute R analyses with:
- Script execution and output capture
- RMarkdown/Quarto rendering
- Parameterized analysis support
- Results and plot tracking

### debug-env
Troubleshoot R environments:
- Missing package detection
- Dependency resolution
- Version conflict diagnosis
- Installation command generation

### generate-plots
Create publication-quality figures with:
- Scatter, bar, box, volcano, heatmap plots
- Journal-specific formatting (Nature, Science, PLOS ONE, IEEE)
- Export to PDF/PNG/SVG/TIFF formats
- Multi-panel composite figures
- Color-blind friendly palettes

## Supported Analyses

| Type | Packages |
|------|----------|
| Data wrangling | tidyverse, data.table |
| Visualization | ggplot2, patchwork, scales |
| Statistics | stats, lme4, survival, broom |
| Bioinformatics | Bioconductor (DESeq2, edgeR, limma) |
| Reporting | rmarkdown, quarto |
| Reproducibility | renv |

## Requirements

- R >= 4.0.0
- `renv` package: `install.packages("renv")`
- (Optional) RStudio for `.Rproj` support
- (Optional) Quarto CLI for advanced reports

## Templates Included

| Template | Description |
|----------|-------------|
| `project_template.R` | Complete project initialization script |
| `analysis.R` | Standard analysis script template |
| `report.qmd` | Quarto report template |
| `renv.lock.example` | Example package lock file |
| `plot_functions.R` | Publication-quality plotting functions library |
| `plot_examples.R` | Example plots (scatter, bar, volcano, heatmap, etc.) |

## Usage Examples

### Create a New Project

```
Create an R project for RNA-seq differential expression analysis with Git
```

### Run Analysis

```
Run scripts/deseq2_analysis.R and return the summary table
```

### Debug Environment

```
My script fails with "package not found" - check what's missing
```

### Generate Report

```
Render the Quarto report to PDF with all figures
```

### Generate Publication Plots

```
Create a volcano plot with Nature journal formatting
```

```
Generate a scatter plot with regression line and export as PDF
```

```
Make a multi-panel figure combining PCA and heatmap
```

## Best Practices

1. **Never modify raw data** - Always work on copies in `data/processed/`
2. **Use `renv::snapshot()`** after installing new packages
3. **Script everything** - Avoid interactive-only analysis
4. **Save all outputs** - Plots, tables, and model objects
5. **Document with reports** - Use Quarto/R Markdown for reproducibility

## License

MIT

## Contributing

Suggestions and improvements welcome! This skill is designed to be a template for reproducible R research workflows.
