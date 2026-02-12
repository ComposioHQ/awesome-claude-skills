---
name: rstudio-research-agent
description: Interact with R and RStudio environments for scientific research tasks including creating projects, running analyses, managing dependencies, and generating publication-quality plots.
---

# RStudio Research Agent

A comprehensive skill for R-based research workflow automation. This skill enables interaction with R and RStudio environments for scientific computing, statistical analysis, bioinformatics, and data visualization.

## When to Use This Skill

- Create a new R project with standard structure for scientific research
- Run R analyses on existing projects and generate reports
- Troubleshoot R package dependencies and environment issues
- Generate publication-quality plots and statistical visualizations
- Set up reproducible R workflows with renv package management

## What This Skill Does

1. **Create R Research Projects**: Scaffold new R projects with standard folder structure, Git initialization, renv package management, template scripts, and RStudio project files.

2. **Run Analyses**: Execute R scripts, RMarkdown, and Quarto documents with full output capture, parameterized analysis support, and report generation.

3. **Debug Environment**: Check for missing packages, resolve library conflicts, verify R version compatibility, and generate installation commands.

4. **Generate Publication-Quality Plots**: Create figures with ggplot2, export to multiple formats, follow journal-specific formatting guidelines, and support multi-panel composite figures with color-blind friendly palettes.

## How to Use

### Basic Usage

```
Create a new R project for gene expression analysis
```

```
Run the analysis script in my R project and show results
```

```
Check if all required R packages are installed
```

### Advanced Usage

```
Create a new R project for RNA-seq differential expression analysis with Git initialized and set up renv with DESeq2, tidyverse, and ggplot2
```

```
Run scripts/deseq2_analysis.R and generate a PDF report with all volcano plots and heatmaps
```

```
Debug my R environment - packages won't load. Check what's missing and provide installation commands.
```

## Example

**User**: "Create a new R project for my genomics data analysis"

**Skill creates**:
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

Then initializes Git, sets up renv, and installs common packages (tidyverse, ggplot2, DESeq2).

## Tips

- Use `renv::snapshot()` after installing new packages to lock versions
- Never modify raw data files - always work on copies in `data/processed/`
- Script everything to avoid interactive-only analysis
- Save all outputs (plots, tables, model objects) to files
- Use Quarto or R Markdown for reproducible reports

## Common Use Cases

- Genomics and bioinformatics analysis (RNA-seq, differential expression)
- Statistical analysis and modeling (linear models, survival analysis)
- Data visualization and figure generation for publications
- Clinical trial data analysis and reporting
- Time series analysis and forecasting
- Multivariate statistics and PCA analysis

---

**Requirements**: R >= 4.0.0, renv package

**Common Packages Used**: tidyverse, ggplot2, rmarkdown, quarto, DESeq2, edgeR, limma, lme4, survival, broom
