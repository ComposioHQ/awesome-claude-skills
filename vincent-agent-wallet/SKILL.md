---
name: vincent-agent-wallet
description: Secure EVM wallet and Polymarket trading for AI agents. Supports transfers, swaps, arbitrary EVM transactions, and prediction markets without ever exposing private keys to the agent.
---

# Vincent Agent Wallet

Give your AI agent a secure crypto wallet. Vincent lets agents send transfers, perform token swaps, execute arbitrary EVM transactions, sign messages for Ethereum and Solana, and trade on Polymarket prediction markets — all without the agent ever touching a private key.

Server-side policies (spend limits, token allowlists, human-in-the-loop approvals) keep the agent on a tight leash, and every transaction attempt is recorded in an audit log.

## When to Use This Skill

- The user asks the agent to send tokens, swap assets, or interact with a smart contract
- The user wants the agent to place trades on Polymarket prediction markets
- The user needs the agent to sign a message or transaction for Ethereum or Solana
- The user wants autonomous on-chain actions with guardrails and audit trails

## What This Skill Does

1. **Wallet Management**: Creates and manages EVM wallets that the agent can use. Private keys are held server-side and never sent to the agent.
2. **Transfers & Swaps**: Send native tokens or ERC-20s to any address, or swap between tokens on supported DEXs.
3. **Arbitrary EVM Transactions**: Build and submit any EVM transaction (contract calls, approvals, etc.).
4. **Raw Signing**: Sign arbitrary messages or transaction payloads for Ethereum and Solana.
5. **Polymarket Trading**: Look up prediction markets, place bets, and manage positions on Polymarket.
6. **Policy Enforcement**: Server-side rules control what the agent can do — spend limits, token allowlists, chain restrictions, and mandatory human approvals for high-value actions.
7. **Audit Logging**: Every transaction attempt (approved or denied) is logged for compliance and debugging.

## How to Use

### Installation

Install the wallet skill:

```bash
npx clawhub@latest install agentwallet
```

Or install directly from the skills repo:

```bash
npx skills add HeyVincent-ai/agent-skills/wallet
```

### Basic Usage

Once installed, ask your agent to perform wallet actions in natural language:

```
Send 0.1 ETH to 0xABC...123
```

```
Swap 50 USDC for ETH on Base
```

```
What prediction markets are trending on Polymarket right now?
```

### Advanced Usage

```
Place a $25 bet on "Yes" for the top Polymarket market about the next Fed rate decision
```

```
Call the `mint` function on contract 0xDEF...456 on Polygon with 1 MATIC
```

```
Sign this message with my Solana key: "Verify ownership for app XYZ"
```

## Example

**User**: "Send 10 USDC to 0x742d35Cc6634C0532925a3b844Bc9e7595f2bD28 on Base"

**Output**:
```
Transaction submitted.

  Type:    ERC-20 Transfer
  Token:   USDC
  Amount:  10.00 USDC
  To:      0x742d...bD28
  Chain:   Base
  Tx Hash: 0x8a3f...c4e1
  Status:  Confirmed (block 18294012)

The transfer has been completed. 10 USDC was sent on Base. You can view the
transaction at https://basescan.org/tx/0x8a3f...c4e1
```

**User**: "What are the top Polymarket markets right now?"

**Output**:
```
Here are the top trending Polymarket prediction markets:

1. "Will the Fed cut rates in March 2026?" — Yes: 62% / No: 38% — $4.2M volume
2. "Bitcoin above $150k by July 2026?" — Yes: 41% / No: 59% — $8.7M volume
3. "Will GPT-5 be released before June 2026?" — Yes: 55% / No: 45% — $2.1M volume

Would you like to place a trade on any of these?
```

## Tips

- Vincent wallets are non-custodial on the server side. The agent requests actions, and the Vincent backend executes them after policy checks.
- Configure spend limits before giving the agent autonomy. Start with low limits and increase as you build confidence.
- Use human-in-the-loop approval policies for high-value transactions during early testing.
- The agent can read balances, transaction history, and market data without any policy restrictions — policies only apply to write operations.
- For Polymarket, the agent can research markets and odds before placing trades, helping it make informed decisions.
- All supported EVM chains (Ethereum, Base, Polygon, Arbitrum, Optimism, etc.) work out of the box.

## Common Use Cases

- **Portfolio rebalancing**: Agent monitors token allocations and swaps to maintain target ratios
- **DCA (Dollar-Cost Averaging)**: Agent executes scheduled purchases of specific tokens
- **Prediction market research and trading**: Agent analyzes news, evaluates Polymarket odds, and places informed bets
- **Payment automation**: Agent sends recurring payments or processes payroll in stablecoins
- **Smart contract interaction**: Agent calls contract functions (minting, staking, claiming rewards)
- **Cross-chain operations**: Agent moves assets between supported EVM chains
- **Treasury management**: Agent manages a project treasury with policy-enforced spending rules

## Resources

- [Vincent GitHub](https://github.com/HeyVincent-ai/Vincent)
- [Agent Skills Repo](https://github.com/HeyVincent-ai/agent-skills)
- [Website](https://heyvincent.ai)
