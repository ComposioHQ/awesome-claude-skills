---
name: vibe-coding-cn
description: Chinese-language skill for AI-assisted programming using Vibe Coding methodology with Glue Coding, Canvas-driven development, and 12-layer language elements.
license: MIT
---

# Vibe Coding CN Skill

通过与 AI 结对编程，将想法变为现实的终极工作站。本 Skill 提供完整的 Vibe Coding 方法论、工作流程和实战指南。

## When to Use This Skill

- 从零开始开发新项目，需要 AI 全程辅助
- 想要复用成熟开源库而非重复造轮子
- 需要理解复杂项目架构和依赖关系
- 想要配置多 Agent 协作的开发环境
- 提升代码阅读和理解能力

## What This Skill Does

1. **Vibe Coding 哲学**: "一二三万物"核心理念，AI 辅助开发的完整方法论
2. **胶水编程 (Glue Coding)**: 能抄不写，能连不造，复用成熟开源库
3. **Canvas 白板驱动**: 图形是第一公民，代码是白板的序列化形式
4. **AI 蜂群协作**: tmux 多 Agent 系统，并行处理复杂任务
5. **12 层语言要素**: 从语法到设计意图的代码理解框架
6. **标准工作流**: 6 步从零到上线 (GDD → 技术栈 → 计划 → 记忆库 → 开发 → 功能)

## How to Use

### Basic Usage

```
用 Vibe Coding 的方式帮我做一个项目：[一句话描述你的项目想法]
```

### Advanced Usage

```
我想用胶水编程实现：[功能描述]
请帮我：
1. 搜索每个环节的成熟开源库
2. 阅读官方文档总结接口用法
3. 生成胶水代码连接这些组件
```

## Example

**User**: "我想做一个 Telegram 机器人，分析加密货币行情后推送给用户"

**Output**:
```
好的，我将用 Vibe Coding 方式协助你开发这个项目。

第 1 步：生成游戏设计文档 (GDD)
第 2 步：推荐技术栈（Python + python-telegram-bot + ccxt）
第 3 步：创建实施计划
第 4 步：建立记忆库 (memory-bank/)
第 5 步：增量式开发，每步验证后继续
第 6 步：添加新功能

每完成一步，我会等待你的验证反馈后再继续下一步。
```

**Inspired by:** [tukuaiai/vibe-coding-cn](https://github.com/tukuaiai/vibe-coding-cn)

## Tips

- 每完成一步都要验证测试，通过后再继续下一步
- 优先复用成熟开源库，避免重复造轮子
- 使用 Canvas 白板可视化项目架构
- 复杂任务可使用 tmux 多 Agent 协作
- 保持 memory-bank/ 文档同步更新

## Common Use Cases

- 快速原型开发：从想法到可运行代码
- 开源库集成：连接多个成熟库实现功能
- 遗留项目理解：Canvas 白板分析架构
- 大规模重构：多 Agent 并行处理
- 代码能力提升：12 层语言要素学习

## Constraints

本 Skill 包含 57 条核心约束：
- 34 条通用开发约束（架构原则、代码质量、错误处理、状态并发、开发流程）
- 23 条胶水开发约束（复用优先、依赖完整性、运行期验证、职责边界）

完整约束列表详见：[GitHub Repository](https://github.com/earyantLe/vibe-coding-skill)
