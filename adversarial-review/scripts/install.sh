#!/usr/bin/env bash
# adversarial-review skill installer (macOS / Linux / Git Bash / WSL)
set -euo pipefail

SKILL_NAME="adversarial-review"
REPO_URL="https://github.com/RevolutionLA/adversarial-review.git"
# skills.sh 结构：skill 位于仓库的 skills/<name>/ 子目录
SKILL_SUBPATH="skills/${SKILL_NAME}"
DEFAULT_DIR="${HOME}/.claude/skills"
TARGET_DIR="${1:-$DEFAULT_DIR}"
TARGET_DIR="${TARGET_DIR%/}"   # 去尾部斜杠，保证父目录推导稳定
DEST="${TARGET_DIR}/${SKILL_NAME}"
# 备份必须落在 skills 目录之外：留在 skills 内的 `.bak.*` 目录带着同名
# frontmatter（name: adversarial-review），会与主 skill 抢触发路由，
# 命中即回退旧流程（v2.1 三方评审 B4/T6 实证的缺陷）。
BACKUP_ROOT="$(dirname "${TARGET_DIR}")/skill-backups"

info()  { printf '\033[36m[info]\033[0m %s\n' "$1"; }
ok()    { printf '\033[32m[ ok ]\033[0m %s\n' "$1"; }
warn()  { printf '\033[33m[warn]\033[0m %s\n' "$1"; }
fail()  { printf '\033[31m[fail]\033[0m %s\n' "$1" >&2; exit 1; }

info "installing ${SKILL_NAME} -> ${DEST}"
mkdir -p "${TARGET_DIR}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

if command -v git >/dev/null 2>&1; then
  git clone --depth 1 "${REPO_URL}" "${TMP_DIR}/repo" >/dev/null 2>&1 \
    || fail "git clone failed. Check network access to ${REPO_URL}"
else
  command -v curl >/dev/null 2>&1 || fail "need git or curl to install"
  warn "git not found, falling back to tarball download"
  curl -fsSL "https://codeload.github.com/RevolutionLA/${SKILL_NAME}/tar.gz/refs/heads/main" \
    -o "${TMP_DIR}/skill.tar.gz" || fail "download failed"
  mkdir -p "${TMP_DIR}/repo"
  tar -xzf "${TMP_DIR}/skill.tar.gz" -C "${TMP_DIR}/repo" --strip-components=1
fi

SRC="${TMP_DIR}/repo/${SKILL_SUBPATH}"
[ -f "${SRC}/SKILL.md" ] || fail "SKILL.md not found at ${SKILL_SUBPATH} — repo layout may have changed"

# 读取远端版本，便于用户判断是否真的更新了
NEW_VER="$(sed -n 's/^  version:[[:space:]]*//p' "${SRC}/SKILL.md" | head -n 1 | tr -d '\r"')"

# 已有安装：备份而不是直接删除（用户可能有本地自定义修改）
if [ -d "${DEST}" ]; then
  OLD_VER=""
  [ -f "${DEST}/SKILL.md" ] && OLD_VER="$(sed -n 's/^  version:[[:space:]]*//p' "${DEST}/SKILL.md" | head -n 1 | tr -d '\r"')"
  BACKUP="${BACKUP_ROOT}/${SKILL_NAME}.bak.$(date +%Y%m%d%H%M%S)"
  warn "existing install found (version: ${OLD_VER:-unknown})"
  info "backing up to ${BACKUP} (outside the skills dir, not deleting — your local edits are preserved there)"
  mkdir -p "${BACKUP_ROOT}"
  mv "${DEST}" "${BACKUP}"
  info "new version: ${NEW_VER:-unknown}"

  # 备份只保留最近 3 份（评审 R13）：重复安装是常态，无限增长的 .bak.<时间戳>
  # 会悄悄吃掉磁盘。只清理本脚本自己命名出来的备份，别的一律不碰。
  KEEP_BACKUPS=3
  old_backups="$(ls -1 "${BACKUP_ROOT}" 2>/dev/null | grep "^${SKILL_NAME}\.bak\." | sort -r || true)"
  to_prune="$(printf '%s\n' "$old_backups" | tail -n +$((KEEP_BACKUPS + 1)))"
  if [ -n "$to_prune" ]; then
    while IFS= read -r stale; do
      [ -n "$stale" ] || continue
      rm -rf "${BACKUP_ROOT}/${stale}" && info "pruned old backup (kept newest ${KEEP_BACKUPS}): ${stale}"
    done <<< "$to_prune"
  fi
fi

mkdir -p "${DEST}"
cp -R "${SRC}/." "${DEST}/"

# sanity check: frontmatter name must match directory name (Agent Skills spec)
HEAD_NAME="$(sed -n 's/^name:[[:space:]]*//p' "${DEST}/SKILL.md" | head -n 1 | tr -d '\r')"
[ "${HEAD_NAME}" = "${SKILL_NAME}" ] || fail "frontmatter name '${HEAD_NAME}' != directory '${SKILL_NAME}'"

ok "installed: ${DEST} (version ${NEW_VER:-unknown})"
ok "frontmatter name verified: ${HEAD_NAME}"
printf '\nNext: restart your agent, then say "跑一次蓝军评审" or "adversarial review this module".\n'
