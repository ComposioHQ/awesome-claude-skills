---
name: customer-support-classifier
description: Automatically classify and prioritize customer support tickets, extract key information, and suggest response templates. Use when processing support inquiries.
---

# Customer Support Classifier

Intelligently analyzes customer support tickets to automatically classify them by priority, category, and sentiment. Extracts key information such as account details, issue descriptions, and customer emotions. Suggests appropriate response templates to help support teams respond faster and more consistently.

## When to Use This Skill

- Processing incoming support tickets to determine priority
- Routing tickets to the appropriate team or agent
- Extracting actionable information from customer messages
- Suggesting response templates for common issues
- Analyzing support trends and patterns

## What This Skill Does

1. **Priority Classification**: Assigns urgency levels (Critical, High, Medium, Low) based on content and sentiment
2. **Category Tagging**: Categorizes tickets (Billing, Technical, Feature Request, Bug Report, etc.)
3. **Information Extraction**: Pulls out account IDs, order numbers, error messages, and key details
4. **Sentiment Analysis**: Detects customer frustration, urgency, or satisfaction levels
5. **Response Suggestions**: Recommends appropriate templates or draft responses

## How to Use

### Basic Usage

```
Classify this support ticket and suggest a response
```

### Advanced Usage

```
Analyze these 10 support tickets, categorize by type, extract account information, and suggest priority order for response
```

## Example

**User**: "Process this support request"

**Input**:
```
Subject: URGENT - Payment failed but charged my card!

Hi, I tried to upgrade my plan 30 minutes ago but got an error. 
However, I was charged $99 on my credit card ending in 4242. 
My account email is john@company.com. I need this fixed ASAP 
because our team can't access the premium features we paid for.

This is really frustrating - please help!
```

**Output**:
```yaml
Classification:
  Priority: Critical
  Category: Billing/Payment Issue
  Sentiment: Frustrated, Urgent
  
Extracted Information:
  Account: john@company.com
  Amount: $99
  Card: ****4242
  Time: 30 minutes ago
  Issue: Payment charged but upgrade failed

Suggested Response Template:
  "Hi [Name], I sincerely apologize for this billing issue. 
   I can see the $99 charge on your account. I'm escalating 
   this to our billing team immediately and will have this 
   resolved within 2 hours. You'll receive a confirmation 
   email once the upgrade is processed."
```

**Inspired by:** Zendesk Auto-routing and Intercom Resolution Bot workflows

## Tips

- Provide historical ticket data for better classification accuracy
- Define custom priority rules for your specific business needs
- Review suggested responses before sending to ensure brand voice
- Use for batch processing during high-volume periods

## Common Use Cases

- Triaging incoming support emails or chat messages
- Prioritizing tickets for small support teams
- Training new support agents with suggested responses
- Identifying trending issues from ticket patterns
- Automating initial customer acknowledgment
