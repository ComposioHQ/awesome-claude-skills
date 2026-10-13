---
name: localscreenshot
description: Take a screenshot of any public web page, as an image or a PDF, from one of 227 countries, with cookie banners and ads hidden. Use when a page has to be seen as a real visitor sees it and no browser is available.
---

# localscreenshot

One command returns a picture of a public page. The browser runs on the service, not on this machine, so nothing has to be installed and no page is loaded locally.

## When to Use This Skill

- A user asks what a page looks like, or asks for a screenshot of a site, and no browser is available here.
- A page has to be checked before or after a deploy, and the result kept next to the code.
- A page has to be seen the way visitors in another country get it.
- A PDF of a page is needed for a report, an archive or an attachment.
- A page has to be checked for a cookie wall, a redirect, or a bot check instead of its content.

## What This Skill Does

1. **Captures**: returns the rendered page as `png`, `jpeg`, `webp` or `pdf`.
2. **Renders from a country**: one of 227, and the answer reports the country that was actually observed.
3. **Cleans the page before the picture**: cookie banners, ads and chat widgets can be hidden.
4. **Reports the cost**: the command prints the credits used and left, and a failed screenshot is not charged.
5. **Fails with a code**: a bot check comes back as `challenge_page`, never as a blank image.

## How to Use

### Basic Usage

```
Take a screenshot of example.com and save it in ./shots/
```

Claude runs:

```bash
npx -y localscreenshot https://example.com -o shots/home.png
```

Which prints:

```text
Saved /work/shots/home.png
1440 x 900, 88,627 bytes
Credits: 1 used, 47 left
```

### Advanced Usage

```
Screenshot the pricing page of example.com as a full-page PDF, as a visitor in Germany, for the report folder.
```

```bash
npx -y localscreenshot https://example.com/pricing --full-page --format pdf --country DE -o report/pricing-de.pdf
```

### Setup

The command needs a key, and the same key serves the API, the command line and the MCP server.

```bash
export LOCALSCREENSHOT_API_KEY="your key"
# or, once per machine:
npx -y localscreenshot login
```

Without a key the command exits with code 2 and sends nothing. Ask the user for one rather than retrying.

### Options worth knowing

| Option | What it does |
| --- | --- |
| `--country <code>` | Load the page from a two-letter country, `DE`, `BR`, `JP`, out of 227. |
| `--full-page` | Capture the whole page, not only the first screen. |
| `--format <format>` | `png` (default), `jpeg`, `webp` or `pdf`. |
| `--device <name>` | Screen to render on, for example `iphone_15`, `ipad`, `desktop_hd`. |
| `--click-text <text>` | Click the single element a visitor reads as this text, then capture. |
| `--no-cookie-banners`, `--no-ads` | Hide them before the picture is taken. |
| `--dark` | Render in dark mode. |
| `-o <file>` | Where to write the image. An existing file is never overwritten without `--force`. |
| `--json` | Print the raw API answer, including the saved path. |

`npx -y localscreenshot countries` lists the countries and needs no key.

## Example

**User**: "the layout looks broken on our pricing page, can you check?"

**Output**: Claude captures the page, opens the image, and answers from what it sees.

```bash
npx -y localscreenshot https://example.com/pricing -o pricing.png
```

```text
Saved /work/pricing.png
1440 x 900, 132,014 bytes
Credits: 1 used, 46 left
```

After the fix, one more capture shows the correction. Keeping both files is enough to show a before and after.

## Tips

- Ask for `--full-page` when the question concerns content further down, the default is the first screen only.
- With the same `-o` name, the second run exits with 2 before sending anything, so nothing is spent by accident. Add `--force` to replace the file.
- A capture from a chosen country costs two credits instead of one.
- `challenge_page` means the site served a bot check. Report that instead of describing a page that was never seen.
- The tool reads public pages only. It does not sign in, solve CAPTCHAs or get past paywalls, so do not promise any of those.

**Credit:** Built by Softlogic around its own screenshot service and command line client.

## Common Use Cases

- Visual check of a page after a deploy, with the capture kept next to the code.
- Report or archive: a PDF of a page as it stood on a given day.
- Localised check: how a page renders for a visitor in another country.
- Answering a user who asks what a site looks like, without a browser on this machine.
