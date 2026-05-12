---
name: run-r-analysis
description: Execute R scripts and RMarkdown files in existing projects, handle parameterized analyses, and return results, tables, and plots.
---

# Run R Analysis

A specialized sub-skill for executing R analyses in existing research projects and generating comprehensive outputs.

## Overview

This sub-skill runs R scripts, RMarkdown documents, and Quarto reports within an existing R project structure. It captures all outputs including console results, plots, tables, and rendered reports.

Use this sub-skill when the user wants to:
- Execute an R script in a project
- Generate an R Markdown or Quarto report
- Run parameterized analyses with different inputs
- Capture and return analysis outputs

---

## What This Sub-Skill Does

When invoked, this sub-skill will:

1. **Activate project environment**
   - Load `renv` environment if present
   - Set working directory to project root
   - Source `.Rprofile` if available

2. **Execute analysis script**
   - Run specified R script
   - Capture console output
   - Track generated files
   - Monitor for errors and warnings

3. **Generate reports**
   - Render R Markdown to HTML/PDF
   - Render Quarto documents
   - Include all figures and tables
   - Return rendered report path

4. **Return results**
   - Console output and messages
   - Paths to generated files
   - Summary statistics
   - Error messages if any

---

## Example User Requests

- "Run `analysis.R` and show me the results"
- "Execute the differential expression analysis in my RNA-seq project"
- "Render the report and return the HTML file"
- "Run the analysis with different parameters"
- "Generate all plots from my analysis script"

---

## Supported File Types

| File Type | Execution Method | Output |
|-----------|------------------|--------|
| `.R` scripts | `source()` | Console output + generated files |
| `.Rmd` | `rmarkdown::render()` | HTML/PDF/Word document |
| `.qmd` | `quarto::quarto_render()` | HTML/PDF/Word document |
| Parameterized scripts | `with parameters` | Multiple outputs |

---

## Execution Workflow

```
1. Verify project structure exists
   ↓
2. Activate renv environment (if present)
   ↓
3. Load required packages
   ↓
4. Execute analysis script
   ↓
5. Capture outputs
   ↓
6. Return results summary
```

---

## Output Handling

### Console Output
All print statements, messages, and warnings are captured and returned.

### Generated Files
- **Figures**: `results/figures/*.pdf`, `*.png`, `*.svg`
- **Tables**: `results/tables/*.csv`, `*.tsv`
- **Models**: `results/models/*.rds`
- **Reports**: `reports/*.html`, `*.pdf`

### Error Handling
- Script errors are reported with line numbers
- Missing packages are identified
- File path issues are diagnosed
- Suggestions for fixes are provided

---

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `script_path` | Path to R script or Rmd file | Required |
| `working_dir` | Project root directory | Current directory |
| `render_report` | Also render Rmd/qmd if present | `true` |
| `output_format` | Report format (html, pdf, all) | `html` |
| `params` | Named list for parameterized reports | `NULL` |

---

## Example Usage

### Basic Script Execution

**User:** Run the analysis script in my project.

**Skill actions:**
```r
# Set working directory
setwd("my-project")

# Activate renv
renv::activate()

# Source analysis script
source("scripts/01_analysis.R")

# Report outputs
# - results/tables/statistics.csv created
# - results/figures/pca_plot.pdf created
# - results/models/regression_model.rds created
```

### Parameterized Report

**User:** Run the report with dataset='variant2'.

**Skill actions:**
```r
rmarkdown::render(
  "reports/report.Rmd",
  params = list(dataset = "variant2"),
  output_format = "html_document"
)
# Output: reports/report_variant2.html
```

### Quarto Report

**User:** Render the Quarto document to PDF.

**Skill actions:**
```r
quarto::quarto_render(
  "reports/analysis.qmd",
  output_format = "pdf"
)
# Output: reports/analysis.pdf
```

---

## Common Output Patterns

| Analysis Type | Expected Outputs |
|--------------|------------------|
| Differential Expression | Volcano plots, MA plots, DEG tables |
| PCA | PCA plots, loadings, explained variance |
| Clustering | Dendrograms, heatmaps, cluster assignments |
| Regression | Diagnostic plots, coefficient tables, predictions |
| Time Series | Forecast plots, residuals, accuracy metrics |

---

## Notes

- Working directory is always set to project root
- Relative paths in scripts work correctly
- `renv` ensures correct package versions
- All outputs are tracked and reported
- Long-running scripts show progress updates

---

## Related Sub-Skills

- **create-project**: Set up new projects before running analyses
- **debug-env**: Troubleshoot environment issues before execution
