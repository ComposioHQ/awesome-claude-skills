---
name: carry-discipline
description: >
  Build explainer videos where every beat grows out of the one before, and prove it with a
  gate that fails replacement. Use when a motion video reads as a slideshow, when scenes
  "replace" each other instead of continuing, when a video looks like slides with animation,
  or when reviewing a faceless/explainer video for craft. Encodes the carry discipline: at
  every beat boundary something on screen must SURVIVE and visibly become the next beat.
  Original implementation written from scratch — no third-party code is vendored, so
  nothing here carries an upstream licence.
---

# Carry discipline

A faceless animated video usually fails the same way: **the slides are fine, the seams
between them don't exist.** Title card, fade, UI shot, fade, feature card, logo. Each beat
looks competent in isolation and the whole thing reads as a deck.

The defect is not rhythm. It is that beat *n+1* **replaces** beat *n* instead of continuing
from it. Nothing crosses the boundary.

## The one rule

> At every beat boundary, name the thing that survives it and visibly becomes the next beat.

If you cannot name it, it is a slide change — whatever the pacing, however good each
individual beat is. That is the whole discipline. Everything below is how to write it and
how to catch yourself failing it.

## Write the carry chain before you build anything

One sentence, in the comp's header comment:

```
CARRY: <element A> -> <element B> -> <element C> -> ... -> <element A again>
```

Each arrow must be a **transformation of the same thing**, not a swap. Good arrows:

- a bar **opens into** an app window; the window **reflows into** the phone
- a card **grows into** the page; the camera **pushes through** the card until it *is* the page
- a bar **collapses into** a line; the line **shoots across** and **becomes** the first grid line
- a stack of rows **gathers** into one node; the node **opens into** the wordmark
- the cast **folds into** the lockup

Not arrows: `slide -> diagram`, `diagram -> terminal`, `card -> card`. Those are replacements.

**Returning to the first element at the end is what closes the chain** and gives the film a
shape instead of a list.

## Per-boundary checklist

For each boundary in the beat sheet, all three must be true:

1. **Identity** — the same object is still on screen on both sides of the cut.
2. **Visible motion** — it moves or scales across the boundary. Not a cut; a transition.
3. **Transformation** — its shape at *t+1* is derived from its shape at *t−1* (rect → rect,
   row → row, dot → glyph).

`display:none` swaps, crossfades, and mutually exclusive scenes fail all three, no matter
how good the rhythm is.

## Rhythm (secondary, and easy to get wrong)

- **Vary shot length by ≥4×.** 0.25s next to 2.5s. Uniform cadence reads as slides even
  when every shot is beautiful.
- **Never cut on a metronome.** Equal intervals are the single most common tell.
- **Include a real rest.** The frame must be still sometimes — roughly a third of the time.
  Rests are what make the bursts land. A frame that is always in motion reads as waiting.
- **Bare hard cuts** belong only to bursts of hits and the end card. Everywhere else, carry.

## Small elements, big ground

The frame is mostly empty. Full-bleed is the exception, not the rule. If the subject fills
the frame there is nowhere for it to go and nothing for a carry to travel across.

**Ground is never a black void.** A lit surface with depth — paper, tabletop, a soft gradient
— gives shapes somewhere to sit and gives the camera somewhere to travel. A flat black field
with outlines floating in it is the most recognisable signature of unproduced motion graphics.

## Motion that earns its place

- Every animated element must do one of: **give feedback**, **show a relationship**, or
  **direct attention**. Anything else, cut it. Decorative motion is not neutral — it measurably
  *reduces* comprehension (`seductive details`, g = −0.37).
- **No idle loops.** Sine pulses, breathing glows, drifting particles. If the scene finished
  entering and has seconds left, that is a *planning* bug: add story, not wobble.
- At most **one** ambient loop on screen at a time.
- Entrances start at **scale 0.9–0.93**, never 0.
- **ease-out** by default (`cubic-bezier(.23,1,.32,1)`); stagger ≤50ms; overlapping action
  beats everything landing on the same frame.
- Fast moves need real motion blur — multi-sample averaged, not CSS `blur()`.

## Text

- Type on screen is not the picture. If the narration could carry the frame with the image
  deleted, the image is missing.
- Three type levels maximum: claim, term, annotation. Never a body-paragraph level in-frame.
- For long-form: 1–3 word keyword pops timed to the spoken word, **not** burned-in full
  sentences (measured: zero burned-in captions across 502 frames of top long-form).
- For Shorts: burned captions, one emphasis mechanism per video, never mixed.

## Verify before showing

Do not ship on vibes. Measure carry and rhythm **on the rendered MP4** with a gate that
fails replacement. It reports, per beat boundary, whether the subject's screen region
**persists** across the cut (`carry score`), plus shot-length variation and rest coverage.
A film whose beats replace each other fails, regardless of how it feels. If your pipeline
has a gate script, wire it in; if not, check the boundaries by hand against the checklist
above.

## The trap that will fool you

A gate can go green while the video is ugly. Carry score 1.00 proves continuity, not taste.
Before shipping, also:
1. Read actual frames at 5+ timestamps. Look at them.
2. Compare against a reference you have watched, frame for frame.
3. Ask whether the ground is lit and whether the palette is more than two colours.
