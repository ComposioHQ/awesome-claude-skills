---
name: create-r-project
description: Create a new R research project with standard folder structure, Git initialization, renv package management, and template scripts.
---

# Create R Research Project

A specialized sub-skill for scaffolding new R research projects with reproducible structure and best practices.

## Overview

This sub-skill creates a complete, production-ready R project structure suitable for scientific research, statistical analysis, bioinformatics, and data visualization.

Use this sub-skill when the user wants to:
- Create a new R project from scratch
- Set up a reproducible research workflow
- Initialize Git for version control
- Generate analysis template scripts

---

## What This Sub-Skill Does

When invoked, this sub-skill will:

1. **Create directory structure**
   - `data/raw/` - Original, immutable data files
   - `data/processed/` - Cleaned, transformed data
   - `scripts/` - Analysis and processing scripts
   - `results/figures/` - Plots and visualizations
   - `results/tables/` - Summary tables
   - `results/models/` - Saved model objects (.rds files)
   - `reports/` - R Markdown/Quarto documents

2. **Initialize version control**
   - Create `.gitignore` with R-specific patterns
   - Initialize Git repository (if requested)
   - Create initial commit with project structure

3. **Set up package management**
   - Initialize `renv` for reproducible R environments
   - Create `renv.lock` file
   - Generate `.Rprofile` for automatic renv activation

4. **Create RStudio project**
   - Generate `.Rproj` file for RStudio integration
   - Configure project options

5. **Generate template files**
   - Analysis script template (`scripts/01_analysis.R`)
   - R Markdown report template (`reports/report.Rmd`)
   - README.md with project documentation
   - `.gitignore` for R projects

---

## Example User Requests

- "Create a new R project for genomics analysis"
- "Set up an R research project with Git"
- "Initialize an R project for differential expression analysis"
- "Create an R workflow for statistical modeling"

---

## Generated Templates

### Analysis Script (`scripts/01_analysis.R`)

```r
# Load libraries
library(tidyverse)
# Add required packages

# Load data
raw_data <- read_csv("data/raw/input.csv")

# Process data
processed_data <- raw_data %>%
  # Add processing steps
  mutate()

# Save processed data
write_csv(processed_data, "data/processed/cleaned.csv")

# Analysis
results <- processed_data %>%
  # Add analysis code
  summarize()

# Save results
write_csv(results, "results/tables/results.csv")

# Generate plots
g <- ggplot(processed_data, aes()) +
  geom_point() +
  theme_minimal()

ggsave("results/figures/plot1.pdf", g, width = 6, height = 4)
```

### R Markdown Report (`reports/report.Rmd`)

```markdown
---
title: "Analysis Report"
output: html_document
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(echo = TRUE)
library(tidyverse)
```

## Methods

Describe your analysis methods here.

## Results

```{r results}
# Load and display results
results <- read_csv("results/tables/results.csv")
results
```

## Figures

```{r figures}
# Include generated figures
knitr::include_graphics("results/figures/plot1.pdf")
```
```

---

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `project_name` | Name of the project directory | Required |
| `init_git` | Initialize Git repository | `false` |
| `create_rproj` | Create RStudio project file | `true` |
| `init_renv` | Initialize renv environment | `true` |
| `project_type` | Type of project (general, bioinformatics, statistics) | `general` |

---

## Notes

- Project follows standard R research project conventions
- `renv.lock` ensures reproducible package versions
- `.gitignore` excludes sensitive data and compiled files
- All scripts use relative paths for portability

---

## Related Sub-Skills

- **run-analysis**: Execute analyses in created projects
- **debug-env**: Set up and troubleshoot R environments
