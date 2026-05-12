---
name: marketing-research
description: >
  Use this skill for any marketing research, product positioning, copywriting research, or audience profiling task.
  Triggers include: "research my product", "develop my value proposition", "profile my avatar", "understand my market",
  "create a unique mechanism", "market awareness", "market sophistication", "ideal customer profile", "ICP research",
  "positioning research", "copywriting research", "features and benefits", "competitor research", "competitive analysis",
  or any request to deeply research a product or audience for marketing purposes. Use this skill proactively whenever
  a user wants to prepare materials for sales copy, landing pages, ads, email sequences, or any persuasion-focused
  content. If a user says "help me understand my market", "I need to figure out my messaging", "who is my customer",
  or "what makes my product different", this skill applies immediately.
---

# Marketing Research Sourcebook — Enhanced Edition

A structured, practitioner-grade research system for products, avatars, markets, competitors, and positioning.
Built for copywriters, marketers, and founders who need deep research before writing a single word of copy.

---

## STEP 0: INTAKE INTERVIEW (Always Start Here)

Before running any module, conduct a brief interview to collect inputs. Ask these questions — all at once, not one at a time:

```
Before we dive in, I need a few details so I can run this properly:

1. What is your product? (Give me a short description — what it is, what it does, and who it's for)
2. What are the main components, features, or chapters?
3. Who is your ideal customer? (Describe them — their role, situation, what they want)
4. Do you have any named competitors? (Even 2–3 is enough)
5. What stage are you at?
   a) Just starting research — need everything
   b) Have a product defined, need avatar and market research
   c) Have avatar research done, need positioning and copy angles
   d) Have everything, need a competitor comparison
```

Once you have answers, store them as the **Research Context Block**:

```
RESEARCH CONTEXT
----------------
Product: [user input]
Features/Components: [user input]
Avatar: [user input]
Competitors: [user input]
Research Stage: [user input]
```

Reference this block throughout — never ask the user to repeat information already captured.

---

## STEP 1: DIAGNOSTIC — WHERE TO START

Use the user's Research Stage answer to route them:

| Stage | Start Here |
|-------|-----------|
| Just starting — need everything | Module 0 (Competitor Research) → Module 1 (Product) → Module 2 (Avatar) → Module 3 (Market) → Module 4 (Value Proposition) |
| Have product, need avatar + market | Module 2 (Avatar) → Module 3 (Market) → Module 4 (Value Proposition) |
| Have avatar, need positioning | Module 4 (Value Proposition) → Module 5 (Mental Models) |
| Need competitor comparison | Module 0 (Competitor Research) → Module 4 (Value Proposition) |

Tell the user which module you're starting with and why. Then proceed.

---

## MODULE 0: COMPETITOR RESEARCH

*Goal: Map the competitive landscape before researching your own product. What's already being promised? What's been heard before? Where is the gap?*

> **Auto-populate from Research Context:** Use `[competitors from intake]` and `[product from intake]` throughout.

### Prompt 1 — Competitor Landscape Map

```
You're an expert market researcher and competitive analyst. You are thorough, specific, and your output is never generic.

Here's context for your task:
- Product category: [product from intake]
- Known competitors: [competitors from intake]
- Target avatar: [avatar from intake]

Here's your task: For each competitor listed, provide:
1. Their core promise / headline claim
2. Their Unique Mechanism (how they say their product works)
3. Their primary target avatar
4. Their apparent State of Sophistication targeting (1–5 scale)
5. What they do NOT address — the gap in their positioning

Then, identify the 2–3 most common claims across all competitors that the market has likely already heard many times.
```

---

### Prompt 2 — Competitive Gap Analysis

```
Based on the competitor landscape above, identify:

1. The most overcrowded positioning angles (what everyone is saying)
2. The most underserved desires in this market (what no one is addressing well)
3. Three positioning territories that are currently wide open
4. Which State of Sophistication level is most underserved by current competitors

This will become the foundation for our Unique Mechanism and Value Proposition.
```

---

### Prompt 3 — Differentiation Pressure Test

```
Here's my product: [product from intake]

Given the competitive landscape we just mapped, pressure-test my product's differentiation:
1. Does my core claim sound like anything a competitor is already saying?
2. Where is my product genuinely different — in mechanism, in audience, in outcome, or in delivery?
3. What would make a jaded, sophistication-level-4 buyer stop scrolling and pay attention to my product specifically?

Be blunt. If my product sounds like everyone else, say so.
```

> **Chain forward:** Save the "positioning territories" from Prompt 2 and the "genuine differences" from Prompt 3. These feed directly into Module 1 (Unique Mechanism naming) and Module 4 (Value Proposition).

---

## MODULE 1: PRODUCT

*Goal: Uncover features, benefits, and a compelling Unique Mechanism that is differentiated from competitors.*

> **Auto-populate from Research Context:** Use `[product from intake]` and `[features from intake]` throughout.
> **Chain from Module 0:** Reference the competitive gaps identified — the Unique Mechanism should occupy territory competitors are NOT claiming.

---

### Prompt 1 — Features, Benefits, Dimensionalize

```
You're an expert product and market researcher. You're inventive, creative, and excellent at finding unique combinations, discoveries, and breakthroughs. You are not generic and your output isn't generic. Everything you produce is advanced, specific, detailed, novel, and uncommon.

Here's context for your task:
- Product: [product from intake]
- Competitive gaps to exploit: [gaps from Module 0, Prompt 2]

Here's your task: For each of the following features — [features from intake] — provide:
1. A detailed description of what the feature is
2. The specific Problem it solves
3. The Benefit of the feature
4. A Dimensionalized benefit: paint vivid word pictures of all the ways the prospect will experience and enjoy that benefit in their daily life, business, and relationships
```

**Prompt 1a — Table format:**
> Organize the output into a table with columns: Feature | Problem Solved | Benefit | Dimensionalized Benefit

---

### Prompt 2 — Unique Mechanism

```
Now, describe how each feature of my product works, step by step. This is the Unique Mechanism.

Your description must include: the problem being solved, the specific actions taken to solve it, and concrete examples of the new outcomes someone experiences. Avoid anything a competitor is already claiming — our mechanism must feel genuinely new.
```

---

### Prompt 3 — Name the Unique Mechanism

```
Give me 5 unique-sounding terms, nicknames, metaphors, and analogies that describe the Unique Mechanism for each feature: [features from intake].

Group them by theme. They must sound fascinating, intriguing, and like a new breakthrough discovery — not like existing competitor language.
```

**Prompt 3a — Refine the names:**
> Run again, this time aiming for names that sound like [insert style — e.g., "Alvin Toffler discoveries", "neuroplasticity research breakthroughs", "exploration of the natural world", "NASA engineering terminology"]

---

### Prompt 4 — Mechanism with Story

```
Describe how each Unique Mechanism works and include a real-world example: what someone does, what happens, and what their life or business looks like after. Be descriptive, pictorial, and expressive.
```

**Prompt 4a — Expand on a specific mechanism:**
> Expand on [chosen mechanism name]. Include a real-world story of how it works and what outcomes someone now experiences. Descriptive, pictorial, expressive.
>
> *(Table option: three columns — mechanism, how it works, real-world example)*

**Prompt 4b — Expand with product detail:**
```
Context:
- Mechanism name: [chosen name]
- Problem it addresses: [detail from product guide]
- Benefits: [detail from product guide]

Task: Describe in expressive detail how this mechanism works. Include real-world examples. Focus on emotional benefits, logical outcomes, and business transformation. Be pictorial and specific.
```

---

### Prompt 5 — Expand Mechanism Names

```
Give me 10 unique-sounding terms, nicknames, metaphors and analogies for [chosen mechanism name]. Group by theme. They must sound like breakthrough discoveries, not generic marketing language.
```

> **Chain forward:** Lock in your chosen mechanism name and description. This becomes the `[Unique Mechanism]` input for Module 4 (Value Proposition).

---

## MODULE 2: AVATAR

*Goal: Build a deep emotional and psychological profile of your ideal buyer.*

> **Auto-populate from Research Context:** Use `[avatar from intake]` throughout.
> **Chain from Module 1:** The problems the product solves (Prompt 1) should anchor the avatar's primary problems here.

---

### Prompt 1 — Uncover Primary Desires

```
My Avatar: [avatar from intake]

What are 6 primary, deep emotional and psychological Desires this Avatar experiences? Go beyond surface wants — uncover the identity-level drives, the things they want but rarely say out loud.
```

**Prompt 1a — Refine for financial freedom angle:**
> Rewrite [chosen desire] to emphasize financial freedom rather than financial security. This avatar can pay their bills — they want the freedom to do anything, anytime, without checking a budget.

---

### Prompt 2 — Uncover Primary Problems

```
My Avatar: [avatar from intake]

What are 6 primary, deep emotional and practical Problems this Avatar struggles with? Include both external frustrations (things happening to them) and internal ones (how they feel about themselves as a result).
```

**Prompt 2a — Expand on a problem:**
```
Context: [chosen problem from Prompt 2]

Expand on this problem. Include: the feeling that others have figured it out while they haven't, the exhaustion of trying everything and getting marginal results, the overwhelm from information overload, and the creeping fear that they might be the problem — not the strategies.
```

**Prompt 2b — First person rewrite:**
> Rewrite the above in first person, as if the Avatar is saying it to their spouse in a raw, honest conversation — and then writing it in their private journal at midnight.

---

### Prompt 3 — Uncover Primary Conflict

```
Context:
- Primary Desire: [top desire from Prompt 1]
- Primary Problem: [top problem from Prompt 2]

Express the conflict between this Desire and this Problem. What's in the way? What keeps going wrong? What has the Avatar already tried that hasn't worked? What does the internal struggle sound like in their own head?
```

> **Chain forward:** Save `Primary Desire`, `Primary Problem`, and `Primary Conflict`. These are required inputs for Module 2 Prompt 4 (Master Avatar) and Module 4 (Value Proposition).

---

### Prompt 4 — Master Avatar Prompt

```
You're an expert on human emotions, behavior, and language. You're also a trained market researcher. You detect human behavior, thoughts, and needs from language and express them with clarity, intensity, and empathy.

Context:
- Product: [product from intake]
- Avatar: [avatar from intake]
- Primary Conflict: [conflict from Prompt 3]

Task: Answer the following in detail, with specific and pictorial real-world examples. Use bullet format.

HEAVEN vs. HELL
- Hell: What does life look like without this product? (Specific, visceral, honest)
- Heaven: What does life look like with this product? (Specific, aspirational, earned)

PAINS vs. GAINS
- Pains: What are their fears, frustrations, and anxieties?
- Gains: What are their wants, needs, hopes, and dreams?

SEE, SAY, HEAR, DO
- See: What do they observe in their marketplace, in competitors, in peers?
- Say: What do they say to themselves and others about their situation?
- Hear: What do they hear from family, friends, colleagues, and strangers?
- Do: What are they doing right now that isn't working — and is making things worse?
```

**Prompt 4a — Table format:**
> Organize this into a table: Category | Emotional Detail | Logical/Practical Detail

---

## MODULE 3: MARKET

*Goal: Map where your avatar sits on the Awareness and Sophistication spectrum so you know exactly how to open your copy.*

> **Auto-populate:** Use `[avatar from intake]` and `[product from intake]` throughout.
> **Chain from Module 0:** Use competitor sophistication levels identified in Module 0 to calibrate your own.

---

### Prompt 1 — State of Awareness

```
You're an expert market researcher with deep knowledge of human psychology and buying behavior.

Context:
- Avatar: [avatar from intake]
- Product: [product from intake]

Create a State of Awareness profile using ONLY first-person language — emotional, vivid, human.

For each of the 5 Awareness Categories below, write:
- 4 bullet points describing the emotional state of someone in this category
- 4 bullet points describing the logical/factual state of someone in this category

Categories:
- Unaware: Does not know the problem exists
- Problem-Aware: Knows the problem, doesn't know solutions exist
- Solution-Aware: Knows solutions exist, hasn't found the right one
- Product-Aware: Has heard of my product, hasn't decided to buy
- Most-Aware: Ready to buy, just needs the right offer
```

**Prompt 1a — Show the progression path:**
> For each category, describe what specific experience, message, or trigger moves this avatar from their current category to the next one.

**Prompt 1b** — Rerun Prompt 1 replacing the full product with a specific component or chapter.

**Prompt 1c — Table format:**
> Organize into a table: Category | Emotional State | Logical State | What Moves Them Forward

---

### Prompt 2 — State of Sophistication

```
Context:
- Product: [product from intake]
- Avatar: [avatar from intake]
- Competitive landscape: [key competitor claims from Module 0]

The 5 States of Sophistication (how many similar products/claims has this avatar already seen):
1. First-ever exposure — never heard anything like this
2. Early awareness — heard a little, open and curious
3. Jaded by claims — heard most claims, maybe tried a competitor
4. Burned by promises — tried several, skeptical and defensive
5. Checked out — no longer believes advertising, won't engage

For each state, give me 3 Claims my product can make that would actually land with someone in that state:
- State 1: Simple, direct, bold
- State 2: Dramatized, bigger, better than what they've heard
- State 3: New mechanism — a different process they haven't seen
- State 4: Faster, easier, more certain mechanism that solves what past products missed
- State 5: A new identity — not a better version of what they tried before, but a fundamentally different self
```

---

## MODULE 4: VALUE PROPOSITION

*Goal: Synthesize everything into 4–6 positioning statements that are emotionally resonant, logically sound, and competitor-differentiated.*

> **Chain inputs required:**
> - Unique Mechanism name + description (from Module 1)
> - Primary Conflict (from Module 2, Prompt 3)
> - Competitive gaps (from Module 0, Prompt 2)
> - Avatar desires and pains (from Module 2, Prompt 4)

---

### Prompt 1 — Value Proposition Development

```
Context:
- Product: [product from intake]
- Avatar: [avatar from intake]
- Unique Mechanism: [mechanism from Module 1]
- Primary Conflict: [conflict from Module 2]
- Competitive gaps: [gaps from Module 0]
- Avatar's deepest desire: [top desire from Module 2]
- Avatar's deepest pain: [top pain from Module 2]

Task: Write 4 compelling Value Propositions for this product. Each must:
1. Speak to the avatar's primary desire or pain
2. Reference the unique mechanism (not a generic claim)
3. Sound nothing like what competitors are saying
4. Be detailed, specific, and emotionally resonant — not a tagline
```

**Prompt 1a — Conflict-led rewrite:**
> Rewrite all 4 with the Primary Conflict as the emotional anchor. Open with the conflict, resolve with the product.

**Prompt 1b — Component-specific variation:**
> Rewrite for a specific component of the product: [chosen feature/chapter]. Same structure, but zoom in on that one component's outcome.

---

## MODULE 5: MENTAL MODELS

*Goal: Reframe any research output through a different psychological or strategic lens to unlock fresh angles and unexpected copy hooks.*

Apply to any output from Modules 0–4.

### How to Use

```
Take the following output: [paste any output from earlier modules]

Reframe it using the mental model of [chosen model below].

Show me how this reframing changes the positioning, the emotional angle, or the copy hook. Give me 3 specific examples of how copy or messaging would change under this model.
```

### Mental Model Library

**Emotion-based models** — for changing the emotional register of your copy:
- **Jealousy Tendency** — What does the avatar see others achieving that they want for themselves?
- **Loss Aversion** — Frame around what they're losing every day without this, not what they'll gain
- **Identity Threat** — How does the problem make them question who they are?
- **Social Proof Cascade** — How does seeing others succeed make the avatar feel left behind?

**Logic-based models** — for building rational persuasion:
- **Inversion** — Instead of "here's how to succeed", ask "what guarantees failure?" then position your product as the antidote
- **First Principles** — Strip away all industry assumptions. What is the core truth about what this avatar needs?
- **Second-Order Thinking** — What happens to the avatar 6 months from now if they don't solve this problem?
- **Opportunity Cost** — What are they giving up (time, money, relationships) by NOT solving this now?

**Positioning models** — for market differentiation:
- **Category Creation** — Can the product be positioned as a new category rather than a better version of an existing one?
- **Jobs To Be Done** — What job is the avatar actually hiring this product to do? (May be very different from what the product technically does)
- **The Challenger Sale** — Teach the avatar something they don't know, then position the product as the logical next step
- **Blue Ocean** — What factors does every competitor compete on that could be eliminated or reduced — and what new factors could be introduced?

**Narrative models** — for story-driven copy:
- **The Hero's Journey** — Avatar as hero, problem as the call to adventure, product as the guide/tool
- **Before/After/Bridge** — Vivid before state, aspirational after state, product as the only bridge between them
- **Enemy Framing** — Name the external enemy (a system, a belief, an industry) so the avatar's failure isn't their fault

---

## OUTPUT TEMPLATES

After completing each module, generate a formatted deliverable the user can take directly into a copywriting or strategy session.

### Avatar Profile (after Module 2)

```
Generate a one-page Avatar Profile using everything we've developed. Include:
- Avatar name/title
- One-sentence description
- Top 3 desires (emotional + rational)
- Top 3 problems (external + internal)
- Primary conflict (one paragraph)
- Heaven state (with product)
- Hell state (without product)
- Key language patterns (how they talk about their problem)
- Awareness level: [from Module 3]
- Sophistication level: [from Module 3]

Format it as a clean, structured profile. No jargon. Written as if briefing a copywriter who has never met this customer.
```

---

### Positioning Canvas (after Modules 0, 1, 4)

```
Generate a Positioning Canvas summarizing:
- Product name
- Unique Mechanism (name + one-sentence description)
- Primary competitive gap we're exploiting
- Our State of Sophistication target level + rationale
- 4 Value Propositions (from Module 4)
- Top 3 copy angles (derived from mental models, if run)
- One sentence that no competitor is currently saying — and we can own

Format as a structured one-pager. This becomes the creative brief for all copy.
```

---

### Competitor Comparison Table (after Module 0)

```
Create a competitor comparison table with the following columns:
Competitor | Core Claim | Unique Mechanism | Sophistication Level Targeted | Gap / Weakness | How We're Different

Include a final row for our product.
```

---

## FULL RESEARCH RUN — RECOMMENDED SEQUENCE

For a complete research engagement, follow this order:

| Step | Module | Output |
|------|--------|--------|
| 1 | Intake Interview | Research Context Block |
| 2 | Module 0: Competitor Research | Competitive gap map |
| 3 | Module 1: Product | Unique Mechanism name + story |
| 4 | Module 2: Avatar | Full avatar profile |
| 5 | Module 3: Market | Awareness + Sophistication maps |
| 6 | Module 4: Value Proposition | 4–6 positioning statements |
| 7 | Module 5: Mental Models | 3 fresh copy angles |
| 8 | Output Templates | Avatar Profile + Positioning Canvas + Competitor Table |

Each module feeds the next. Never skip the intake — it eliminates all manual placeholder work.
