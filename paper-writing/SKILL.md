---
name: paper-writing
description: "学术论文写作检查与优化助手。基于 MLNLP-World 社区整理的论文写作技巧，帮助检查和优化学术论文。Use when: (1) 检查论文 LaTeX 格式和排版, (2) 优化公式符号使用, (3) 改进图表设计, (4) 润色英文学术表达, (5) 检查参考文献格式, (6) 投稿前终稿检查, (7) 用户询问论文写作技巧或规范。"
---

# Paper Writing Tips - 学术论文写作助手

帮助用户检查和优化学术论文，确保符合顶会投稿规范。

## 核心检查规则

### 公式符号规范

| 类型 | 规范 | LaTeX 命令 |
|------|------|-----------|
| 标量 | 小写拉丁字母，`l` 用 `\ell` 替代 | `$x$`, `$\ell$` |
| 向量 | 小写加粗 | `\mathbf{x}` (拉丁), `\boldsymbol{\alpha}` (希腊) |
| 矩阵 | 大写加粗 | `\mathbf{X}` |
| 集合 | 花体 | `\mathcal{X}` |
| 数域/期望 | 黑板粗体 | `\mathbb{R}`, `\mathbb{E}` |
| 多字母变量 | 正文字体 | `\textrm{softmax}`, `\textrm{enc}` |
| 函数 | 内置命令 | `\arg`, `\max`, `\sin`, `\exp` |

**公式格式要求：**
- 括号使用 `\left(` `\right)` 自动调整大小
- 多行公式用 `align` 环境，`&=` 对齐等号
- 只对引用的公式加编号，其他用 `\nonumber`

### 写作风格规范

**必须避免：**
- 缩写形式：`don't` → `do not`, `can't` → `cannot`
- 所有格 `'s`：尽量转化为 `of` 结构

**拉丁文惯用语：**
- `e.g.,` = for example（注意逗号）
- `i.e.,` = that is（注意逗号）
- `et al.` = and others（句末不加额外句号）

**LaTeX 格式：**
- 英文引号：``` `` ``` 和 `''`（不用中文引号）
- 不间断空格：`Figure~\ref{}`, `Table~\ref{}`, `BERT~\cite{}`
- URL：`\url{}`（需 `\usepackage{hyperref}`）

### 选词用词规范

**避免绝对化表述：**
| 避免 | 使用 |
|------|------|
| obvious | straightforward |
| always | generally, usually, often |
| never | rare |
| avoid, eliminate | alleviate, relieve |

**冠词使用：**
- `a/an` 跟元音音素：`an LSTM`, `an F1 score`, `a U-Net`
- 可数名词单数需加 `the` 特指或用复数泛指

**缩写规范：**
- 首次出现：`graph attention network (GAT)` 或 `BERT~\citep{BERT}`
- 保持一致：`BERT` 不要写成 `Bert` 或 `bert`

### 表格图片规范

**表格：**
- 使用 `booktabs` 宏包：`\toprule`, `\midrule`, `\bottomrule`
- 三线表，避免竖线
- 调整：`\centering`, `\small`, `\setlength{\tabcolsep}{8pt}`

**图片：**
- 使用矢量图（PDF 格式）
- 字体大小介于正文和 caption 之间
- 颜色不超过六种，适用于黑白打印
- 箭头方向保持一致

### 参考文献规范

**引用命令：**
| 模板 | 插入语 | 句子成分 |
|------|--------|----------|
| ACL/NAACL/EMNLP | `\citep{}` | `\citet{}` |
| COLING | `\citep{}` | `\newcite{}` |
| AAAI/IJCAI | `\cite{}` | `\citeauthor{} \shortcite{}` |

**其他要求：**
- 优先引用正式发表版本，非 arXiv
- 格式保持一致（会议名缩写等）

## 终稿检查清单

检查论文时，按以下清单逐项核对：

1. **匿名性**：无个人/机构信息
2. **页数**：不超页
3. **拼写语法**：使用 Grammarly/Writefull 检查
4. **缩写**：首次使用时已定义
5. **大小写**：模型名一致（BERT 不是 Bert）
6. **图片**：矢量图，字体统一，颜色≤6种
7. **表格**：booktabs 样式，无竖线
8. **公式**：引用的有编号，格式正确
9. **引用**：`\citep`/`\citet` 正确使用
10. **代码/数据**：无个人信息，无隐藏文件夹（.git）

## Resources

### references/

详细规则和示例请参阅：

- **[writing-rules.md](references/writing-rules.md)**：完整的写作规范，包含所有规则的详细说明和示例图片
- **[final-checklist.md](references/final-checklist.md)**：投稿前完整检查清单
- **[resources.md](references/resources.md)**：推荐的论文写作学习资源
