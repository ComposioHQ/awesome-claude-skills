# Advanced Reveal.js Features

These features are available if the user specifically requests them. They are not used by default.

## Fragments (Progressive Reveal)

Show content step-by-step on click:

```html
<p class="fragment">Appears on click</p>
<p class="fragment fade-up">Slides up</p>
<p class="fragment highlight-red">Turns red</p>
```

Fragment animations:
- `fade-in` (default)
- `fade-out`
- `fade-up`, `fade-down`, `fade-left`, `fade-right`
- `highlight-red`, `highlight-green`, `highlight-blue`
- `strike` (strikethrough)

## Speaker Notes

Add private notes visible only in speaker view (press `S` to open):

```html
<section>
  <h2>Slide Title</h2>
  <p>Visible content</p>
  <aside class="notes">
    Private notes for the presenter.
    - Remember to mention X
    - Transition to next topic
  </aside>
</section>
```

## Backgrounds

### Solid Color
```html
<section data-background-color="#283b95">
```

### Image
```html
<section data-background-image="image.jpg">
<section data-background-image="image.jpg" data-background-opacity="0.5">
<section data-background-image="image.jpg" data-background-size="contain">
```

### Gradient
```html
<section data-background-gradient="linear-gradient(to bottom, #283b95, #17b2c3)">
<section data-background-gradient="radial-gradient(#283b95, #17b2c3)">
```

## Auto-Animate

Automatically animate elements between slides. Elements with matching `data-id` attributes will transition smoothly:

```html
<section data-auto-animate>
  <h1>Title</h1>
</section>
<section data-auto-animate>
  <h1>Title</h1>
  <h2>Subtitle appears with animation</h2>
</section>
```

More complex example with matching elements:

```html
<section data-auto-animate>
  <div data-id="box" style="width: 100px; height: 100px; background: blue;"></div>
</section>
<section data-auto-animate>
  <div data-id="box" style="width: 300px; height: 150px; background: red;"></div>
</section>
```

## Transitions

Set per-slide transitions:

```html
<section data-transition="fade">
<section data-transition="slide">
<section data-transition="convex">
<section data-transition="concave">
<section data-transition="zoom">
<section data-transition="none">
```

Different in/out transitions:
```html
<section data-transition="slide-in fade-out">
```

## Slide Visibility

Hide slides from normal flow (accessible via URL only):
```html
<section data-visibility="hidden">
```

Skip slides in navigation but keep visible:
```html
<section data-visibility="uncounted">
```

## Code Highlighting

Basic syntax highlighting:
```html
<pre><code class="language-python">
def hello():
    print("Hello")
</code></pre>
```

Supported languages: `javascript`, `python`, `html`, `css`, `java`, `ruby`, `go`, `rust`, `sql`, `bash`, `json`, `yaml`, and many more.

**Line highlighting (step-through on click):**
```html
<pre><code data-line-numbers="1-2|3|4">
let a = 1;
let b = 2;
let c = x => 1 + 2 + x;
c(3);
</code></pre>
```

This highlights lines 1-2 first, then line 3 on click, then line 4.

**Static line highlighting (no step-through):**
```html
<pre><code data-line-numbers="3,5-7">
...
</code></pre>
```
