---
name: openclawnpm-tools
description: NPM package management tools for OpenClaw - publish, version, and manage npm packages. 让 OpenClaw 能够自动化 NPM 包管理。
---

# OpenClaw NPM 工具 Skill

让 OpenClaw 能够操作 npm 包管理和发布。

## 何时使用此 Skill

- 需要发布 npm 包
- 需要管理包版本
- 需要查看包信息
- 需要发布 beta/alpha 版本

## 此 Skill 做什么

### 能力 1: 包发布
- 发布到 npm 官方仓库
- 发布 beta/alpha 版本
- 发布 scoped packages

### 能力 2: 版本管理
- 语义化版本更新 (major/minor/patch)
- 查看版本历史
- 管理 npm 账号

### 能力 3: 包查询
- 搜索 npm 包
- 查看包信息
- 查看下载统计

## 使用示例

**基础用法:**
```
帮我发布这个包到 npm
```

**进阶用法:**
```
将包版本升级到 1.0.0 并发布
```

**示例:**
- 用户说："发布 1.0.0 版本"
- 输出：执行 npm publish

**灵感来自:** OpenClaw 插件发布工作流

## 常见用例

- 自动化 npm 包发布
- 版本号自动更新
- 发布测试版本给用户试用