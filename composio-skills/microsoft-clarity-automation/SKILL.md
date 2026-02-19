---
name: Microsoft Clarity Automation
description: "Automate user behavior analytics with Microsoft Clarity -- export heatmap data, session metrics, and engagement analytics segmented by browser, device, country, source, and more through the Composio Microsoft Clarity integration."
requires:
  mcp:
    - rube
---

# Microsoft Clarity Automation

Export **Microsoft Clarity** user behavior analytics directly from Claude Code. Pull heatmap data, session metrics, and engagement insights segmented by multiple dimensions without leaving your terminal.

**Toolkit docs:** [composio.dev/toolkits/microsoft_clarity](https://composio.dev/toolkits/microsoft_clarity)

---

## Setup

1. Add the Composio MCP server to your configuration:
   ```
   https://rube.app/mcp
   ```
2. Connect your Microsoft Clarity account when prompted. The agent will provide an authentication link.
3. Ensure your Clarity project has sufficient data collection enabled for the dimensions you want to analyze.

---

## Core Workflows

### 1. Export Recent Analytics Data

Export Clarity analytics data for the last 1-3 days, segmented by up to three dimensions simultaneously.

**Tool:** `MICROSOFT_CLARITY_DATA_EXPORT`

Key parameters:
- `numOfDays` (required) -- number of days to export: `1` (last 24h), `2` (last 48h), or `3` (last 72h)
- `dimension1` -- first breakdown dimension
- `dimension2` -- second breakdown dimension (optional)
- `dimension3` -- third breakdown dimension (optional)

Available dimensions:
- `Browser` -- Chrome, Firefox, Safari, Edge, etc.
- `Device` -- Desktop, Mobile, Tablet
- `Country/Region` -- geographic location of users
- `OS` -- Windows, macOS, iOS, Android, etc.
- `Source` -- traffic source (e.g., google, direct, referral)
- `Medium` -- traffic medium (organic, cpc, referral, etc.)
- `Campaign` -- marketing campaign name
- `Channel` -- traffic channel grouping
- `URL` -- specific page URLs

Example prompt: *"Export Clarity data for the last 24 hours broken down by Device and Country/Region"*

---

### 2. Device Performance Analysis

Analyze how user behavior differs across device types to optimize responsive design.

**Tool:** `MICROSOFT_CLARITY_DATA_EXPORT`

Configuration: `numOfDays: 3`, `dimension1: "Device"`, `dimension2: "Browser"`

Example prompt: *"Show me Clarity metrics for the last 3 days by Device and Browser"*

---

### 3. Traffic Source Breakdown

Understand which traffic sources drive the most engaged users.

**Tool:** `MICROSOFT_CLARITY_DATA_EXPORT`

Configuration: `numOfDays: 2`, `dimension1: "Source"`, `dimension2: "Medium"`

Example prompt: *"Export Clarity data for the last 48 hours broken down by Source and Medium"*

---

### 4. Geographic User Behavior

Analyze user engagement patterns across different countries and regions.

**Tool:** `MICROSOFT_CLARITY_DATA_EXPORT`

Configuration: `numOfDays: 3`, `dimension1: "Country/Region"`, `dimension2: "Device"`

Example prompt: *"Get Clarity data for the last 72 hours segmented by Country/Region and Device type"*

---

### 5. Page-Level Performance

Examine which specific URLs have the highest or lowest engagement metrics.

**Tool:** `MICROSOFT_CLARITY_DATA_EXPORT`

Configuration: `numOfDays: 1`, `dimension1: "URL"`, `dimension2: "Device"`

Example prompt: *"Export yesterday's Clarity data broken down by URL and Device"*

---

### 6. Campaign Attribution Analysis

Evaluate marketing campaign effectiveness through user behavior metrics.

**Tool:** `MICROSOFT_CLARITY_DATA_EXPORT`

Configuration: `numOfDays: 3`, `dimension1: "Campaign"`, `dimension2: "Channel"`, `dimension3: "Device"`

Example prompt: *"Show Clarity engagement data for the last 3 days by Campaign, Channel, and Device"*

---

## Known Pitfalls

- **Limited time window:** Data export is limited to the last 1, 2, or 3 days only. The `numOfDays` parameter only accepts values of 1, 2, or 3. For longer historical analysis, you need to run exports periodically and aggregate them externally.
- **Dimension name exact match:** Dimension values must match exactly as listed (e.g., `Country/Region` not `country` or `region`). Case and slashes matter.
- **Maximum three dimensions:** You can segment by up to three dimensions per export. For more complex analysis, run multiple exports with different dimension combinations.
- **Data availability lag:** Clarity data may have a short processing delay. Very recent sessions (last few minutes) may not appear in exports.
- **Single tool limitation:** The Clarity integration currently offers only the data export tool. For heatmap visualizations and session recordings, use the Clarity web dashboard directly.
- **Response size:** Exports with high-cardinality dimensions like `URL` combined with other dimensions can produce large response payloads. Consider narrowing your time window or using fewer dimensions.

---

## Quick Reference

| Tool Slug | Description |
|---|---|
| `MICROSOFT_CLARITY_DATA_EXPORT` | Export analytics data with up to 3 dimensional breakdowns |

**Available Dimensions:**

| Dimension | Description |
|---|---|
| `Browser` | Web browser (Chrome, Firefox, Safari, etc.) |
| `Device` | Device type (Desktop, Mobile, Tablet) |
| `Country/Region` | Geographic location |
| `OS` | Operating system |
| `Source` | Traffic source |
| `Medium` | Traffic medium |
| `Campaign` | Marketing campaign |
| `Channel` | Traffic channel grouping |
| `URL` | Specific page URL |

---

*Powered by [Composio](https://composio.dev)*
