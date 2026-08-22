---
name: delta-force-tune
description: Windows system-layer frame-rate optimization for Delta Force (三角洲行动) with AI agent support — reversible optimizations, health checks, and A/B auto-tuning.
---

# Delta Force Tune

## When to Use This Skill

- User complains about Delta Force stuttering, low FPS, or frame drops on Windows 10/11
- User asks for system-level game optimization that is reversible and safe
- User wants measured A/B comparison of tuning groups instead of guesswork

## What This Skill Does

1. **Detect** — reads hardware, finds the game install, and reports the current
   state of 22 Windows-layer optimizations (read-only, safe)
2. **Apply** — after explicit user consent, applies the chosen optimizations with
   write-ahead backups
3. **Restore** — restores every change to its exact original value, per item or all
   at once
4. **Health check** — read-only checks for missing VC++ runtimes, memory frequency,
   and PCIe link status
5. **A/B auto-tune** — measures a baseline and candidate groups with PresentMon and
   keeps or reverts them by rule (avg FPS / 1% low / P99 / stutters)

## How to Use

### Basic Usage

```
Clone https://github.com/jiaxindeyang-a11y/delta-force-tune, then:
powershell -NoProfile -ExecutionPolicy Bypass -File delta-optimizer.ps1 -Detect -Json
```

### Advanced Usage

```
powershell -NoProfile -ExecutionPolicy Bypass -File delta-optimizer.ps1 -Apply -Preset balanced -Force -Json
powershell -NoProfile -ExecutionPolicy Bypass -File delta-optimizer.ps1 -Restore -Json
powershell -NoProfile -ExecutionPolicy Bypass -File tuning-experiment.ps1 -Baseline -Json
powershell -NoProfile -ExecutionPolicy Bypass -File tuning-experiment.ps1 -Test -Group group-1 -Json
```

## Example

**User**: "游戏掉帧严重，帮我优化三角洲行动"

**Output**:
```
Agent detects hardware + game path, lists 22 items with current state, gets consent,
applies the balanced preset, reports ok/failed/skipped + reboot list + backup path.
```

## Tips

- Keep the same map/quality/route during A/B sampling
- Reboot after applying items flagged `reboot: true`
- Install Microsoft PresentMon yourself (`winget install Microsoft.PresentMon`) —
  the tool never installs things for you
- Red lines: no game-file edits, no process injection, no anti-cheat interaction,
  no virtualization toggling, no GPU model spoofing

## Common Use Cases

- FPS / stutter optimization for Delta Force on Windows
- Reversible Windows gaming tweaks with full restore
- Data-driven A/B comparison of tuning groups
