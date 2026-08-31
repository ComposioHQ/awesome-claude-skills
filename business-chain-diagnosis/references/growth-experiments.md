# 增长实验模板 Growth Experiment Template

用于「获客」与「复购与传播」环节：把模糊的「做点推广」变成可验证的实验。
Turns vague "do some marketing" into testable experiments for Acquisition and Retention & Referral.

## 实验卡 Experiment Card（每个实验一张 one per experiment）
1. 假设 Hypothesis：我们相信【目标用户】会因【机制】而【行为/指标变化】，因为【已有证据】。
   We believe [target users] will [metric change] because of [mechanism], based on [existing evidence].
2. 指标 Metric：主指标 1 个 + 护栏指标（防止损害其他环节）+ 观测周期。
   One primary metric + guardrail metrics (protect other stages) + observation window.
3. 变量 Variable：只改一个变量，其余冻结。 Change exactly one variable; freeze the rest.
4. 样本与时长 Sample & Duration：最小样本（如每组 100 付费用户）与完整使用周期。
   Minimum sample (e.g., 100 paying users per arm) and at least one full usage cycle.
5. 门槛 Thresholds：显著性（p<0.05 或相对提升 >=10%）、预算上限、提前终止条件。
   Significance (p<0.05 or relative lift >=10%), budget cap, early-stop condition.
6. 步骤 Steps：改动清单 → 上线 → 数据采集 → 分析。 Change list → ship → collect → analyze.
7. 决策规则 Decision rules：达标=全量/继续；未达标=回滚；边界情况=再测一轮。
   Hit threshold = roll out; miss = roll back; borderline = run one more round.

## 常用实验库 Experiment Library
### 获客 Acquisition
- 渠道对照：同文案两个渠道，比较 CAC 与转化率。 Same copy, two channels: compare CAC & conversion.
- 标题 A/B：痛点式 vs 收益式。 Pain-point headline vs benefit headline.
- 落地页变量：CTA 文案 / 按钮颜色 / 首屏长度。 CTA copy / button color / above-the-fold length.

### 激活 Activation
- 上手路径：3 步引导 vs 1 步直达核心。 3-step onboarding vs straight-to-core-value.
- 起始模板：给模板 vs 空白开始。 Provide a template vs start blank.

### 付费转化 Paid Conversion
- 定价锚点：3 档 vs 2 档。 3 tiers vs 2 tiers.
- 免费额度：数量制 vs 时间制。 Quantity-based free tier vs time-based.

### 复购与传播 Retention & Referral
- 续费提醒：提前 7 天 + 权益提示 vs 提前 3 天。 Renewal nudge: 7 days + value recap vs 3 days.
- 推荐奖励：双向奖励 vs 单向。 Double-sided referral reward vs single-sided.
- 习惯循环：周报邮件 vs 应用内进度条。 Weekly report email vs in-app progress bar.

## 证据与打分 Evidence & Scoring
- 实验前的假设必须有证据支撑（社区信号 / 访谈 / 竞品分析）；纯拍脑袋的「实验」不得作为强证据。
  Hypotheses need existing evidence (community signals / interviews / competitor analysis); guesses are never strong evidence.
- 实验结果的证据档：A/B 达标且可重复 → strong；单次观察 → weak；未测 → none。
  Result evidence tiers: replicated A/B hit = strong; single observation = weak; untested = none.
- 每个实验结论回填修复进度表，作为复检时分数变化的依据。
  Each experiment's outcome feeds the repair-progress table and justifies re-check score changes.

## 使用方式 How to Use
- 修复「获客 / 复购与传播」环节时，AI 按本模板输出实验卡（假设、指标、样本、门槛、决策规则）。
  When fixing Acquisition or Retention & Referral, the AI outputs an experiment card per this template.
- 用户执行后把结果给 AI，AI 更新证据档并复检。
  After the user runs it, the AI updates the evidence tier and re-checks.