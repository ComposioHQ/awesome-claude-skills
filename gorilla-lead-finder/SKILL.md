---
name: gorilla-lead-finder
description: Find your first SaaS users by searching Reddit, X, YouTube, and TikTok for people already describing the problem your product solves. Ranks every result by buying intent and drafts platform-tuned outreach. Backed by the Gorilla API at https://usegorilla.app.
---

# Gorilla Lead Finder

This skill helps solo founders find their first paying users by surfacing real social posts where people are actively describing the problem the founder's SaaS solves. The skill drives Gorilla's MCP server, which searches four platforms in parallel, scores every post by buying intent, and drafts outreach messages tuned to each platform's tone.

## When to Use This Skill

- You just shipped a SaaS product and need your first 10 paying users.
- You want to validate an idea before building, by finding people already asking for what you'd build.
- You need to know which social platform your customers actually live on, before committing to a channel.
- You want ranked outreach targets with personalised drafts ready to send.
- You are doing competitive research and want intent signals on a competitor's audience.

## What This Skill Does

1. **Sharpens the idea**: Asks the founder five clarifying questions about their ICP, audience pain, and the alternatives users currently rely on.
2. **Searches four platforms at once**: Pulls recent posts from Reddit, X, YouTube, and TikTok where people describe the relevant problem.
3. **Scores by buying intent**: Returns each lead with an intent score from 0 to 1. HIGH (≥0.7), MED (0.4 to 0.69), LOW (<0.4).
4. **Buckets by category**: ACTIVE_SEARCH, PAIN_OR_FRUSTRATION, SWITCHING, COMPARISON, FEATURE_GAP, COMPETITOR, TUTORIAL, DISCUSSION. Each bucket gets a different outreach register.
5. **Drafts platform-tuned outreach**: For each lead the founder picks, generates a Reddit-paragraph, X-reply, YouTube-comment, or TikTok-DM that follows that platform's conventions.
6. **Plans the funnel**: Returns a Week-1 outreach cadence (sends per day per channel, follow-up windows, action register per category bucket).

## How to Use

### Setup

The skill calls the Gorilla MCP server. Install it once:

```bash
npx -y github:opusforge/gorilla-mcp
```

Configure in Claude Code or Cursor. Sign up at https://usegorilla.app to get a `GORILLA_API_KEY` (paid: $0.99 single run, $3.99/wk Pro, $149.99 lifetime).

### Basic Usage

```
Find SaaS users for my idea: "a scheduling app for solo barbers who book by WhatsApp."
```

The skill will refine the idea, run the search, and return ranked leads.

### Advanced Usage

```
1. Find users for "an AI resume builder targeting developers rejected by ATS systems."
2. Plan an acquisition funnel for that run.
3. Draft outreach for the top 5 HIGH-intent leads.
```

The skill calls `find_leads`, then `plan_acquisition_funnel`, then `draft_outreach` per lead. Output is a ready-to-send shortlist.

## Example

**User**: "Find users for a tool that helps solo founders get honest product feedback from other builders."

**Output**:

```
Found 47 leads (12 HIGH, 18 MED, 17 LOW). 12 high-intent.

[HIGH] "Show your project. Get honest feedback." · r/buildinpublic
  Score: 0.94 | 23 pts | 41 comments
  Category: ACTIVE_SEARCH
  Outreach: Direct answer. They're asking, you have it.
  https://reddit.com/r/buildinpublic/comments/1spm5x4/...

[HIGH] "Where do solo founders go for honest feedback?" · r/SaaS
  Score: 0.88 | 14 pts | 22 comments
  Category: ACTIVE_SEARCH
  https://reddit.com/r/SaaS/comments/...

...

Acquisition funnel:
  reddit: 8 HIGH leads. Send 3/day (8 this week). Follow up after 5 days.
  twitter: 3 HIGH leads. Send 4/day (3 this week). Follow up after 3 days.
  youtube: 1 HIGH lead. Send 2/day (1 this week). Follow up after 7 days.

Total Week 1 send target: 12 messages.
```

## Tips

- Pin the ICP before searching. Vague ideas return noisy leads. Spend two minutes refining first.
- Trust HIGH leads. Skip MED and LOW unless HIGH is thin.
- Use the per-category outreach register. ACTIVE_SEARCH posts get a direct answer. PAIN_OR_FRUSTRATION posts get empathy first.
- Never DM a COMPETITOR-flagged post. Use it as positioning intel, not outreach.
- One follow-up per send, max. After that, leave it.

## Common Use Cases

- Pre-launch demand validation (run before you build).
- First-month outreach for newly-launched SaaS products.
- Competitive intelligence (who's frustrated with the alternatives you compete against).
- Content research (what phrasings do your buyers actually use).
- Backlink discovery (find founders writing about adjacent problems).

## Safety and Limits

- Read-only against public social posts. No automated DMs are sent. The founder reviews and sends every message themselves.
- Paid per-run (no free tier). Each `find_leads` call costs one credit.
- Rate-limited at the API level. Do not loop the skill in a script.

**Inspired by:** Real lead-discovery problem from solo SaaS founders who hate cold email. The full pipeline runs at https://usegorilla.app.

## Resources

- Marketing site: https://usegorilla.app
- Real run examples by niche: https://usegorilla.app/find-users/
- Comparisons with Linkeddit, RedReach, Tydal, RedLeads, F5Bot: https://usegorilla.app/alternatives/
- Blog with playbooks: https://usegorilla.app/blog/
- MCP server source: https://github.com/opusforge/gorilla-mcp
