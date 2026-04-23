---
name: philidor
description: DeFi vault intelligence with institutional-grade risk scores, yield comparison, portfolio analysis, and oracle monitoring across five major protocols and six chains.
---

# Philidor — DeFi Vault Intelligence

Philidor provides institutional-grade risk infrastructure for DeFi vaults. It scores, compares, and monitors yield opportunities across Morpho, Yearn, Aave, Beefy, and Spark on Ethereum, Base, Arbitrum, Polygon, Optimism, and Gnosis.

## When to Use This Skill

- Finding the safest vaults for a given asset and chain
- Comparing yield opportunities across protocols with risk-adjusted analysis
- Checking detailed risk breakdowns (asset composition, platform code, governance)
- Analyzing portfolio exposure and risk concentration
- Monitoring oracle health and feed freshness across chains
- Getting a high-level overview of the DeFi vault market

## What This Skill Does

1. **Vault Search & Filter** — Search and filter vaults by chain, protocol, asset, risk tier, TVL, and APR. Sort by any metric.
2. **Risk Scoring** — Institutional-grade risk scores (0–10) across three vectors: Asset Composition (40%), Platform & Strategy (40%), and Governance (20%). Tiered as Prime (≥8), Core (5–7.9), or Edge (<5).
3. **Protocol Comparison** — Compare 2–3 vaults side-by-side on TVL, APR, risk score, audit status, and incident history. Get full protocol profiles with security track records.
4. **Portfolio Analysis** — Analyze wallet positions across vaults with aggregate risk scoring, chain/protocol concentration, and exposure breakdown.
5. **Oracle Monitoring** — Check Chainlink oracle feed health, staleness thresholds, and deviation alerts across all supported chains.
6. **Market Statistics** — Total TVL, vault counts, risk tier distribution, and TVL breakdown by protocol and chain.

## How to Use

### Basic Usage

```bash
# Get market overview
philidor stats

# Search for USDC vaults
philidor search "USDC"

# Analyze a portfolio
philidor portfolio 0xYourWalletAddress
```

### Advanced Usage

```bash
# Screen for Prime-tier vaults with >$1M TVL on Ethereum
philidor search --chain Ethereum --risk-tier Prime --min-tvl 1000000

# Compare two specific vaults side-by-side
philidor compare --vault ethereum:0xVault1 --vault base:0xVault2

# Get full risk breakdown for a vault
philidor risk-breakdown --network ethereum --address 0xVaultAddress

# Find the safest WETH vaults across all chains
philidor safest --asset WETH
```

## Agent Workflows

### Find the Best Vault for an Asset

```bash
philidor search --asset USDC --sort-by apr_net --sort-order desc --json
philidor safest --asset USDC --min-tvl 500000 --json
```

### Compare Protocols for a Strategy

```bash
philidor protocol-info morpho --json
philidor protocol-info aave-v3 --json
philidor compare --vault ethereum:0xMorphoVault --vault ethereum:0xAaveVault --json
```

### Assess Portfolio Risk

```bash
philidor portfolio 0xWalletAddress --json
philidor risk-breakdown --network ethereum --address 0xLargestPosition --json
```

### Monitor Safety

```bash
philidor incidents --json
philidor oracle-health --chain Ethereum --json
philidor stats --json
```

## Tips

- Always use `--json` for structured output when integrating with other tools or agents.
- Check risk scores before recommending any vault — a high APR with a low risk score may indicate elevated risk.
- Note data freshness: vault data syncs continuously, but snapshots reflect point-in-time state.
- Cross-reference incident history when evaluating protocols — use `philidor incidents` to see recent critical events.
- Risk tiers provide quick classification: Prime (≥8) for conservative allocations, Core (5–7.9) for balanced, Edge (<5) for risk-tolerant.

## Prerequisites

```bash
npm install -g @philidorlabs/cli
```

No API key is required. The CLI connects to the public Philidor API.
