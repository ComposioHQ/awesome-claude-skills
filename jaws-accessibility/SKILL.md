---
name: jaws-accessibility
description: Accessibility engineering skill for web products with JAWS/NVDA screen reader testing, WCAG 2.2 compliance, and Spain/EU legislation guidance (Ley 11/2023, EAA, EN 301 549).
---

# JAWS Accessibility Skill

Practical, implementation-first accessibility engineering for web interfaces. Covers WCAG 2.2 compliance, screen reader testing with JAWS and NVDA, keyboard navigation, ARIA patterns, and Spanish/EU accessibility legislation.

## When to Use This Skill

- Implementing WCAG 2.2 AA compliance for web components
- Testing and fixing screen reader issues with JAWS or NVDA
- Keyboard and focus management in SPAs (React, Next.js, Vue)
- Accessibility audits with structured severity reporting
- Spanish/EU legal compliance checks (Ley 11/2023, RD 1112/2018, EAA, EN 301 549)
- Remediating ARIA anti-patterns and semantic HTML issues

## What This Skill Does

1. **Screen Reader Testing**: Validates behavior across JAWS + Chrome and NVDA + Firefox, including known version-specific bugs
2. **WCAG 2.2 Implementation**: Maps each finding to specific Success Criteria with code fixes
3. **Legal Compliance**: Covers Spanish (Ley 11/2023, RD 1112/2018) and EU (European Accessibility Act, EN 301 549) requirements with exact dates and scope
4. **Audit Methodology**: 8-phase structured audit with findings grouped by Critical/High/Medium/Low severity
5. **Focus Management**: SPA-specific patterns for route changes, modals, live regions, and status announcements

## How to Use

### Basic Usage — Fix a component

```
This modal is not accessible with JAWS. Fix the focus trap, Escape key handling, and aria attributes.
```

### Advanced Usage — Full audit

```
Run a JAWS accessibility audit on the /transparency page. Use the 8-phase methodology and report findings by severity with WCAG SC mapping.
```

### Legal scope check

```
Does Ley 11/2023 apply to a private foundation website in Spain? What are the deadlines?
```

## Example

**User**: "The backdrop overlay in our mobile menu closes on click but JAWS users can't dismiss it."

**Output**:
```
Impact: JAWS users have no keyboard mechanism to dismiss the overlay.

Root cause: The backdrop is a <div> with only onClick — no keyboard handler, no role, no aria-hidden.

Fix:
<div
  role="presentation"
  onClick={() => setIsOpen(false)}
  aria-hidden="true"
/>

The Escape key dismiss should be handled by the focus trap hook (useFocusTrap),
not by the backdrop element itself.

Manual test:
1. JAWS + Chrome: Open menu → Tab through items → press Escape → verify focus returns to trigger
2. NVDA + Firefox: Same flow → verify no ghost focus on backdrop
```

## Tips

- Always prioritize native HTML semantics (`<button>`, `<nav>`, `<dialog>`) before ARIA
- NVDA is the strict standards-compliance reference; JAWS has more real-world market share
- Do not rely on `aria-current` or `aria-description` inside `role="grid"` rows — JAWS 2025+ has known bugs
- Inject `aria-live` containers empty in initial HTML, then populate — JAWS ignores regions injected with content simultaneously

## Common Use Cases

- Making React/Next.js SPAs screen-reader accessible
- Fixing focus management after client-side route changes
- Resolving ARIA anti-patterns flagged by axe-core or Lighthouse
- Preparing websites for European Accessibility Act (EAA) compliance
- Auditing against WCAG 2.2 AA with JAWS/NVDA manual testing
- Ensuring cookie consent banners and modals are keyboard-operable

## Full Skill Repository

The complete skill with reference files (WCAG criteria, JAWS/NVDA compatibility matrix, audit methodology, legislation guide) is available at: [Ambitos-1995/jaws-accessibility-skill](https://github.com/Ambitos-1995/jaws-accessibility-skill)

**Credit:** Built by [Fundación Ámbitos](https://github.com/Ambitos-1995), a Spanish mental health foundation, from real-world accessibility remediation of their production website.
