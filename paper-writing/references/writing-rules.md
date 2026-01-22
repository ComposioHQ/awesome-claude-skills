# 论文写作规范详解

本文档包含所有论文写作规则的详细说明和示例。

## 目录

1. [公式符号规范](#公式符号规范)
2. [写作风格规范](#写作风格规范)
3. [选词用词规范](#选词用词规范)
4. [句子表述规范](#句子表述规范)
5. [段落布局规范](#段落布局规范)
6. [表格图片规范](#表格图片规范)
7. [参考文献规范](#参考文献规范)

---

## 公式符号规范

### 1. 标量符号用小写拉丁字母表示

为避免混淆字母 `l` 和数字 `1`，字母 `l` 可用 `\ell` 替代。

示例图片：`pics/1.png`

### 2. 有结构的值使用 `\boldsymbol`（Attention）

有结构的值例如句子序列、树、图等。

示例图片：`pics/2.png`

### 3. `\boldsymbol` 的集合可用 `\mathcal`（Attention）

示例图片：`pics/3.png`

### 4. 向量值小写加粗，矩阵大写加粗

- 拉丁字母用 `\mathbf`
- 希腊字母用 `\boldsymbol`

示例图片：`pics/4.png`

### 5. 数域、期望等使用 `\mathbb`

示例图片：`pics/5.png`

### 6. 保持元素与集合的符号对应

示例图片：`pics/6.png`

### 7. 非单个字母的变量名

公式中的 `softmax`、`proj`、`enc` 等超过一个字母的变量或符号，使用正文字体，即使用 `\textrm` 或 `\textit` 命令。

示例图片：`pics/13.png`

### 8. 使用函数命令

许多函数和符号有现成的命令：`\arg{}`、`\max{}`、`\sin{}`、`\tanh{}`、`\inf`、`\det{}`、`\exp{}`

示例图片：`pics/14.png`

### 9. 公式中的括号使用 `\left`、`\right` 标记

```latex
\begin{gather}
   \bold{s} = \left(\sum_{i=0}^{N-1}{\alpha_{i} \bold{h}_i}\right) + \bold{h}_N\\
   \bold{s} = (\sum_{i=0}^{N-1}{\alpha_{i} \bold{h}_i}) + \bold{h}_N \\
\end{gather}

\begin{gather}
   \left\{ x \middle| x\ne\frac{1}{2}\right\} \\
   \{ x | x\ne\frac{1}{2}\}
\end{gather}
```

示例图片：`pics/15.jpeg`

### 10. 使用 `align` 表示一组公式，等号对齐

```latex
\begin{align}
   E &= m c^2 \\
   C &= B \log_2\left(1+\frac{S}{N}\right)
\end{align}
```

示例图片：`pics/16.jpeg`

### 11. 只对引用的公式加编号（Attention）

使用 `\nonumber` 去除不需要引用的公式编号。

```latex
\begin{equation}
   E = m c^2 \nonumber
\end{equation}
```

示例图片：`pics/17.jpeg`

---

## 写作风格规范

### 12. 写作风格要正式，避免缩写

- `don't` → `do not`
- 所有格 `'s` 尽量转化为 `of`

示例图片：`pics/7.png`

### 13. 拉丁文惯用语

- `e.g.,` 表示 `for example,`
- `i.e.,` 表示 `that is,`
- `et al.` 表示 `and others of the same kind,`
- `etc.` 表示 `and others,`（不用于列举人）
- `et al.` 或 `etc.` 在句末时，不用再添加额外的句号

示例图片：`pics/8.png`

### 14. 英文引号

使用 ``` `` ``` 和 `''` 分别表示左右引号，而不是其他符号或任何中文引号。

示例图片：`pics/9.png`

### 15. 不间断空格 `~`

使用 `~` 表示不间断空格，不间断空格不会导致意外的换行：

```latex
Figure~\ref{} shows the model performance.
Table~\ref{} shows dataset details.
We use BERT~\cite{bert} model.
Section~\ref{} concludes this paper.
```

示例图片：`pics/10.png`

### 16. URL 链接使用 `\url{}` 命令

```latex
\usepackage{hyperref}
\url{https://example.com}
```

示例图片：`pics/11.png`

### 17. 引号只表示"所谓"，不表示引用（Attention）

引用的表述考虑使用斜体 `\textit{}` 而不是引号。

示例图片：`pics/12.png`

---

## 选词用词规范

### 18. 注意连词符的词性

- 最后一个词是名词的，连起来是形容词词性
- 最后一个词是动词的，连起来是动词词性

示例图片：`pics/pic_29_1.jpeg`, `pics/pic_29_2.jpeg`

### 19. 词性易错点

- `First`、`Secondly` 均为副词
- `training`、`test`、`validation` 均为名词

示例图片：`pics/pic_30.jpeg`

### 20. 缩写符合使用习惯

- 符合习惯，与提出者尽量一致：CNN、LSTM、FEVER、ConceptNet、SQuAD、BiDAF
- 初次出现时，全称在前，缩写在后：`graph attention network (GAT)`、`pre-trained language model (PLM)`
- 或缩写在前，citation 在后：`BERT~\citep{BERT}`
- 领域名、任务名、指标等一般不需要大写：`natural language processing`、`question answering`、`accuracy`、`macro-F1 score`

示例图片：`pics/pic_31.jpeg`

### 21. 注意单复数

尤其是不规则单复数变化、不可数名词。

示例图片：`pics/pic_32.jpeg`

### 22. a/an 跟着元音音素走

- `an LSTM cell`
- `an F/H/L/M/N/S/X`
- `a U`

示例图片：`pics/pic_33.jpeg`

### 23. the 的使用

一般不会独立出现可数名词单数，要么加 `the` 特指，要么加复数泛指。

示例图片：`pics/pic_34.jpeg`

### 24. 时态：以一般现在时为主（Attention）

示例图片：`pics/pic_35.jpeg`

### 25. 避免绝对化表述

- 使用 `straightforward` 替换 `obvious`
- 使用 `generally`、`usually`、`often` 替换 `always`
- 使用 `rare` 替换 `never`
- 使用 `alleviate`、`relieve` 替换 `avoid`、`eliminate`

示例图片：`pics/36.jpg`

### 26. 避免模糊表述

避免使用 `meaning`、`semantic`、`better` 等词而不加解释。当表示一个事物更好时，不能仅仅说它更好，需要给出相应的解释与理由。

示例图片：`pics/37.jpg`

---

## 句子表述规范

### 27. 避免过多使用代词

避免过多使用 `it`、`they` 等，模型名缩写也不长，并且更清楚。

示例图片：`pics/38.jpg`

### 28. 避免过多贴标签

提出的方法到底改善了哪里，是什么导致的这个结果？

示例图片：`pics/39.jpg`

### 29. 一句话说一件事

尽量使用简单句，少使用长的复合句。

示例图片：`pics/40.jpg`

### 30. 不要混着说

观察/发现、假设、方法、效果要分开表述。

示例图片：`pics/41.jpg`

---

## 段落布局规范

### 31. 一行字数未超过 1/4 时，建议删除或增加字数（Attention）

可尝试在该段话最后添加 `\looseness=-1`，有时可以在不删除最后一行的情况下，将最后一行的个别单词"挤上去"。

示例图片：`pics/pic_42.png`

---

## 表格图片规范

### 32. 使用 Booktabs 绘制更好看的表格

使用 `\usepackage{booktabs}`，借助 `\toprule`、`\bottomrule`、`\midrule`、`\cmidrule` 命令画出好看的分隔线。

```latex
\begin{table}[htbp]
   \centering
   \begin{tabular}{lcccccl}\toprule
      & \multicolumn{3}{c}{E} & \multicolumn{3}{c}{F}
      \\\cmidrule(lr){2-4}\cmidrule(lr){5-7}
               & $mv$  & Rel.~err & Time    & $mv$  & Rel.~err & Time\\\midrule
      A    & 11034 & 1.3e-7 & 3.9 & 15846 & 2.7e-11 & 5.6 \\
      B & 21952 & 1.3e-7 & 6.2 & 31516 & 2.7e-11 & 8.8 \\
      \bottomrule
   \end{tabular}
   \caption{With booktabs.}
\end{table}
```

示例图片：`pics/18.jpeg`

### 33. 章节、表格、图片的引用

- 使用 `\label{...}` 定义后，通过 `\ref{...}` 自动引用跳转
- 子图引用：`Figure~\ref{fig:figure}(a)`

### 34. 不要把图表中的 Caption 在正文中复述

- Caption：写"这个表格是什么"
- 正文：写"这个表格说明了什么"

示例图片：`pics/20.jpeg`

### 35. "三线表"建议：尽量不要画竖线（Attention）

示例图片：`pics/22.jpg`

### 36. 表格大小调整

- 用 `\centering` 居中
- 用 `\small`、`\scriptsize`、`\footnotesize`、`\tiny` 调整字号
- 用 `\setlength{\tabcolsep}{8pt}` 调整列间距
- 用 `p{2cm}` 固定列宽
- 用 `\multirow`、`\multicolumn` 合并单元格

示例图片：`pics/23.jpg`

### 37. 矢量图

图像应使用矢量图（如 PDF 格式）：
- 使用 Adobe Illustrator、OmniGraffle 等软件绘制后存为矢量图
- 使用 Matplotlib：`plt.savefig('draw.pdf')`
- 在 LaTeX 中使用 pgfplots 直接绘制

示例图片：`pics/24.jpg`

### 38. 图片字体大小

- 介于正文字体与 caption 之间
- 图中字体大小保持一致

示例图片：`pics/25.jpg`, `pics/update1_pic_25.png`

### 39. 图表设计应适用于黑白打印

不要以颜色作为指代图示中线条的唯一特征，可使用实线/虚线、亮/暗、不同线形等。

示例图片：`pics/26.jpg`

### 40. 图片风格保持简洁美观

- 不要使用过多的颜色种类（不超过六种）
- 避免过亮的颜色
- 使用简洁的图示，尽量少用文字描述
- 同样功能模块使用统一格式
- 箭头走向应趋于同一个方向

示例图片：`pics/27.jpg`

---

## 参考文献规范

### 41. 引用需要排查是否在句子中做成分

- `\citep{}`：作为插入语（parent）
- `\citet{}`：作为句子主要成分（主语、宾语等）

示例图片：`pics/pic_43.png`

### 42. 尽量引用发表的版本而非 arXiv 版本

示例图片：`pics/pic_44.png`

### 43. 引用条目的格式尽量前后一致

如会议名缩写、是否包含会议时间地点等应保持一致。

示例图片：`pics/pic_45.png`
