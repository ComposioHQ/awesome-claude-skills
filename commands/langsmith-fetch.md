---
description: Debug LangChain/LangGraph agents by fetching execution traces from LangSmith Studio
argument-hint: Optional trace ID or time range
---

# LangSmith Fetch

Load the `awesome-claude-skills:langsmith-fetch` skill and follow its workflow to debug agent traces.

If `$ARGUMENTS` is provided, use it as the trace ID or time filter.

Otherwise, fetch the most recent traces from the last 5 minutes.
