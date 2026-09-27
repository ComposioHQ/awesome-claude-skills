# 示例：一份 v2.2+ 合规的蓝军报告（能通过机检器）

> 本文件是**格式演示**，被审代码是虚构的 `auth/` 模块——不是某次真实评审的记录。
> 它存在的理由：随包发布的历史样例 [`sample-review.md`](sample-review.md) 产于 v2.2 之前，
> 按 v2.2「未实测不得定高危」的标准会被自家机检器判红。用户第一次跑机检器就看到红，
> 第一印象会是"这工具坏了"，所以这里给一份**明确按现行格式写**的对照物。
>
> 想验证它真的合规，跑：
> `node scripts/check-report.mjs examples/sample-review-v2.2.md` → 应当 `exit=0`。

---

## 被审对象

```
仓库：      demo-shop（虚构）
基线：      main @ e19a2c3
改动范围：  auth/session.ts 新增令牌刷新，auth/middleware.ts 改了过期判断
项目背景：  内部 SaaS，令牌有效期 15 分钟，刷新失败会踢到登录页
声称已完成：令牌过期前自动刷新；刷新失败保留旧会话
```

选定维度：正确性 · 错误处理 · 并发与竞态 · 兼容性 · 测试有效性

---

## 缺陷总表

| 编号 | 级别 | 定级依据 | 一句话 | 维度 | 位置（文件:行号） |
|---|---|---|---|---|---|
| B1 | 🔴 | 实测 | 刷新窗口算错，令牌刚发出就被判过期，用户每次刷新都掉登录 | 正确性 | auth/session.ts:47 |
| B2 | 🟠 | 实测 | 刷新失败的 catch 里把错误吞了，中间件仍按"已刷新"继续放行 | 错误处理 | auth/middleware.ts:88 |
| B3 | 🟡 | 推理·待实测 | `expiresAt` 用字符串存，跨时区比较不可靠 | 兼容性 | auth/session.ts:19 |
| B4 | 🟡 | 实测 | 新增的两个分支没有测试覆盖，现有测试走不到失败路径 | 测试有效性 | tests/session.test.ts:1-60 |

### B1 · 🔴 刷新窗口算错

- **证据链**：`auth/session.ts:47` 用 `Date.now() + 15 * 1000` 而不是 `15 * 60 * 1000` 计算过期时间，于是 45 行的 `needsRefresh()` 在任何一次调用里都直接返回 `true`。
- **复现命令**（实测输出）：

```bash
sed -n '45,48p' auth/session.ts
```

```text
45:  function needsRefresh(t: Token) { return Date.now() > t.expiresAt - 30_000; }
47:  const expiresAt = Date.now() + 15 * 1000;   // ← 想要 15 分钟
```

```bash
npx tsx -e "const e=Date.now()+15*1000; console.log('issued, needsRefresh =', Date.now() > e - 30_000)"
```

```text
issued, needsRefresh = true
```

- **触发条件**：任何一次签发令牌的请求，无需等待。
- **用户可见后果**：登录后第一次操作就被送回登录页，且循环出现——看起来像"登录不进去"。
- **修复方向**：`const expiresAt = Date.now() + 15 * 60 * 1000;`，并把 15/60/1000 抽成 `TOKEN_TTL_MS` 常量；补一条断言 `expiresAt - issuedAt === TOKEN_TTL_MS` 的测试。

### B2 · 🟠 吞掉刷新失败

- **证据链**：`auth/middleware.ts:88` 的 `catch {}` 块为空，`refreshed` 变量在 catch 之前就已置 `true`，因此刷新抛错时后续 `if (refreshed) return next()` 依旧放行，请求带着过期令牌进入业务层。
- **复现命令**（实测输出）：

```bash
sed -n '84,92p' auth/middleware.ts && npx vitest run tests/session.test.ts -t "refresh failure"
```

```text
84:    let refreshed = true;
88:    } catch { /* 保留旧会话 */ }
90:    if (refreshed) return next();
No test matches "refresh failure"（该路径没有测试）
```

- **触发条件**：刷新接口超时或返回 5xx（真实高频场景，弱网下尤其明显）。
- **用户可见后果**：业务层收到过期令牌，报"无权访问"而不是"请重新登录"，用户以为权限被收回。
- **修复方向**：把 `refreshed = true` 移到 try 成功分支；catch 内显式 `return res.status(401).json({ error: 'reauth_required' })`。

### B3、B4（🟡 只占总表一行）

- **B3** 修复方向：`expiresAt` 改存 epoch ms（number），比较前不做字符串隐式转换。
- **B4** 修复方向：为刷新失败与过期判定各补一条测试，断言 401 与重定向。

---

## 维度覆盖声明

| 维度 | 结论 |
|---|---|
| 正确性 | 已查 —— 发现 B1 |
| 错误处理 | 已查 —— 发现 B2 |
| 并发与竞态 | 已查，未发现问题（刷新用互斥锁，`session.ts:60-72` 已读） |
| 兼容性 | 已查 —— 发现 B3 |
| 测试有效性 | 已查 —— 发现 B4 |

## 未验证项

- B3 为**推理**定级：没有跑出可复现的跨时区错值，需要一条构造 `expiresAt` 为 ISO 字符串的测试才能升级为 🟠。
- 刷新接口的真实超时率未测量（需要生产日志），B2 的"高频"是推断。
