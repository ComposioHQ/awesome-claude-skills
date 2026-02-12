# ============================================================================
# Publication-Quality Plot Examples
# ============================================================================
# Description: Example scripts demonstrating common publication plots
# Author: [Your name]
# Date: [Date]
# ============================================================================

library(ggplot2)
library(dplyr)
library(patchwork)

# Source the plot functions
source("templates/plot_functions.R")

# ============================================================================
# Example 1: Scatter Plot with Regression Line
# ============================================================================

# Simulated data
set.seed(42)
scatter_data <- data.frame(
  x = rnorm(100, mean = 50, sd = 10),
  y = rnorm(100, mean = 50, sd = 10)
)
scatter_data$y <- scatter_data$x * 0.8 + rnorm(100, sd = 5)
scatter_data$group <- sample(c("Control", "Treatment"), 100, replace = TRUE)

# Create scatter plot
p_scatter <- ggplot(scatter_data, aes(x = x, y = y, color = group)) +
  geom_point(size = 3, alpha = 0.7) +
  geom_smooth(method = "lm", se = TRUE, linewidth = 0.8) +
  scale_color_manual(values = c("#E69F00", "#0072B2")) +
  theme_publication() +
  labs(x = "Independent Variable (units)",
       y = "Dependent Variable (units)",
       color = "Group")

# Save
save_publication_figure(p_scatter, "scatter_regression",
                        width = 89, height = 89,
                        formats = c("pdf", "png"))

# ============================================================================
# Example 2: Bar Plot with Error Bars
# ============================================================================

# Summary data for bar plot
bar_data <- data.frame(
  category = c("A", "B", "C", "D"),
  mean_value = c(25, 40, 35, 50),
  se = c(3, 4, 3.5, 5)
)

# Create bar plot
p_bar <- ggplot(bar_data, aes(x = category, y = mean_value, fill = category)) +
  geom_bar(stat = "identity", width = 0.7) +
  geom_errorbar(aes(ymin = mean_value - se, ymax = mean_value + se),
                width = 0.2, linewidth = 0.8) +
  scale_fill_manual(values = okabe_ito[1:4]) +
  theme_publication() +
  labs(x = "Category",
       y = "Mean Value ± SE",
       fill = "Category") +
  theme(legend.position = "none")

# Save
save_publication_figure(p_bar, "bar_with_error",
                        width = 89, height = 89,
                        formats = c("pdf", "png"))

# ============================================================================
# Example 3: Volcano Plot (Differential Expression)
# ============================================================================

# Simulated differential expression data
set.seed(42)
n_genes <- 1000
volcano_data <- data.frame(
  gene = paste0("Gene", 1:n_genes),
  log2FC = rnorm(n_genes, 0, 2),
  pvalue = runif(n_genes, 0.0001, 1)
)

# Add significance
volcano_data <- volcano_data %>%
  mutate(
    neglog10p = -log10(pvalue),
    significance = case_when(
      log2FC >= 1 & pvalue < 0.05 ~ "Up",
      log2FC <= -1 & pvalue < 0.05 ~ "Down",
      TRUE ~ "NS"
    )
  )

# Create volcano plot
p_volcano <- ggplot(volcano_data, aes(x = log2FC, y = neglog10p)) +
  geom_point(aes(color = significance), alpha = 0.6, size = 1.5) +
  scale_color_manual(
    values = c("Down" = "#0072B2", "NS" = "#999999", "Up" = "#D55E00"),
    name = ""
  ) +
  geom_vline(xintercept = c(-1, 1), linetype = "dashed", color = "grey50") +
  geom_hline(yintercept = -log10(0.05), linetype = "dashed", color = "grey50") +
  theme_publication() +
  labs(x = expression(log[2]~Fold~Change),
       y = expression(-log[10]~P~Value)) +
  theme(legend.position = "right")

# Save
save_publication_figure(p_volcano, "volcano_plot",
                        width = 100, height = 89,
                        formats = c("pdf", "png"))

# ============================================================================
# Example 4: Box Plot
# ============================================================================

# Simulated data for box plot
set.seed(42)
box_data <- data.frame(
  group = rep(c("Control", "Treatment A", "Treatment B"), each = 30),
  value = c(rnorm(30, 20, 5), rnorm(30, 35, 8), rnorm(30, 30, 6))
)

# Create box plot
p_box <- ggplot(box_data, aes(x = group, y = value, fill = group)) +
  geom_boxplot(outlier.shape = NA, width = 0.7) +
  geom_point(position = position_jitter(width = 0.1),
             size = 1.5, alpha = 0.5) +
  scale_fill_manual(values = okabe_ito[1:3]) +
  theme_publication() +
  labs(x = "Group",
       y = "Measured Value",
       fill = "Group") +
  theme(legend.position = "none")

# Save
save_publication_figure(p_box, "box_plot",
                        width = 89, height = 89,
                        formats = c("pdf", "png"))

# ============================================================================
# Example 5: Multi-Panel Figure (2x2 grid)
# ============================================================================

# Create four different plots for demonstration
p1 <- ggplot(mtcars, aes(x = wt, y = mpg)) +
  geom_point(color = okabe_ito[1], size = 2, alpha = 0.7) +
  geom_smooth(method = "lm", se = FALSE, color = "black") +
  theme_publication(base_size = 10) +
  labs(x = "Weight", y = "MPG", title = "A")

p2 <- ggplot(mtcars, aes(x = factor(cyl), y = hp, fill = factor(cyl))) +
  geom_boxplot(outlier.shape = NA) +
  geom_point(position = position_jitter(width = 0.1),
             size = 1, alpha = 0.5) +
  scale_fill_okabe_ito() +
  theme_publication(base_size = 10) +
  labs(x = "Cylinders", y = "Horsepower", title = "B") +
  theme(legend.position = "none")

p3 <- ggplot(diamonds[sample(nrow(diamonds), 1000), ],
             aes(x = carat, y = price)) +
  geom_point(color = okabe_ito[2], size = 1, alpha = 0.5) +
  theme_publication(base_size = 10) +
  labs(x = "Carat", y = "Price", title = "C")

p4 <- ggplot(mtcars, aes(x = gear, fill = factor(am))) +
  geom_bar(position = "fill") +
  scale_fill_okabe_ito() +
  theme_publication(base_size = 10) +
  labs(x = "Gear", y = "Proportion", fill = "Transmission", title = "D")

# Combine into 2x2 grid
combined_figure <- (p1 | p2) / (p3 | p4)

# Save multi-panel figure
ggsave("results/figures/multipanel_2x2.pdf",
       combined_figure,
       width = 183, height = 183,
       units = "mm", dpi = 600)

# ============================================================================
# Example 6: Line Plot (Time Series)
# ============================================================================

# Simulated time series data
set.seed(42)
time_points <- rep(1:10, 3)
line_data <- data.frame(
  time = time_points,
  value = c(
    20 + time_points[1:10] + rnorm(10, 0, 2),
    25 + time_points[1:10] * 1.2 + rnorm(10, 0, 3),
    15 + time_points[1:10] * 0.8 + rnorm(10, 0, 2)
  ),
  group = rep(c("Series A", "Series B", "Series C"), each = 10)
)

# Create line plot
p_line <- ggplot(line_data, aes(x = time, y = value, color = group)) +
  geom_line(linewidth = 0.8) +
  geom_point(size = 2.5) +
  scale_color_manual(values = okabe_ito[1:3]) +
  theme_publication() +
  labs(x = "Time (hours)",
       y = "Measured Value (arbitrary units)",
       color = "Group") +
  theme(legend.position = "top",
        panel.grid.minor = element_line(color = "grey95"))

# Save
save_publication_figure(p_line, "line_plot",
                        width = 120, height = 89,
                        formats = c("pdf", "png"))

# ============================================================================
# Example 7: Heatmap (Correlation Matrix)
# ============================================================================

# Create correlation matrix
corr_matrix <- cor(mtcars[, c("mpg", "cyl", "disp", "hp", "wt", "qsec")])

# Convert to long format
corr_long <- expand.grid(dimnames(corr_matrix)) %>%
  mutate(correlation = as.vector(corr_matrix),
         Row = Var1, Col = Var2)

# Create heatmap
p_heat <- ggplot(corr_long, aes(x = Col, y = Row, fill = correlation)) +
  geom_tile(color = "white", linewidth = 0.5) +
  scale_fill_gradient2(low = "#0072B2", mid = "white", high = "#D55E00",
                       midpoint = 0, limits = c(-1, 1)) +
  theme_publication() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(x = "", y = "", fill = "Correlation")

# Save
save_publication_figure(p_heat, "heatmap",
                        width = 120, height = 100,
                        formats = c("pdf", "png"))

# ============================================================================
# Session Info
# ============================================================================

sessionInfo()
