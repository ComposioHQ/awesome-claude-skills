---
name: voice-notify
description: "macOS voice notification system for Claude Code agent teams. Provides TTS announcements for team events: agent check-in, task completion, error alerts. Features: 5 emotion presets (celebrate/comfort/encourage/alert/normal), 3 vibe levels (chill/normal/hype), filler word injection, time-aware greetings, speech queue, debounce. Zero dependencies — uses macOS built-in say + afplay. Use when: (1) user asks to enable voice notifications or voice alerts, (2) user says 'voice notify', 'voice reminder', '语音提醒', '语音播报', '语音通知', (3) user wants audio feedback for agent team workflows, (4) user asks agents to 'report in' or '报到' with voice, (5) user wants spoken alerts when tasks complete, (6) user wants vibe coding emotional feedback."
---

# Voice Notify

TTS 语音提醒 + 音效系统，专为 macOS 优化。在 Claude Code 任务完成、出错、Agent 报到时播报语音，保持开发心流。

---

## 系统要求（macOS 专属）

| 条件 | 说明 |
|------|------|
| macOS 12 Monterey 及以上 | 内置 `say` + `afplay` |
| 下载高质量语音 | 见下方「首次配置」|

> macOS `say` 命令与 Siri 语音引擎相互独立，无法直接调用 Siri 声音。
> **最接近 Siri 中文音色的替代方案：`Lili (Premium)`**（温和自然普通话女声）。

---

## 首次配置（自动安装 Hooks）

**重要：用户首次触发此 skill 时，必须执行以下两步自动配置，这样语音提醒才能在后续所有会话中自动生效：**

### 第一步：安装全局 Hooks（让语音自动触发）

```bash
bash ~/.claude/skills/voice-notify/scripts/install-hooks.sh
```

这会将 voice-notify 注册到 Claude Code 的全局 hooks 中，之后每次：
- **会话启动** → 自动播报「会话已启动，准备就绪」
- **任务完成** → 自动庆祝「任务完成」
- **工具出错** → 自动安抚「出现错误，请检查」
- **需要关注** → 自动提醒「需要您的关注」

### 第二步：检查语音环境

```bash
bash ~/.claude/skills/voice-notify/scripts/setup.sh
```

手动下载路径：**系统设置 → 辅助功能 → 朗读内容 → 管理语音** → 下载「莉莉 (Premium)」

### 安装完成后告知用户

安装成功后，告知用户：
- 语音提醒已全局生效，**重启 Claude Code 后自动启用**
- 随时用 `vn mute` 静音，`vn normal` 恢复
- 卸载：`bash ~/.claude/skills/voice-notify/scripts/install-hooks.sh --uninstall`

---

## Scripts

| 脚本 | 用途 |
|------|------|
| `scripts/voice.sh` | TTS 播报，支持预设/语气词/队列 |
| `scripts/sfx.sh` | 系统音效 |
| `scripts/vn.sh` | 模式快捷切换（quiet/normal/mute/hype） |
| `scripts/setup.sh` | 首次环境检测与引导（含 vn 别名安装） |
| `scripts/install-hooks.sh` | 自动安装/卸载全局 Hooks |
| `scripts/demo.sh` | 功能演示（`--fast` 快速模式） |

`SKILL_DIR` = `~/.claude/skills/voice-notify`

---

## voice.sh 完整参数

```
voice.sh "<消息>" [语音名] [语速] [flags...]
```

| Flag | 说明 | 示例 |
|------|------|------|
| `--preset=<name>` | 情感预设（见下表） | `--preset=celebrate` |
| `--vibe=<level>` | 情绪强度：`chill`\|`normal`\|`hype` | `--vibe=hype` |
| `--time-aware` | 根据时段自动加前缀（早啊/这么晚啊…） | `--time-aware` |
| `--queue` | 等上一条语音播完再说，防打断 | `--queue` |
| `--debounce=<秒>` | 同类事件X秒内只播一次，防轰炸 | `--debounce=5` |
| `--no-filler` | 禁用语气词注入 | `--no-filler` |

### 情感预设

| Preset | 语速 | 特征 | 典型使用场景 |
|--------|------|------|------------|
| `celebrate` | 200 | 正常语速，随机加「哇！太棒了！冲！」 | 任务完成、构建通过、成就 |
| `comfort` | 165 | 语速慢，随机加「嗯...没事的，会好的」 | 出错、失败、安抚 |
| `encourage` | 210 | 中快，随机加「加油！冲冲冲！继续！」 | 进度播报、中途鼓励 |
| `alert` | 210 | 清晰有力，随机加「注意，警告！」 | 严重错误、需要介入 |
| `normal` | 200 | 平和自然，偶尔加「好，」 | 通用通知、报到 |

### 语气词注入（借鉴 NoizAI characteristic-voice）

每条消息随机决定是否注入语气词（约 60% 概率）：
- 前缀和后缀各独立随机，来自各预设的词库
- 使用 `--no-filler` 关闭

### 时段感知（--time-aware）

| 时段 | 前缀 |
|------|------|
| 05:00–10:00 | 「早啊，」 |
| 18:00–22:00 | 「傍晚了，」 |
| 22:00–05:00 | 「这么晚啊，」 |

---

## Setup（用户偏好配置）

首次调用时询问偏好（如用户说「enable voice」直接用默认值）：

**1. Mode**

| Mode | 触发时机 |
|------|---------|
| `full` | 每个事件：报到、进度、完成、错误、鼓励 |
| `milestone`（默认）| 全员就绪、任务完成、错误、成就 |
| `completion` | 仅最终完成 |
| `off` | 静默 |

**2. Voice**

| 选项 | 语音 |
|------|------|
| 中文（默认）| `Lili (Premium)` |
| 粤语 | `Sinji` |
| 英文 | `Samantha` |

**3. Rate** — 默认由 preset 决定，可手动覆盖

**4. Vibe Level**

| Level | 说明 |
|-------|------|
| `chill` | 极简，无鼓励，无语气词 |
| `normal`（默认）| 适度鼓励，语气词启用 |
| `hype` | 全力输出，高频鼓励，多语气词 |

---

## Sound Effects

```bash
bash SKILL_DIR/scripts/sfx.sh <effect>
```

| Effect | Sound | 使用时机 |
|--------|-------|---------|
| `start` | Blow | 会话开始 |
| `success` | Glass | 构建/测试通过 |
| `error` | Sosumi | 构建失败、严重错误 |
| `celebrate` | Hero | 大任务完成 |
| `levelup` | Purr | 成就解锁 |
| `coin` | Pop | 小胜利、提交 |
| `notify` | Tink | 通用通知 |
| `warning` | Basso | 非严重警告 |
| `checkin` | Morse | Agent 报到 |

Always run sfx with `run_in_background: true`.

---

## Agent-Specific Voices（full mode）

| Agent 角色 | 语音 |
|-----------|------|
| PM | `Lili (Premium)` |
| Researcher | `Meijia (Enhanced)` |
| Designer | `Sinji` |
| DEV | `Yue (Premium)` |
| QA | `Meijia` |

`milestone`/`completion` 模式下统一使用用户选择的语音。

---

## Notification Patterns

> 所有 voice/sfx 命令使用 `run_in_background: true`

### Team Check-in（mode: full, milestone）

```bash
# 每个 Agent 到达（先音效，再语音）
bash SKILL_DIR/scripts/sfx.sh checkin
bash SKILL_DIR/scripts/voice.sh "老板，【角色名】已上线，向您报到！" "<agent_voice>" --preset=normal --queue

# 全员就绪
bash SKILL_DIR/scripts/sfx.sh celebrate
bash SKILL_DIR/scripts/voice.sh "全员报到完毕，团队就绪，等待老板指令！" "Lili (Premium)" --preset=celebrate --queue
```

### Task Completion（mode: full, milestone, completion）

仅 PM 输出最终汇总时触发：

```bash
bash SKILL_DIR/scripts/sfx.sh celebrate
bash SKILL_DIR/scripts/voice.sh "老板，任务执行完毕，【summary】已完成" "Lili (Premium)" --preset=celebrate --time-aware
```

### Error Alert（mode: full, milestone）

```bash
bash SKILL_DIR/scripts/sfx.sh error
bash SKILL_DIR/scripts/voice.sh "出现错误，请检查" "Lili (Premium)" --preset=alert --no-filler
```

### Build/Test Pass（mode: full, milestone）

```bash
bash SKILL_DIR/scripts/sfx.sh success
bash SKILL_DIR/scripts/voice.sh "构建通过，一切正常" "Lili (Premium)" --preset=celebrate
```

### Progress Narration（mode: full; vibe: normal, hype）

```bash
bash SKILL_DIR/scripts/sfx.sh coin
bash SKILL_DIR/scripts/voice.sh "已完成3项，共7项，再坚持一下" "Lili (Premium)" --preset=encourage --queue --debounce=10
```

### Encouragement（vibe: normal, hype）

每完成 3–5 个子任务随机触发一条：

```bash
bash SKILL_DIR/scripts/sfx.sh coin
bash SKILL_DIR/scripts/voice.sh "效率拉满，太强了" "Lili (Premium)" --preset=celebrate --debounce=30
```

可用语句（随机选一条，不连续重复）：
- 干得漂亮！继续保持
- 效率拉满，太强了
- 这波操作很丝滑
- 节奏很好，继续
- 又搞定一个，冲冲冲
- 代码如诗，优雅

### Achievement System（vibe: normal, hype）

```bash
bash SKILL_DIR/scripts/sfx.sh levelup
bash SKILL_DIR/scripts/voice.sh "成就解锁！五连胜，手感火热！" "Lili (Premium)" --preset=celebrate --no-filler
```

| 成就 | 触发 |
|------|------|
| First Blood | 首个任务完成 |
| Hat Trick | 3 个任务 |
| On A Roll | 5 个无错误 |
| Marathon | 会话超 2 小时 |
| Centurion | 今日提交 10+ |

---

## 模式快捷切换（vn 命令）

用户可在任意终端快速切换语音模式，无需中断 Claude Code 任务：

```bash
vn quiet    # 安静模式：只播完成+严重错误
vn normal   # 正常模式（默认）
vn mute     # 完全静音
vn hype     # 全开：每步都播，语气词拉满
vn status   # 查看当前模式
```

支持缩写：`vn q` / `vn n` / `vn m` / `vn h` / `vn s`

模式配置写入 `~/.voice_notify_config`，voice.sh 和 sfx.sh 每次执行时自动读取。

| 模式 | 语音过滤 | 音效过滤 | 语气词 |
|------|---------|---------|--------|
| `mute` | 全部静音 | 全部静音 | — |
| `quiet` | 仅 celebrate + alert | 仅 celebrate + error | 强制关闭 |
| `normal` | 不干预 | 不干预 | 按调用参数 |
| `hype` | 不干预 | 不干预 | 强制全开 |

首次使用需运行 `bash setup.sh` 安装 `vn` 别名。

---

## Rules

- **防打断**：多 Agent 场景下播报均加 `--queue`，确保顺序播出
- **防轰炸**：进度类消息加 `--debounce=N`，避免刷屏式播报
- **错误用 `--no-filler`**：严肃消息不需要语气词，保持清晰
- **时段感知**：首次报到或任务完成加 `--time-aware`，体现关怀
- 语音降级顺序：`Lili (Premium)` → `Yue (Premium)` → `Lili (Enhanced)` → `Tingting`
- milestone mode 中间步骤静默
- full mode 消息控制在 20 个中文字以内
