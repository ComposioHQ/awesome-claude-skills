---
name: content-moderation
description: Moderate text, images, and video using Vettly's AI-powered content moderation API via MCP server. Check content against policies, validate policy configs, and audit moderation decisions.
---

# Content Moderation

Moderate user-generated content using Vettly's content moderation API. This skill uses the `@vettly/mcp` MCP server to check text, images, and video against configurable moderation policies with auditable decisions.

## Setup

Install the `@vettly/mcp` MCP server in your Claude Code settings:

```json
{
  "mcpServers": {
    "vettly": {
      "command": "npx",
      "args": ["-y", "@vettly/mcp"],
      "env": {
        "VETTLY_API_KEY": "your-api-key"
      }
    }
  }
}
```

Get an API key at [vettly.dev](https://vettly.dev).

## Available Tools

### `moderate_content`

Check text, image, or video content against a Vettly moderation policy. Returns a safety assessment with category scores, the action taken, provider used, latency, and cost.

**Parameters:**
- `content` (required) - The content to moderate (text string, or URL for images/video)
- `policyId` (required) - The policy ID to use for moderation
- `contentType` (optional, default: `text`) - Type of content: `text`, `image`, or `video`

### `validate_policy`

Validate a Vettly policy YAML without saving it. Returns validation results with any syntax or configuration errors. Use this to test policy changes before deploying them.

**Parameters:**
- `yamlContent` (required) - The YAML policy content to validate

### `list_policies`

List all moderation policies available in your Vettly account. Takes no parameters. Use this to discover available policy IDs before moderating content.

### `get_usage_stats`

Get usage statistics for your Vettly account including request counts, costs, and moderation outcomes.

**Parameters:**
- `days` (optional, default: `30`) - Number of days to include in statistics (1-365)

### `get_recent_decisions`

Get recent moderation decisions with optional filtering by outcome, content type, or policy.

**Parameters:**
- `limit` (optional, default: `10`) - Number of decisions to return (1-50)
- `flagged` (optional) - Filter to only flagged content (`true`) or safe content (`false`)
- `policyId` (optional) - Filter by specific policy ID
- `contentType` (optional) - Filter by content type: `text`, `image`, or `video`

## When to Use This Skill

- Moderate user-generated content (comments, posts, uploads) before publishing
- Test and validate moderation policy YAML configs during development
- Audit recent moderation decisions to review flagged content
- Monitor moderation costs and usage across your account
- Compare moderation results across different policies

## Examples

### Moderate a user comment

```
Moderate this user comment for my community forum policy:
"I hate this product, it's the worst thing I've ever used and the developers should be ashamed"
```

Claude will call `list_policies` to find available policies, then `moderate_content` with the appropriate policy ID and return the safety assessment.

### Validate a policy before deploying

```
Validate this moderation policy YAML:

categories:
  - name: toxicity
    threshold: 0.8
    action: flag
  - name: spam
    threshold: 0.6
    action: block
```

Claude will call `validate_policy` and report any syntax or configuration errors.

### Review recent flagged content

```
Show me all flagged content from the last week
```

Claude will call `get_recent_decisions` with `flagged: true` to retrieve recent moderation decisions that were flagged.

## Tips

- Always call `list_policies` first if you don't know which policy ID to use
- Use `validate_policy` to test policy changes before deploying to production
- Use `get_usage_stats` to monitor costs and catch unexpected spikes
- Filter `get_recent_decisions` by `contentType` or `policyId` to narrow results
- For image and video moderation, pass the content URL rather than raw data
