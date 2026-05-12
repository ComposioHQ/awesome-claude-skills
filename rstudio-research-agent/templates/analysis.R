# ============================================================================
# Analysis Script Template
# ============================================================================
# Description: [Brief description of what this analysis does]
# Author: [Your name]
# Date: [Date]
# Input: data/raw/[input_file]
# Output: results/[output_files]
# ============================================================================

# Load libraries --------------------------------------------------------------
library(tidyverse)
library(here)

# Set options -----------------------------------------------------------------
options(scipen = 999)  # Disable scientific notation

# Define paths ----------------------------------------------------------------
DATA_RAW <- here("data/raw")
DATA_PROCESSED <- here("data/processed")
RESULTS_FIGURES <- here("results/figures")
RESULTS_TABLES <- here("results/tables")
RESULTS_MODELS <- here("results/models")

# Load data -------------------------------------------------------------------
# df <- read_csv(file.path(DATA_RAW, "filename.csv"))

# Data preparation ------------------------------------------------------------
# Clean and transform data here

# Analysis --------------------------------------------------------------------
# Perform your analysis here

# Visualization ---------------------------------------------------------------
# Create plots with ggplot2

# Save results ----------------------------------------------------------------
# ggsave(file.path(RESULTS_FIGURES, "figure1.png"), ...)

# Session info (for reproducibility) -----------------------------------------
sessionInfo()
