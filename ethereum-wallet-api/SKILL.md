---
name: ethereum-wallet-api
description: Manage Ethereum wallets through the Ethereum Wallet Manager HTTP API — create wallets, check balances, validate addresses, query gas prices, and list transactions, authenticated with an X-API-Key header. Use when the user wants to manage Ethereum wallets on their own wallet-manager backend.
---

# Ethereum Wallet Manager API

Manage Ethereum wallets through a self-hosted HTTP API. Authentication uses the `X-API-Key` request header (no email/password login required).

## When to Use This Skill

- The user wants to create or list Ethereum wallets on their own wallet-manager backend.
- The user needs to check an ETH balance or validate an Ethereum address.
- The user needs the current gas price or wants to review transaction history.
- The user has a running Ethereum Wallet Manager API and an API Key generated from the web console.

## What This Skill Does

1. **Create a wallet** — `POST /api/wallet`
2. **List wallets** — `GET /api/wallet`
3. **Check a wallet's balance** — `GET /api/wallet/{id}/balance`
4. **Validate an address** — `GET /api/wallet/validate-address/{address}`
5. **Query gas price** — `GET /api/wallet/gas-price`
6. **List transactions** — `GET /api/transaction?page=&pageSize=`
7. **Inspect a transaction** — `GET /api/transaction/{id}`

## How to Use

Set the connection details as environment variables:

```bash
export API_BASE_URL="https://your-server.example.com"
export API_KEY="your-api-key"
```

Then call the endpoints with the `X-API-Key` header:

```bash
curl -s "$API_BASE_URL/api/wallet" -H "X-API-Key: $API_KEY"
curl -s "$API_BASE_URL/api/wallet/validate-address/0x1234..."
```

## Example

**User**: "Create a wallet called 'Trading' and check its balance."

**Steps**:
1. `POST /api/wallet` with body `{"name": "Trading"}` and the `X-API-Key` header.
2. Read the returned `id`.
3. `GET /api/wallet/{id}/balance` to check the balance.

## Tips

- Never hardcode the API Key; keep it in an environment variable.
- Address validation and gas-price queries are public endpoints and do not require an API Key.
- Fund transfers are deliberately not exposed by this skill; request separate authorization from the service provider to enable them.