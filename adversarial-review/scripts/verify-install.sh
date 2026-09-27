#!/usr/bin/env bash
# 验证 adversarial-review skill 是否安装成功
set -uo pipefail

SKILL_NAME="adversarial-review"
# 显式清单只覆盖"写清单时想到的宿主"。v2.5 轮换安装根时实测：Codex 的根
# （~/.codex/skills）不在清单里，多根一致性检查于是静默跳过一份陈旧副本，
# 照样打印"✅ 全部安装根版本一致"——v2.1 T1 那条"只验第一个命中根"的缺陷
# 换了个位置复活。所以清单之外再做一层点目录发现：宿主根都在 $HOME 的
# 一层隐藏目录下（.claude/.codex/.cursor/.qoder/.trae/...），glob 不递归，成本恒定。
EXPLICIT=(
  "${HOME}/.claude/skills/${SKILL_NAME}"
  "${HOME}/.agents/skills/${SKILL_NAME}"
  "${HOME}/.codex/skills/${SKILL_NAME}"
  "${HOME}/.dsh/skills/${SKILL_NAME}"
  "${HOME}/.config/agents/skills/${SKILL_NAME}"
)

CANDIDATES=()
for c in "${EXPLICIT[@]}" "${HOME}"/.*/skills/"${SKILL_NAME}"; do
  [ -f "${c}/SKILL.md" ] || continue
  real="$(cd "$c" 2>/dev/null && pwd -P)" || continue
  dup=0
  for r in "${CANDIDATES[@]}"; do
    [ "$r" = "$real" ] && { dup=1; break; }
  done
  [ "$dup" -eq 0 ] && CANDIDATES+=("$real")
done

FOUND=""

# 显式指定的路径优先，且要在"自动查找失败"之前生效
if [ -n "${1:-}" ]; then
  if [ -f "${1}/SKILL.md" ]; then
    FOUND="$1"
  else
    echo "✗ 指定路径下没有 SKILL.md: $1"
    exit 1
  fi
fi

if [ -z "$FOUND" ]; then
  for c in "${CANDIDATES[@]}"; do
    FOUND="$c"; break
  done
fi

if [ -z "$FOUND" ]; then
  echo "✗ 未找到 ${SKILL_NAME}，已检查以下位置："
  for c in "${EXPLICIT[@]}"; do echo "    - $c"; done
  echo "    - ${HOME}/.*/skills/${SKILL_NAME}（自动发现各宿主的点目录安装根）"
  echo ""
  echo "请先安装，或手动指定路径: bash scripts/verify-install.sh /your/skills/dir"
  exit 1
fi

echo "发现安装位置: $FOUND"
echo "核对安装根: ${#CANDIDATES[@]} 个"
echo ""

# 0. 多安装根版本一致性（v2.1 T1：一个根装了新版、另一个根仍是旧版时，
# 只验第一个命中根会对着陈旧副本报"通过"）
if [ -z "${1:-}" ]; then
  VER_SEEN=""
  for c in "${CANDIDATES[@]}"; do
    [ -f "${c}/SKILL.md" ] || continue
    v="$(sed -n 's/^  version:[[:space:]]*//p' "${c}/SKILL.md" | head -n 1 | tr -d '\r" ')"
    if [ -n "$VER_SEEN" ] && [ -n "$v" ] && [ "$v" != "$VER_SEEN" ]; then
      echo "✗ 版本漂移：$c 为 $v，另一安装根为 $VER_SEEN —— 请把**所有**安装根同步到同一版本后再验证"
      exit 1
    fi
    [ -n "$v" ] && VER_SEEN="$v"
  done
  if [ -n "$VER_SEEN" ]; then
    echo "✅ 全部安装根版本一致（$VER_SEEN）"
  else
    echo "·  安装根中未读到 version 字段，跳过多根一致性判断"
  fi
fi

fail=0
SPEC_CHECKED=0

# 1. SKILL.md 存在且非空
if [ -s "${FOUND}/SKILL.md" ]; then
  echo "✅ SKILL.md 存在 ($(wc -l < "${FOUND}/SKILL.md") 行)"
else
  echo "✗ SKILL.md 缺失或为空"; fail=1
fi

# 2. frontmatter name 与目录名一致
head_name="$(sed -n 's/^name:[[:space:]]*//p' "${FOUND}/SKILL.md" | head -n 1 | tr -d '\r')"
dir_name="$(basename "$FOUND")"
if [ "$head_name" = "$dir_name" ]; then
  echo "✅ frontmatter name ($head_name) 与目录名一致"
else
  echo "✗ frontmatter name ($head_name) != 目录名 ($dir_name)"; fail=1
fi

# 3. description 存在
if grep -q '^description:' "${FOUND}/SKILL.md"; then
  echo "✅ description 存在"
else
  echo "✗ description 缺失"; fail=1
fi

# 4. 报告机检器必须随包可用（v2.3 外部评审建议 4）
#    它承载"未经实测不得定高危"这条约束；装完发现文件缺失，模板里的机检
#    步骤就会在用户机器上空转——那正是本项目抓过的那类"名实不符"。
if [ ! -f "${FOUND}/scripts/check-report.mjs" ]; then
  echo "✗ 报告机检器缺失: ${FOUND}/scripts/check-report.mjs（安装不完整）"; fail=1
elif ! command -v node >/dev/null 2>&1; then
  echo "·  未检测到 node，跳过报告机检器的可运行性探测"
else
  # 无参数时它应当返回"用法错误(2)"。跑到 2 就说明文件能被解析、主逻辑能执行；
  # 跑到 1 以外的其他码（例如模块级异常常见的 1）说明装到了坏副本。
  node "${FOUND}/scripts/check-report.mjs" >/dev/null 2>&1
  cr_code=$?
  if [ "$cr_code" -eq 2 ]; then
    echo "✅ 报告机检器可用（无参数按预期返回用法错误 2）"
  else
    echo "✗ 报告机检器异常退出码 $cr_code（预期 2=用法错误）"; fail=1
  fi
fi

# 5. 规范校验（若本机有校验器）
# 注意：v2.0 起校验器位于仓库级 scripts/，不随 skill 安装。
# 依次尝试：同目录安装副本 -> 环境变量 -> 仓库布局，都找不到就明确说明，不要静默跳过。
VALIDATOR=""
for cand in \
  "${FOUND}/scripts/validate-skill.mjs" \
  "${ADVERSARIAL_REVIEW_VALIDATOR:-}" \
  "$(dirname "$0")/../../../scripts/validate-skill.mjs"
do
  if [ -n "$cand" ] && [ -f "$cand" ]; then VALIDATOR="$cand"; break; fi
done

if command -v node >/dev/null 2>&1; then
  if [ -n "$VALIDATOR" ]; then
    echo ""
    echo "--- 规范校验 ($VALIDATOR) ---"
    node "$VALIDATOR" "$FOUND" || fail=1
    SPEC_CHECKED=1
  else
    echo ""
    echo "·  未找到 validate-skill.mjs（它位于仓库 scripts/，不随 skill 安装），跳过规范校验"
    echo "   如需完整校验，请从仓库运行： node scripts/validate-skill.mjs <skill目录>"
    SPEC_CHECKED=0
  fi
else
  echo ""
  echo "·  未检测到 node，跳过规范校验"
  SPEC_CHECKED=0
fi

echo ""
if [ "$fail" -ne 0 ]; then
  echo "⚠️  验证发现问题，请参考上面的提示。"
  exit "$fail"
fi

# 关键：跳过了规范校验就不能宣称"验证通过"——否则用户看到绿色结论，
# 而实际上 frontmatter 的长度/格式约束根本没被检查过。
# 这与本项目修复过的"永远绿的 CI 检查"是同一类静默通过缺陷。
if [ "$SPEC_CHECKED" -eq 1 ]; then
  echo "🎉 验证通过（含规范校验）。重启 agent 后即可使用。"
else
  echo "⚠️  基础检查通过，但**规范校验未执行** —— 不能视为完整验证。"
  echo "    已确认的只有：SKILL.md 存在、frontmatter name 与目录名一致、description 存在。"
  echo "    未被检查的包括：name/description 的长度与格式约束、正文非空。"
  exit 2
fi
