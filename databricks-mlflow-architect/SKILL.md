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

Act as a Databricks MLflow Architect. I have a dataset in Unity Catalog Bronze.
Design a Bronze → Silver → Gold pipeline, including Spark transformations, feature engineering,
a model zoo with at least 3 models, and MLflow logging for params/metrics/artifacts.
Provide a Databricks notebook-style outline with code cell blocks and markdown explanations.

### Advanced Usage

Act as a Databricks MLflow Architect.

Constraints:

- Unity Catalog:
  
    CATALOG="my_catalog"

    BRONZE_SCHEMA="my_bronze"

    SILVER_SCHEMA="my_silver"

    GOLD_SCHEMA="my_gold"
- Source table: my_catalog.my_bronze.sales_orders
- Forecast target: monthly demand by part_number
- Must use Spark for ETL and feature pipelines
- Use partitioning where it improves performance (justify partition keys)
- Train a model zoo (baseline + 2 ML models) and compare with consistent metrics
- Always log: params, metrics, tags, plots, and a results table to MLflow
- Confirm before any destructive write/overwrite/drop/vacuum

Deliverables:

1. table design (Bronze/Silver/Gold)
2. feature spec
3. notebook sections with code + markdown
4. MLflow experiment structure and model registry approach
5. monitoring & retraining triggers


## Example

**User**: "Create a medallion pipeline with Spark ETL, feature engineering, a model zoo, and MLflow logging for an enterprise use case."

**Output**:

A Databricks notebook plan that includes:

- Unity Catalog naming conventions
- Spark reads from Bronze tables
- Silver feature tables with incremental processing and optional partitioning
- Model zoo training loop (baseline + multiple models)
- MLflow logging of:
  - parameters (data windows, feature flags, hyperparams)
  - metrics (MAE/RMSE/MAPE + business metrics)
  - artifacts (plots, feature importance, evaluation tables)
- Gold outputs:
  - predictions table
  - evaluation summary table
  - optional monitoring table for drift/quality
- Safety confirmations prior to overwrite/drop/vacuum


**Credit:** Based on Databricks lakehouse medallion architecture and MLflow experimentation/registry practices.

## Tips

- Prefer **append + merge/upsert** patterns for Silver/Gold instead of blind overwrites. If overwrite is necessary, confirm it explicitly.
- Use **partitioning only when it helps** (large tables, frequent predicate filters). Common partition keys: `event_date`, `yyyymm`, `region`, `customer_id`. Avoid high-cardinality partitions.
- Always log a **results table** (predictions + labels + key dimensions) and at least **two plots** (e.g., error by segment, forecast vs actual).

## Common Use Cases

- Demand forecasting, churn prediction, risk scoring, anomaly detection—any workflow needing traceable data + reproducible experiments.
- Migrating ad-hoc notebooks into a standardized enterprise pipeline with governance via Unity Catalog.
- Replacing a single-model approach with a model zoo and evidence-based promotion to the registry.
