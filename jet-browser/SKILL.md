---
name: jet-browser
description: Install, verify, integrate, or troubleshoot the Jet Browser WPE WebKit runtime when a project needs an isolated browser process, ordered JSONL automation, native input, semantic DOM inspection, screenshots, or framework-neutral browser tools.
---

# Jet Browser

Use Jet Browser as a replaceable browser-runtime boundary. Keep model choice, agent reasoning, credentials, and orchestration in the calling project.

## When to use this skill

- Add a real browser runtime to an agent or deterministic test harness without adopting a bundled agent framework.
- Give each untrusted task an isolated browser process with explicit resource and profile ownership.
- Drive navigation, native pointer and keyboard input, semantic DOM inspection, JavaScript, tabs, downloads, and screenshots through ordered JSONL.
- Reproduce browser startup and interaction checks in local development or CI.
- Diagnose a Jet Browser installation or integration that does not pass its standalone acceptance flow.

Do not use this skill to control an already-running personal Chrome profile. Jet Browser is based on WPE WebKit, not Chromium, and does not provide Chrome extensions or CDP compatibility.

## Prerequisites

Check for Docker and Node.js 24 or newer before starting. If either is unavailable, report the missing requirement instead of claiming that verification succeeded.

## Setup and verification

1. Reuse an existing Jet Browser checkout when the project already contains one. Otherwise clone `https://github.com/masakaai/jet-browser` and keep the checkout location explicit.
2. Read `README.md`, `docs/demo.md`, and `docs/agent-tools.md` before changing the integration boundary.
3. Run `npm ci`, then `npm run standalone`.
4. Treat the command's JSON result as the acceptance check. The local page, JavaScript marker, native text input, semantic DOM state, PNG capture, browser-network isolation, and clean shutdown must all pass.
5. For source changes, also run `npm test` and `cargo test --all-targets`.

Never convert partial output into a success claim. Preserve the failing stage and the relevant command output when reporting a problem.

## Integration rules

- Prefer the versioned tool declarations exported by `sdk/tools.mjs`; do not invent tool names or response fields.
- Send one JSON command per line and consume one JSON response per line. Preserve ordering and always close the session in guaranteed cleanup.
- Keep one isolated browser session per container. Mount profile or download paths explicitly and never pass unrelated host credentials into the container.
- Use semantic evidence for target selection and a fresh screenshot for visual verification when both are available.
- Treat JavaScript evaluation, imported profiles, downloads, and outbound network access as privileged capabilities controlled by the embedding harness.
- Pin a tagged image digest for production. The published image currently targets `linux/amd64`; ARM hosts require compatible emulation or a native source build.

## Product and benchmark boundaries

Jet Browser is local or self-hosted browser infrastructure. It is not an agent framework, anti-bot service, hosted proxy network, or managed control plane.

Benchmark claims must retain their scope. The published 1,445.25 ms verified-ready time and 189.6 MiB active memory are medians from a pinned offline fixture. They do not measure public-site success, stealth, CAPTCHA handling, model accuracy, or long-running stability. Consult the published method and raw samples before repeating a number.

## Example prompts

### Verify an installation

```text
Install Jet Browser in this repository, confirm Docker and Node.js 24+, run the standalone acceptance flow, and report each verified stage. Do not attach to my daily Chrome profile.
```

### Add it beneath an existing agent

```text
Integrate Jet Browser as the replaceable browser runtime for this harness. Reuse the versioned tool schemas, keep one session per container, preserve ordered JSONL responses, and add guaranteed cleanup plus an offline smoke test.
```

### Troubleshoot a failure

```text
Diagnose why Jet Browser's standalone check fails here. Identify the first failing stage, preserve the actual evidence, and do not weaken network isolation or sandbox settings to make the check pass.
```

## Expected result

A successful task should leave behind:

- an explicit Jet Browser checkout or pinned runtime reference;
- a passing standalone JSON acceptance result;
- integration code that uses the published schemas and ordered JSONL contract;
- bounded session, profile, network, and cleanup behavior; and
- a report that separates observed evidence from unverified assumptions.

**Source and attribution:** [Jet Browser](https://github.com/masakaai/jet-browser), maintained by the MASAKA project under Apache-2.0.
