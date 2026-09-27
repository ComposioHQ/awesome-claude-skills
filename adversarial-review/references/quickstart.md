# 三方对抗式评审 · 快速上手

## 30 秒上手

安装 skill 后，在你的项目里直接说：

```
蓝军评审一下这个模块
```

或英文：

```
adversarial review the auth module
```

不需要记任何命令。skill 会自动接管流程。

---

## 三种档位怎么选

| 场景 | 用哪档 | 说这句话 |
|---|---|---|
| 改了个小 bug，想快速看一眼 | 轻档（~1x） | "轻量审一下这次改动" |
| 做完一个功能，准备合并 | **标准档**（默认，~3x） | "蓝军评审" |
| 要发版了 / 大重构 / 动了上游兼容 | 重档（~5-8x） | "重档评审，这版要发布" |

**不确定就用默认标准档。** "~Nx" 指相对一轮蓝军审查的 token 开销。报告有分级展开与按编号引用纪律（见 SKILL.md「Token 纪律」），不会逐条灌水。

---

## 你会拿到什么

跑完后 `docs/review/` 下会有四份文档。**别只看结论，去看证据链**：

```bash
cat docs/review/BLUE-TEAM-REVIEW-*.md       # 蓝军：缺陷 + 证据链
cat docs/review/RESPONSE-*.md               # 开发团队（主代理）的逐条回应
cat docs/review/THIRD-PARTY-REVIEW-*.md     # 第三方：修没修对 + 新缺陷
cat docs/review/ADJUDICATION-*.md           # 中立裁定：最终该修什么
```

**优先看 `ADJUDICATION` 的「合并执行清单」**——那是可以直接照着改的清单。

---

## 什么时候不该用它

- ❌ **改了一行文案** → 用不着三方流程，浪费额度
- ❌ **想让 AI 说"代码很好"** → 这个 skill 的立场就是敌意的，不会给你这个
- ❌ **没有测试的项目，且不打算补** → 第三方"测试假安全感"的检查会空转
- ❌ **依赖外部系统行为的关键结论** → 三方互搏抓不出共同盲区，**必须实测**

---

## 一个常见误解

> "过了三方评审 = 代码没问题了"

**不是。** 三个角色的子代理通常是**同一个模型**。它抓的是**逻辑性缺陷**（自相矛盾、遗漏分支、声明与实现不符、测试造假），抓不出**双方共有的知识盲区**。

所以：**凡是对上游/外部系统行为的假设，一律实测，不要让两个 agent 互相点头。**

---

## 想自己改模板？

**改之前先读两个地方**：

1. **[`prompt-templates.md`](prompt-templates.md)** —— 三个角色的完整提示词模板都在这里。
2. **[`prompt-templates.md`](prompt-templates.md) 末尾的「设计要点」表** —— 列出改模板时**不能丢**的 13 条约束（尤其是"逐维度表态""第三方稽核蓝军覆盖度""裁定方审查共同前提""分级展开+按编号引用""定级与实测绑定"这五条）。

**要扩展审查范围**（比如想加上"性能"之外的质量属性），改 [`review-dimensions.md`](review-dimensions.md)，不要去改模板——**维度是数据，模板是机制**。

改完用校验器过一遍（校验器在**仓库**的 `scripts/` 下，不随 skill 安装）：

```bash
# 从仓库根目录运行
node scripts/validate-skill.mjs skills/adversarial-review
node scripts/test-validate-skill.mjs    # 校验器自身的回归测试
node scripts/test-check-report.mjs      # 报告机检器的回归测试
node scripts/check-links.mjs            # 检查文档里的本地链接
node scripts/check-docs.mjs             # 文档中的行数/条数主张与实况一致
node scripts/test-mutations.mjs         # 突变测试：证明这些检查真能失败
```

跑完评审后，用**随 skill 安装**的报告机检器把蓝军和第三方两份总表各扫一遍（未实测却定高危、缺「定级依据」列、位置列为空、**声称实测却在自己的展开段落里拿不出命令**，都会失败）：

```bash
S=~/.claude/skills/adversarial-review/scripts/check-report.mjs
node $S docs/review/BLUE-TEAM-REVIEW-<version>.md
node $S docs/review/THIRD-PARTY-REVIEW-<version>.md
```

完整产出样例见 [`../examples/sample-review-v2.2.md`](../examples/sample-review-v2.2.md)（能通过机检器）；[`../examples/sample-review.md`](../examples/sample-review.md) 是 v2.2 之前的历史样例，保留是为了演示行号腐烂，机检器对它判红是预期行为。
