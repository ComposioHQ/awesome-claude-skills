# React Best Practices

[English](README.md) | [한국어](README.ko.md) | **中文** | [日本語](README.ja.md)

---

一个结构化的仓库，用于创建和维护针对代理和 LLM 优化的 React 最佳实践。

## 结构

- `rules/` - 单独的规则文件（每条规则一个文件）
  - `_sections.md` - 章节元数据（标题、影响、描述）
  - `_template.md` - 创建新规则的模板
  - `area-description.md` - 单独的规则文件
- `src/` - 构建脚本和工具
- `metadata.json` - 文档元数据（版本、组织、摘要）
- __`AGENTS.md`__ - 编译输出（自动生成）
- __`test-cases.json`__ - LLM 评估的测试用例（自动生成）

## 入门

1. 安装依赖：
   ```bash
   pnpm install
   ```

2. 从规则构建 AGENTS.md：
   ```bash
   pnpm build
   ```

3. 验证规则文件：
   ```bash
   pnpm validate
   ```

4. 提取测试用例：
   ```bash
   pnpm extract-tests
   ```

## 创建新规则

1. 将 `rules/_template.md` 复制到 `rules/area-description.md`
2. 选择适当的区域前缀：
   - `async-` - 消除瀑布流（第 1 章节）
   - `bundle-` - 包体积优化（第 2 章节）
   - `server-` - 服务器端性能（第 3 章节）
   - `client-` - 客户端数据获取（第 4 章节）
   - `rerender-` - 重渲染优化（第 5 章节）
   - `rendering-` - 渲染性能（第 6 章节）
   - `js-` - JavaScript 性能（第 7 章节）
   - `advanced-` - 高级模式（第 8 章节）
3. 填写 frontmatter 和内容
4. 确保有带解释的清晰示例
5. 运行 `pnpm build` 重新生成 AGENTS.md 和 test-cases.json

## 规则文件结构

每个规则文件应遵循以下结构：

```markdown
---
title: 规则标题
impact: MEDIUM
impactDescription: 可选描述
tags: 标签1, 标签2, 标签3
---

## 规则标题

规则及其重要性的简要说明。

**错误示例（描述问题所在）：**

```typescript
// 错误代码示例
```

**正确示例（描述正确做法）：**

```typescript
// 正确代码示例
```

示例后的可选解释文本。

参考：[链接](https://example.com)

## 文件命名规范

- 以 `_` 开头的文件是特殊文件（从构建中排除）
- 规则文件：`area-description.md`（例如 `async-parallel.md`）
- 章节从文件名前缀自动推断
- 规则在每个章节内按标题字母顺序排序
- ID（如 1.1、1.2）在构建时自动生成

## 影响级别

- `CRITICAL` - 最高优先级，主要性能提升
- `HIGH` - 显著性能改进
- `MEDIUM-HIGH` - 中高程度的提升
- `MEDIUM` - 中等性能改进
- `LOW-MEDIUM` - 中低程度的提升
- `LOW` - 渐进式改进

## 脚本

- `pnpm build` - 将规则编译成 AGENTS.md
- `pnpm validate` - 验证所有规则文件
- `pnpm extract-tests` - 提取 LLM 评估的测试用例
- `pnpm dev` - 构建和验证

## 贡献

添加或修改规则时：

1. 为您的章节使用正确的文件名前缀
2. 遵循 `_template.md` 结构
3. 包含带解释的清晰错误/正确示例
4. 添加适当的标签
5. 运行 `pnpm build` 重新生成 AGENTS.md 和 test-cases.json
6. 规则自动按标题排序 - 无需管理编号！

## 致谢

最初由 [Vercel](https://vercel.com) 的 [@shuding](https://x.com/shuding) 创建。
