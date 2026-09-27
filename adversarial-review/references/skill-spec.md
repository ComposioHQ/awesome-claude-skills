# Agent Skills 规范速查（SKILL.md）

> 来源：Agent Skills 规范。写/改 skill 时对照本表。

## 目录结构

```
skill-name/
├── SKILL.md          # 必需：frontmatter + 指令正文
├── scripts/          # 可选：可执行代码
├── references/       # 可选：参考文档（按需加载）
└── assets/           # 可选：模板、资源
```

**`references/` 的意义**：agent 决定激活 skill 后会**载入整个 SKILL.md**。正文太长会挤占上下文，所以长内容应拆到 `references/` 里按需读取。

---

## 渐进式披露（Progressive Disclosure）—— 最容易被忽略的规范

这是官方规范里**最容易漏掉、后果最直接**的一组约束。它们不在 frontmatter 校验范围内，所以**自动化工具查不出来，只能靠人遵守**。

| 约束 | 要求 | 违反后果 |
|---|---|---|
| **正文行数** | `SKILL.md` 正文应 **< 500 行** | 超长正文挤占上下文，agent 处理真实任务的能力下降 |
| **引用深度** | 文件引用只能 **一层深**（从 SKILL.md 直接指向 `references/xxx.md`） | 深层嵌套会导致 agent **只读取到部分内容** |
| **内容分层** | 核心指令放 SKILL.md，详细资料放 `references/` | 把参考手册塞进正文，等于每次激活都强制加载它 |

**为什么这三条重要**：frontmatter 有校验器能查，正文没有。**规范在这里靠自觉**——所以它最容易在"赶时间"时被牺牲。

**做法**：正文只保留"做什么、按什么顺序做、什么情况例外"；把模板、长表格、规范速查、示例等"按需才看"的内容外置。本仓库自己的 `SKILL.md` 就是按此组织（正文 173 行，三个提示词模板与「设计要点」表外置到 `references/prompt-templates.md`）。

**自检**：

```bash
# 正文是否超 500 行
wc -l skills/*/SKILL.md

# 是否存在深层引用（形如 references/a/b.md 的引用通常意味着嵌套）
grep -rn "references/.*/" skills/*/SKILL.md
```

---

## frontmatter 字段

| 字段 | 必需 | 约束 |
|---|---|---|
| `name` | ✅ | ≤ 64 字符；仅小写字母、数字、连字符；不得以连字符开头/结尾；**不得有连续连字符**；**必须与父目录名一致** |
| `description` | ✅ | 1-1024 字符，非空；应同时说明「做什么」和「何时用」 |
| `license` | ❌ | 协议名或指向随附协议文件 |
| `compatibility` | ❌ | 1-500 字符；仅在有特定环境要求时使用 |
| `metadata` | ❌ | 字符串键值映射（如 author / version） |
| `allowed-tools` | ❌ | 空格分隔的预授权工具列表（实验性，宿主支持度不一） |

> **依据说明**：「`name` 必须与父目录名一致」以及上表各字段的长度上限，均来自 **Agent Skills 官方规范**（`agentskills` 规范文档的 frontmatter 表格），不是本仓库的约定。本仓库的 `scripts/validate-skill.mjs` 按此实现校验。

### 合法 / 非法 name 对照

```yaml
name: pdf-processing      # ✅
name: data-analysis       # ✅
name: code-review         # ✅

name: PDF-Processing      # ❌ 不允许大写
name: -pdf                # ❌ 不能以连字符开头
name: pdf--processing     # ❌ 不允许连续连字符
name: my_skill            # ❌ 不允许下划线
```

---

## description 写法

**好的写法**（包含具体关键词 + 触发条件）：

```yaml
description: Extracts text and tables from PDF files, fills PDF forms, and merges
  multiple PDFs. Use when working with PDF documents or when the user mentions
  PDFs, forms, or document extraction.
```

**差的写法**：

```yaml
description: Helps with PDFs.
```

**要点**：
1. 把用户**可能说出的原话**写进去（中英文都要，如果你的用户群是双语）。
2. 明确写「**Use when...**」或「**当用户说...时使用**」——这是 agent 判断激活的依据。
3. 关键词决定检索命中率，别嫌啰嗦。

---

## 正文建议章节

规范对正文格式无限制，但推荐包含：

- 分步指令（Step-by-step instructions）
- 输入/输出示例
- 常见边界情况（Common edge cases）

**本仓库额外建议**（来自实战）：

- **能力边界**：主动声明这个 skill **做不到什么**。这不减分，反而防止误用。
- **常见错误用法**：把踩过的坑写下来，比写十条"最佳实践"有用。

---

## 校验

本仓库自带校验器，无需安装依赖：

```bash
node scripts/validate-skill.mjs /path/to/your-skill
```

会检查：frontmatter 是否存在、`name` 格式与目录名一致性、`description` 长度与触发词、`compatibility` 长度、未知字段、正文是否存在。

---

## 参考

- Agent Skills 规范：<https://github.com/agentskills/agentskills>
- Anthropic Skills 仓库：<https://github.com/anthropics/skills>
