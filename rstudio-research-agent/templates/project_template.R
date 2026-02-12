# ============================================================================
# R Project Initialization Script
# ============================================================================
# This script sets up a new R research project with proper directory structure
# and package management using renv.
#
# Usage: Run this script at the start of a new project
# ============================================================================

# Setup message
message("Setting up R research project...")

# Create directory structure
dirs <- c(
  "data/raw",
  "data/processed",
  "scripts",
  "results/figures",
  "results/tables",
  "results/models",
  "reports",
  "docs"
)

for (dir in dirs) {
  if (!dir.exists(dir)) {
    dir.create(dir, recursive = TRUE)
    message("Created directory: ", dir)
  }
}

# Create .gitkeep files for empty directories
gitkeep_dirs <- c(
  "data/raw/.gitkeep",
  "data/processed/.gitkeep",
  "results/figures/.gitkeep",
  "results/tables/.gitkeep",
  "results/models/.gitkeep",
  "reports/.gitkeep"
)

for (file in gitkeep_dirs) {
  if (!file.exists(file)) {
    write("", file = file)
  }
}

# Initialize renv if not already initialized
if (!file.exists("renv.lock")) {
  if (interactive()) {
    response <- readline("Initialize renv for package management? (y/n): ")
    if (tolower(response) == "y") {
      renv::init()
      message("renv initialized. Remember to snapshot your packages:")
      message("  renv::snapshot()")
    }
  } else {
    renv::init()
    message("renv initialized. Remember to snapshot your packages:")
    message("  renv::snapshot()")
  }
}

# Create .Rproj file if using RStudio
if (!file.exists(paste0(getwd(), ".Rproj"))) {
  if (requireNamespace("rstudioapi", quietly = TRUE) && rstudioapi::isAvailable()) {
    rstudioapi::createProject(getwd())
    message("Created RStudio project file")
  }
}

# Create a basic README
if (!file.exists("README.md")) {
  readme_content <- c(
    "# Project Title",
    "",
    "## Description",
    "",
    "Brief description of the research project.",
    "",
    "## Project Structure",
    "",
    "```",
    ".",
    "|-- data/",
    "|   |-- raw/           # Original, immutable data",
    "|   |-- processed/     # Cleaned, transformed data",
    "|-- scripts/           # Analysis scripts",
    "|-- results/",
    "|   |-- figures/       # Plots and visualizations",
    "|   |-- tables/        # Summary tables",
    "|   |-- models/        # Saved model objects",
    "|-- reports/           # R Markdown/Quarto reports",
    "|-- docs/              # Additional documentation",
    "```",
    "",
    "## Setup",
    "",
    "```r",
    "# Install and activate renv",
    "renv::restore()",
    "```",
    "",
    "## Usage",
    "",
    "## References",
    ""
  )
  writeLines(readme_content, "README.md")
  message("Created README.md")
}

message("\n=== Project setup complete! ===")
message("\nNext steps:")
message("1. Add your data to data/raw/")
message("2. Create analysis scripts in scripts/")
message("3. Use renv::install() to add required packages")
message("4. Run renv::snapshot() to save your package state")
