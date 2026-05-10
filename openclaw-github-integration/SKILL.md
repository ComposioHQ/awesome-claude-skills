---
name: openclaw-github-integration
description: Integrate OpenClaw with GitHub for repository management, issues, PRs, and actions. 让 OpenClaw 能够自动化 GitHub 操作。
---

# OpenClaw GitHub 集成 Skill

让 OpenClaw 能够操作 GitHub 的各种功能，包括仓库管理、Issue、PR 和 Actions。

## 何时使用此 Skill

- 需要搜索 GitHub 仓库或代码
- 需要创建/管理 Issue 和 PR
- 需要查看 Actions 运行状态
- 需要获取用户或组织信息

## 此 Skill 做什么

### 能力 1: 仓库操作
- 搜索仓库
- 查看仓库信息（stars, forks, issues）
- Fork 仓库
- 创建/更新文件

### 能力 2: Issue 管理
- 创建 Issue
- 搜索 Issue
- 查看 Issue 详情
- 添加评论

### 能力 3: PR 操作
- 查看 PR 列表
- 创建 PR
- 审查 PR

### 能力 4: Actions
- 查看 workflow 运行状态
- 触发 workflow

### 能力 5: 用户和搜索
- 搜索代码
- 搜索用户和仓库

## 使用示例

**基础用法:**
```
帮我搜索 AI agent 相关的热门仓库
```

**进阶用法:**
```
在 tangyuan-dev/awesome-claude-skills 仓库创建一个 issue：添加 OpenClaw 支持
```

**示例:**
- 用户说："查看我的仓库列表"
- 输出：调用 GitHub API 获取用户仓库

**灵感来自:** OpenClaw 的 GitHub 集成日常工作流

## 常见用例

- 搜索开源项目
- 自动创建 Issue 报告 bug
- 监控仓库状态
- 管理 PR 审查流程