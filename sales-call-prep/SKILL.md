---
name: sales-call-prep
description: Research a prospect company and generate a complete demo call brief — company snapshot, compliance risk profile, tailored 15-minute demo flow, likely objections, and suggested CTA.
---

# Sales Call Prep

Prepares a comprehensive brief for a FileFlo demo call. Takes company name + contact name and produces everything needed to run a confident, personalized 15-minute demo that ends with a trial start.

## When to Use This Skill

Run this immediately when a prospect books a demo. Prep takes 5–10 minutes.

## Output: The Call Brief

### 1. Company Snapshot
Gathered via web search for "[company name] [city] [industry]":
- Company size (employees, locations)
- What they do / their business model
- Recent news: new projects, expansions, hires, press mentions
- Any signals of growth or change (new permits, job postings for compliance/HR roles)
- Tech stack clues from job postings (what HR/safety software do they mention?)

### 2. Compliance Risk Profile
Based on their industry and size:
- Applicable regulations: OSHA, DOT/FMCSA, HIPAA, I-9/USCIS, state-specific
- Estimated fine exposure:
  - Construction: $15,625 per OSHA violation × estimated violation frequency
  - Transportation: up to $15,846 per FMCSA recordkeeping violation
  - Healthcare: HIPAA fines $100–$50,000 per violation
- Most likely pain: what is their specific nightmare scenario given their size and industry?
- Status quo guess: are they likely using spreadsheets, shared drives, a legacy HR system?

### 3. Tailored 15-Minute Demo Flow
Customize based on their industry and the pain point that got them to book:

```
0:00–2:00  Discovery
  "Before I dive in — what's the main thing you were hoping to see today?"
  "How are you currently tracking [certs/I-9s/inspections] at [Company]?"

2:00–8:00  Show the most relevant feature first
  Construction: Start with audit binder generation (most visual, most impactful)
  Transportation: Start with CDL cert tracking + 90/60/30-day alerts
  Healthcare: Start with license renewal workflow + HIPAA documentation
  Staffing: Start with I-9 bulk tracking + expiration dashboard

8:00–12:00  Walk through the compliance dashboard + rule-pack
  "This is checking your records against [150 OSHA / 80 DOT / HIPAA] rules in real time."
  "Green = compliant. Yellow = expiring in 30 days. Red = violation."

12:00–15:00  ROI math + CTA
  Calculate for their size: "[X] employees × average $15K OSHA fine × [industry violation rate]"
  "FileFlo is $299/month. One avoided fine pays for 4.5 years."
  CTA: "Want to start the 14-day free trial right now? I can walk you through setup."
```

### 4. Likely Objections + Responses

| Objection | Response |
|-----------|----------|
| "We already have a system" | "What are you using? [Listen] Most of our customers were using [their answer] — the gap was usually [audit binders / expiration tracking / mobile inspections]. Is that something you're handling in that system?" |
| "I need to check with [someone]" | "Totally makes sense. Would it help if I sent a one-pager with the ROI math for [Company] specifically? Then you'd have something concrete to share." |
| "What does setup look like?" | "Most customers are up and running in under a week. We have an onboarding call where we configure your rule-pack for [their vertical]. What's your current compliance calendar look like?" |
| "How does it integrate?" | "We connect with most HRIS systems. Which system are you using? I can confirm the integration." |
| "It's too expensive" | "If avoiding one OSHA/DOT fine pays for 4.5 years of FileFlo — what's the risk of one violation for [Company]?" |

### 5. Suggested CTA Sequence

Primary: Start free 14-day trial on the call (no credit card required)
- "Let me pull up the signup page — takes about 2 minutes and I'll stay on to help you set up your first rule-pack."

Secondary: Book an onboarding call
- "If you want to loop in [manager/IT], I can send a calendar invite for a 30-minute onboarding session with our CS team next week."

Tertiary: Send a post-call ROI summary
- "I'll send you a quick breakdown — [Company's employee count] × [vertical average fine] showing the ROI math. Something concrete for you to share internally."

## Instructions

1. Ask for: company name, contact name + title, demo booked date/time, how they came in (outbound/inbound/referral)
2. Web search: "[company name] [city]" + "[company name] compliance OR safety OR HR"
3. Search OSHA inspection database for their industry + state: osha.gov/pls/imis/establishment.search
4. Check FMCSA SAFER if transportation: safer.fmcsa.dot.gov
5. Search for job postings that reveal their tech stack and pain points
6. Calculate specific fine exposure for their company size
7. Customize the demo flow for their vertical — do not use generic flow
8. Output the full call brief in the 5-section format above
