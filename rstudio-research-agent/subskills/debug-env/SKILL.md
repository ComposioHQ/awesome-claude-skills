---
name: debug-r-env
description: Check for missing R packages, resolve library conflicts, verify R version compatibility, and suggest fixes for environment issues.
---

# Debug R Environment

A specialized sub-skill for troubleshooting and fixing R environment issues including missing packages, version conflicts, and configuration problems.

## Overview

This sub-skill diagnoses and resolves common R environment problems that prevent scripts from running correctly. It analyzes R installations, package dependencies, and system configurations.

Use this sub-skill when the user wants to:
- Check if required packages are installed
- Resolve package version conflicts
- Fix "package not found" errors
- Verify R version compatibility
- Debug library path issues
- Troubleshoot compilation failures

---

## What This Sub-Skill Does

When invoked, this sub-skill will:

1. **Analyze R environment**
   - Check R version and platform
   - List installed packages and versions
   - Examine library paths
   - Verify package dependencies

2. **Identify missing packages**
   - Scan scripts for `library()` and `require()` calls
   - Check for Bioconductor packages
   - Detect GitHub package dependencies
   - Identify version mismatches

3. **Diagnose conflicts**
   - Find package masking issues
   - Detect incompatible versions
   - Identify system dependencies
   - Check compilation requirements

4. **Provide solutions**
   - Generate installation commands
   - Suggest version updates
   - Recommend renv initialization
   - Provide troubleshooting steps

---

## Example User Requests

- "My R script says 'package not found'"
- "Check if all packages for RNA-seq analysis are installed"
- "Fix my R environment - ggplot2 won't load"
- "Why is DESeq2 throwing an error?"
- "Debug the package dependencies in my project"
- "Install all required packages for my analysis"

---

## Diagnostic Checks

### Environment Scan
```r
# R version and platform
version
R.version.string

# Library paths
.libPaths()

# Installed packages
installed.packages()[,c("Package", "Version")]

# Package conflicts
sessionInfo()
conflicts()
```

### Missing Package Detection
```r
# Scan scripts for library() calls
grep("library\\(|require\\(", scripts, value = TRUE)

# Check if packages are installed
is_installed <- function(pkg) {
  require(pkg, quietly = TRUE, character.only = TRUE)
}
```

### Dependency Resolution
```r
# Check package dependencies
tools::package_dependencies()

# Verify installation
packageVersion("ggplot2")

# Check for updates
old.packages()
```

---

## Common Issues and Solutions

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| "there is no package called" | Package not installed | `install.packages("pkgname")` |
| Bioconductor package not found | Bioconductor not configured | `BiocManager::install("pkgname")` |
| Package masked by another | Namespace conflict | `library(pkgname)` explicitly |
| Compilation error | Missing system dependencies | Install system build tools |
| Version mismatch | Package requires newer R | Update R or use older package |
| renv activation fails | Corrupted lock file | Delete and restore `renv.lock` |

---

## Installation Command Generator

For different package sources, this sub-skill generates appropriate commands:

### CRAN Packages
```r
install.packages("package_name")
```

### Bioconductor Packages
```r
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("package_name")
```

### GitHub Packages
```r
remotes::install_github("username/package")
# or
devtools::install_github("username/package")
```

### Multiple Packages
```r
packages <- c("tidyverse", "ggplot2", "dplyr")
install.packages(packages)
```

---

## Analysis-Specific Package Lists

### Differential Expression
- DESeq2
- edgeR
- limma
- EnhancedVolcano
- pheatmap

### Statistical Modeling
- lme4
- broom
- car
- emmeans
- multcomp

### Data Visualization
- ggplot2
- patchwork
- scales
- cowplot
- viridis

### Bioinformatics
- Biostrings
- GenomicRanges
- biomaRt
- AnnotationDbi

---

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `script_path` | Path to R script to analyze | Current directory |
| `required_packages` | List of packages to verify | Auto-detect from scripts |
| `check_bioc` | Check Bioconductor packages | `true` |
| `check_updates` | Check for available updates | `false` |
| `fix_issues` | Attempt to install missing packages | `false` |

---

## Diagnostic Report Example

```
=== R Environment Diagnostic Report ===

R Version: 4.3.2 (2023-10-31)
Platform: x86_64-pc-linux-gnu
Library Path: /home/user/R/x86_64-pc-linux-gnu-library/4.3

--- Installed Packages ---
tidyverse    2.0.0  ✓
ggplot2      3.4.4  ✓
dplyr        1.1.3  ✓

--- Missing Packages ---
DESeq2       ✗     (Bioconductor required)
EnhancedVolcano ✗   (CRAN)
pheatmap     ✗     (CRAN)

--- Installation Commands ---
if (!requireNamespace("BiocManager", quietly = TRUE))
    install.packages("BiocManager")
BiocManager::install("DESeq2")
install.packages(c("EnhancedVolcano", "pheatmap"))

--- Warnings ---
- R 4.3.2 detected; some packages may require R >= 4.4.0
- renv not initialized; consider running renv::init()
```

---

## Notes

- Always checks both CRAN and Bioconductor sources
- Respects `renv.lock` if present in project
- Provides safe installation commands (review before running)
- Detects system dependencies for compilation
- Checks for package masking conflicts

---

## Related Sub-Skills

- **create-project**: Set up new projects with proper environment
- **run-analysis**: Execute scripts after fixing environment issues
