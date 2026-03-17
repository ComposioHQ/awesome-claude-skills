#!/bin/bash
# ================================================
# Claude Code Skills Setup - Android (Termux)
# Usage: bash install.sh
# ================================================

set -e

REPO="https://github.com/makladmk87-max/awesome-claude-skills"
SKILLS_DIR="$HOME/.claude/skills"
REPO_DIR="$HOME/awesome-claude-skills"

echo "==> Setting up Claude Code skills on Android..."

# ── 1. Install dependencies (Termux) ──────────────────────────────────────────
if command -v pkg &>/dev/null; then
  echo "==> Installing packages via Termux..."
  pkg update -y
  pkg install -y git nodejs
elif command -v apt-get &>/dev/null; then
  echo "==> Installing packages via apt..."
  apt-get update -y
  apt-get install -y git nodejs npm
fi

# ── 2. Install Claude Code CLI ─────────────────────────────────────────────────
if ! command -v claude &>/dev/null; then
  echo "==> Installing Claude Code CLI..."
  npm install -g @anthropic-ai/claude-code
else
  echo "==> Claude Code already installed: $(claude --version)"
fi

# ── 3. Clone or update the skills repo ────────────────────────────────────────
if [ -d "$REPO_DIR/.git" ]; then
  echo "==> Updating existing repo..."
  git -C "$REPO_DIR" pull
else
  echo "==> Cloning skills repo..."
  git clone "$REPO" "$REPO_DIR"
fi

# ── 4. Link skills into ~/.claude/skills ──────────────────────────────────────
mkdir -p "$SKILLS_DIR"

echo "==> Installing skills..."
for skill_dir in "$REPO_DIR"/*/; do
  skill_name=$(basename "$skill_dir")
  skill_file="$skill_dir/SKILL.md"

  # Skip non-skill directories
  if [ ! -f "$skill_file" ]; then
    continue
  fi

  target="$SKILLS_DIR/$skill_name.md"
  cp "$skill_file" "$target"
  echo "    + $skill_name"
done

echo ""
echo "✓ Done! Skills installed to $SKILLS_DIR"
echo ""
echo "To use Claude Code, run: claude"
echo "To update skills later, run: bash $REPO_DIR/install.sh"
