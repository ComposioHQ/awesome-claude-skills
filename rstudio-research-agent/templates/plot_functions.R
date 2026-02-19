# ============================================================================
# Publication-Quality Plot Functions
# ============================================================================
# Description: Collection of functions for creating publication-ready plots
# Author: [Your name]
# Date: [Date]
# ============================================================================

# Required libraries ----------------------------------------------------------
library(ggplot2)
library(scales)
library(patchwork)

# Color-blind friendly palettes ---------------------------------------------
# Okabe-Ito palette (recommended for publications)
okabe_ito <- c(
  "#E69F00", # Orange
  "#56B4E9", # Sky blue
  "#009E73", # Bluish green
  "#F0E442", # Yellow
  "#0072B2", # Blue
  "#D55E00", # Vermillion
  "#CC79A7", # Reddish purple
  "#999999"  # Grey
)

# Diverging palette for heatmaps/volcano plots
diverging_palette <- c("#D55E00", "#F0E442", "#999999", "#56B4E9", "#0072B2")

# ============================================================================
# Publication Theme
# ============================================================================

#' Publication-Ready ggplot2 Theme
#'
#' Creates a clean, publication-quality theme for ggplot2 figures
#' following common journal guidelines.
#'
#' @param base_size Base font size in points
#' @param base_family Base font family (Arial recommended for publications)
#' @return A ggplot theme object
#'
#' @examples
#' ggplot(mtcars, aes(x = wt, y = mpg)) +
#'   geom_point() +
#'   theme_publication()
theme_publication <- function(base_size = 12, base_family = "Arial") {
  theme_bw(base_size = base_size, base_family = base_family) +
  theme(
    # Legend placement
    legend.position = "top",
    legend.title = element_text(size = rel(1)),
    legend.text = element_text(size = rel(0.9)),
    legend.key.size = unit(0.4, "cm"),
    legend.margin = margin(0, 0, 0, 0, "cm"),
    legend.box.margin = margin(0, 0, -5, 0, "mm"),

    # Panel borders
    panel.border = element_rect(size = 0.5, color = "black"),
    panel.grid.major = element_line(color = "grey90", linewidth = 0.25),
    panel.grid.minor = element_blank(),

    # Axis text
    axis.text = element_text(size = rel(0.9), color = "black"),
    axis.title = element_text(size = rel(1)),

    # Plot elements
    plot.title = element_text(size = rel(1.2), hjust = 0.5),

    # Strip text for facets
    strip.background = element_rect(color = "black", fill = "grey90"),
    strip.text = element_text(size = rel(0.9))
  )
}

# ============================================================================
# Scale Functions
# ============================================================================

#' Okabe-Ito Color Scale
#'
#' Applies the color-blind friendly Okabe-Ito palette
#'
#' @param palette Number of colors to use (1-8)
#'
scale_color_okabe_ito <- function(palette = 8) {
  discrete_scale("colour", "okabe_ito",
                 function(n) okabe_ito[1:min(n, 8)])
}

scale_fill_okabe_ito <- function(palette = 8) {
  discrete_scale("fill", "okabe_ito",
                 function(n) okabe_ito[1:min(n, 8)])
}

# ============================================================================
# Export Functions
# ============================================================================

#' Save Publication-Quality Figure
#'
#' Exports a ggplot object to publication-ready formats with proper
#' dimensions and resolution.
#'
#' @param plot ggplot object to save
#' @param filename Output filename (without extension)
#' @param path Output directory path
#' @param width Width in mm
#' @param height Height in mm
#' @param dpi Resolution for raster formats (default: 600)
#' @param formats Vector of formats: c("pdf", "png", "svg", "tiff")
#'
#' @examples
#' p <- ggplot(mtcars, aes(x = wt, y = mpg)) + geom_point()
#' save_publication_figure(p, "scatter_plot",
#'                         width = 89, height = 89,
#'                         formats = c("pdf", "png"))
save_publication_figure <- function(plot,
                                    filename,
                                    path = "results/figures",
                                    width = 89,
                                    height = 89,
                                    dpi = 600,
                                    formats = c("pdf")) {

  # Create output directory if needed
  if (!dir.exists(path)) {
    dir.create(path, recursive = TRUE)
  }

  # Export in each requested format
  for (fmt in formats) {
    filepath <- file.path(path, paste0(filename, ".", fmt))

    ggsave(filepath, plot = plot,
           width = width, height = height,
           units = "mm", dpi = dpi,
           device = fmt)

    message("Saved: ", filepath)
  }
}

# ============================================================================
# Specific Plot Functions
# ============================================================================

#' Create Scatter Plot with Regression
#'
#' @param data Data frame
#' @param x x-axis variable
#' @param y y-axis variable
#' @param color Color/group variable (optional)
#' @param add_regression Add regression line
#' @param show_ci Show confidence interval
#'
create_scatter_plot <- function(data, x, y, color = NULL,
                                add_regression = TRUE, show_ci = TRUE) {
  x_sym <- enquo(x)
  y_sym <- enquo(y)

  p <- ggplot(data, aes(x = !!x_sym, y = !!y_sym))

  if (is.null(color)) {
    p <- p + geom_point(size = 3, alpha = 0.7)
    if (add_regression) {
      if (show_ci) {
        p <- p + geom_smooth(method = "lm", se = TRUE, color = "black")
      } else {
        p <- p + geom_smooth(method = "lm", se = FALSE, color = "black")
      }
    }
  } else {
    color_sym <- enquo(color)
    p <- p + geom_point(aes_string(color = color), size = 3, alpha = 0.7) +
      scale_color_okabe_ito()
    if (add_regression) {
      if (show_ci) {
        p <- p + geom_smooth(aes_string(color = color),
                            method = "lm", se = TRUE)
      } else {
        p <- p + geom_smooth(aes_string(color = color),
                            method = "lm", se = FALSE)
      }
    }
  }

  p + theme_publication()
}

#' Create Bar Plot with Error Bars
#'
#' @param data Data frame
#' @param x x-axis variable (categorical)
#' @param y y-axis variable (numeric)
#' @param fill Fill variable (optional)
#' @param error_var Error bar variable (optional)
#'
create_bar_plot <- function(data, x, y, fill = NULL, error_var = NULL) {
  x_sym <- enquo(x)
  y_sym <- enquo(y)

  p <- ggplot(data, aes(x = !!x_sym, y = !!y_sym, group = !!x_sym))

  if (is.null(fill)) {
    p <- p + geom_bar(stat = "identity", fill = okabe_ito[1], width = 0.7)
  } else {
    fill_sym <- enquo(fill)
    p <- p + geom_bar(aes_string(fill = fill),
                      stat = "identity", width = 0.7, position = "dodge") +
      scale_fill_okabe_ito()
  }

  if (!is.null(error_var)) {
    p <- p + geom_errorbar(aes_string(ymin = paste0(y, "-", error_var),
                                      ymax = paste0(y, "+", error_var)),
                          width = 0.2)
  }

  p + theme_publication() +
    labs(y = deparse(substitute(y)), x = deparse(substitute(x)))
}

#' Create Volcano Plot
#'
#' @param data Data frame with log2FC and p-value columns
#' @param logfc Column name for log2 fold change
#' @param pval Column name for p-value
#' @param fc_threshold Fold change threshold
#' @param p_threshold P-value threshold
#'
create_volcano_plot <- function(data, logfc = "log2FC", pval = "pvalue",
                                 fc_threshold = 1, p_threshold = 0.05) {
  # Calculate -log10(p-value)
  data <- data %>%
    mutate(neglog10p = -log10(!!sym(pval)),
           significance = case_when(
             abs(!!sym(logfc)) >= fc_threshold & !!sym(pval) < p_threshold ~ "Up",
             abs(!!sym(logfc)) >= fc_threshold & !!sym(pval) < p_threshold ~ "Down",
             TRUE ~ "NS"
           ))

  p <- ggplot(data, aes(x = !!sym(logfc), y = neglog10p)) +
    geom_point(aes(color = significance), alpha = 0.6, size = 1.5) +
    scale_color_manual(values = c("Down" = "#0072B2",
                                   "NS" = "#999999",
                                   "Up" = "#D55E00"),
                       name = "") +
    geom_vline(xintercept = c(-fc_threshold, fc_threshold),
               linetype = "dashed", color = "grey50") +
    geom_hline(yintercept = -log10(p_threshold),
               linetype = "dashed", color = "grey50") +
    theme_publication() +
    labs(x = expression(log[2]~Fold~Change),
         y = expression(-log[10]~P~Value))

  return(p)
}

#' Create Box Plot
#'
#' @param data Data frame
#' @param x x-axis variable (categorical)
#' @param y y-axis variable (numeric)
#' @param fill Fill variable (optional)
#'
create_box_plot <- function(data, x, y, fill = NULL) {
  x_sym <- enquo(x)
  y_sym <- enquo(y)

  p <- ggplot(data, aes(x = !!x_sym, y = !!y_sym, group = !!x_sym))

  if (is.null(fill)) {
    p <- p + geom_boxplot(fill = okabe_ito[1], outlier.shape = NA) +
      geom_point(position = position_jitter(width = 0.1), size = 1, alpha = 0.5)
  } else {
    fill_sym <- enquo(fill)
    p <- p + geom_boxplot(aes_string(fill = fill),
                          outlier.shape = NA) +
      geom_point(position = position_jitterdodge(dodge.width = 0.75),
                 size = 1, alpha = 0.5) +
      scale_fill_okabe_ito()
  }

  p + theme_publication()
}

# ============================================================================
# Session Info
# ============================================================================

# For reproducibility
sessioninfo::session_info()
