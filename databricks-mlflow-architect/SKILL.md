---
name: databricks-mlflow-architect
description: Designs an enterprise-grade Databricks + MLflow lakehouse pipeline using Unity Catalog medallion layers (bronze/silver/gold), Spark processing, model zoo comparisons, and full parameter/metric/artifact logging.
---

# Databricks MLflow Architect

This skill helps you design and implement an enterprise-grade machine learning solution on Databricks using Unity Catalog and the medallion architecture:

- **Bronze**: raw ingested tables (source-aligned)
- **Silver**: cleaned/standardized + feature engineering
- **Gold**: model outputs, scoring results, and curated analytics tables

It emphasizes **Spark-first data processing**, **partitioning strategies** where needed, **model zoo experimentation**, and **MLflow tracking** for parameters, metrics, artifacts (plots/tables), and reproducibility.

## When to Use This Skill

- You need a production-ready Databricks ML pipeline that follows **Unity Catalog** and **Bronze/Silver/Gold** standards.
- You want a repeatable workflow that logs everything to **MLflow** (params, metrics, artifacts, versions) and supports auditability.
- You must compare multiple models (a **model zoo**) and promote the best candidate to production with clear evidence.

## What This Skill Does

1. **Architects the lakehouse pipeline**: Defines catalog/schema/table layout and medallion responsibilities.
2. **Implements Spark-based ETL + feature engineering**: Reads from Bronze, transforms to Silver, writes partitioned tables when appropriate.
3. **Runs a model zoo and compares models**: Trains multiple candidate models with consistent evaluation.
4. **Logs everything with MLflow**: Parameters, metrics, tags, datasets lineage hints, plots, and tables are captured.
5. **Writes Gold outputs**: Predictions, feature snapshots (optional), and monitoring-ready datasets land in Gold.
6. **Enforces safe operations**: Confirms before destructive actions (overwrite, drop, vacuum, backfills).

## How to Use

### Basic Usage

