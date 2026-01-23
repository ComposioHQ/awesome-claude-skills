# Installation Guide

Complete installation instructions for planning-with-files.

## Quick Install (Recommended)

```bash
/plugin marketplace add OthmanAdi/planning-with-files
/plugin install planning-with-files@planning-with-files
```

That's it! The skill is now active.

---

## Installation Methods

### 1. Claude Code Plugin (Recommended)

Install directly using the Claude Code CLI:

```bash
/plugin marketplace add OthmanAdi/planning-with-files
/plugin install planning-with-files@planning-with-files
```

**Advantages:**
- Automatic updates
- Proper hook integration
- Full feature support

---

### 2. Manual Installation

Clone or copy this repository into your project's `.claude/plugins/` directory:

#### Option A: Clone into plugins directory

```bash
mkdir -p .claude/plugins
git clone https://github.com/OthmanAdi/planning-with-files.git .claude/plugins/planning-with-files
```

#### Option B: Add as git submodule

```bash
git submodule add https://github.com/OthmanAdi/planning-with-files.git .claude/plugins/planning-with-files
```

#### Option C: Use --plugin-dir flag

```bash
git clone https://github.com/OthmanAdi/planning-with-files.git
claude --plugin-dir ./planning-with-files
```

---

### 3. Legacy Installation (Skills Only)

If you only want the skill without the full plugin structure:

```bash
git clone https://github.com/OthmanAdi/planning-with-files.git
cp -r planning-with-files/skills/* ~/.claude/skills/
```

---

### 4. One-Line Installer (Skills Only)

Extract just the skill directly into your current directory:

```bash
curl -L https://github.com/OthmanAdi/planning-with-files/archive/master.tar.gz | tar -xzv --strip-components=2 "planning-with-files-master/skills/planning-with-files"
```

Then move `planning-with-files/` to `~/.claude/skills/`.

---

## Verifying Installation

After installation, verify the skill is loaded:

1. Start a new Claude Code session
2. You should see: `[planning-with-files] Ready. Auto-activates for complex tasks, or invoke manually with /planning-with-files`
3. Or type `/planning-with-files` to manually invoke

---

## Updating

### Plugin Installation

```bash
/plugin update planning-with-files@planning-with-files
```

### Manual Installation

```bash
cd .claude/plugins/planning-with-files
git pull origin master
```

### Skills Only

```bash
cd ~/.claude/skills/planning-with-files
git pull origin master
```

---

## Uninstalling

### Plugin

```bash
/plugin uninstall planning-with-files@planning-with-files
```

### Manual

```bash
rm -rf .claude/plugins/planning-with-files
```

### Skills Only

```bash
rm -rf ~/.claude/skills/planning-with-files
```

---

## Requirements

- **Claude Code:** v2.1.0 or later (for full hook support)
- **Older versions:** Core functionality works, but hooks may not fire

---

## Platform-Specific Notes

### Windows

See [docs/windows.md](windows.md) for Windows-specific installation notes.

### Cursor

See [docs/cursor.md](cursor.md) for Cursor IDE installation.

---

## Need Help?

If installation fails, check [docs/troubleshooting.md](troubleshooting.md) or open an issue at [github.com/OthmanAdi/planning-with-files/issues](https://github.com/OthmanAdi/planning-with-files/issues).
