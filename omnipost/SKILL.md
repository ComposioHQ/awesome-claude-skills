---
name: omnipost
description: 把已经写好的内容（图文 / 视频 / 博客文章）一键分发到多个平台（CSDN、掘金、知乎、微信公众号、微博、B站、小红书、视频号、抖音、快手、百家号、搜狐号、头条号、开源中国、思否、Dev.to、Mastodon、Bluesky、WordPress 等 40 余个），通过本机安装的 OmniPost 桌面应用完成。当用户想「发布 / 分发 / 同步 / 一键多平台发」文章、图文或视频时使用本 skill。
---

# OmniPost — 多平台内容分发（agent 的「手」）

OmniPost 是装在**用户本机**的桌面应用（Windows / macOS），把**你（agent）已经准备好的内容**分发到多个平台。它在 `127.0.0.1` 起一个本地服务，可用 **MCP / CLI / HTTP** 三种方式调用。**内容生成在你这边，OmniPost 只负责分发**：它不含任何模型、不判断内容、不自动互动。账号登录态只存在用户电脑上，发出去的请求来自用户自己的浏览器会话，不经过任何云端。

## 第 0 步：先找到本机的 OmniPost（重要）

1. 读 `~/.omnipost/server.json`，取 `port`（通常是 `8787`；每次启动可能变）。
2. `GET http://127.0.0.1:<port>/api/health`，返回里：
   - `cli.shell` = 这台机器上可直接执行的 CLI 命令（Windows 通常是 `<安装目录>\omnipost.cmd`，macOS 是 `/Applications/OmniPost.app/Contents/Resources/bin/omnipost-cli`）；
   - `mcp.sse` / `mcp.stdio` = MCP 接入方式。
3. **本文档里所有 `omnipost <子命令>`，一律替换成 `cli.shell` 的值。**
4. 请求失败 → OmniPost 没在运行，请用户启动它；`/api/health` 返回 404 → 版本太旧，请用户更新。

调用方式按顺序选：

1. **CLI（默认）**：不依赖你的工具列表里有什么，装了 OmniPost 就能用。
2. **MCP（如果已挂载）**：若当前工具列表里已有 `omnipost` 这个 server 的工具（如 `list_platforms` / `publish_post`），直接用它们更省事。**不要假设 MCP 已配置，也不要自行去配置**——没有就用 CLI。
3. **HTTP（需要更细控制时）**：`http://127.0.0.1:<port>/api/...`，参数与 MCP 工具同构。

> 想要为这台机器定制、路径都算好的版本：`GET http://127.0.0.1:<port>/api/skill?download=1` 会下载一份本机专属 Skill（zip，含同样的 rules/ 目录）。

### CLI 高频命令速查（实测语法，别猜参数名）

```
# 看状态 / 平台 / 账号 / 告警（分发前先看一眼 alerts）
omnipost status
omnipost platforms
omnipost accounts
omnipost alerts

# 建草稿（默认、最稳）：正文用 --doc，目标用 --targets 或 --platforms 或 --group
omnipost publish --doc ./article.md --targets weixin:default,zhihu:default --mode draft --title "标题" --summary "摘要" --cover ./cover.jpg

# 正式发布（只在用户明确要求时）
omnipost publish --doc ./article.md --platforms csdn,cnblogs --mode publish --tags AI,Agent --summary "摘要"

# 结构化参数整包（{targets,mode,doc:{title,markdown,summary,cover,extras,…}}，与 MCP/HTTP 同构）
omnipost publish --json ./publish.json

# 定时：到点由运行中的桌面应用执行；--spacing 错峰；--deliver auto 时支持的平台交给平台自带定时（关机也发）
omnipost schedule --doc ./article.md --at "2026-10-20 09:00" --platforms xiaohongshu,douyin --mode publish --spacing 10

# 查结果：用本次返回的 recordId 对账，别拿「列表里有同名草稿」当证据
omnipost posts --limit 20
omnipost publish-status zhihu --recordId <id>

# 图库（可选）：provider 是位置参数（pixabay|pexels|unsplash）
omnipost images search pixabay "team workflow" --perPage 6
omnipost images use pexels --item-file ./item.json --mode cover
```

- 任何子命令都支持 `--help`（如 `omnipost publish --help`）；**参数写错会报「未知参数」并提示正确写法——照提示改，不要换姿势瞎试**。
- ⚠️ Windows 上 **URL 含 `&` 不要直接放命令行参数**（PowerShell 调 `.cmd` 会在 `&` 处静默截断，exit code 仍是 0）：封面/图片一律走 `--json` / `--item-file` 文件传参，或先下载为本地文件再传路径。安装目录另有 `omnipost.ps1` 可直调（不经 cmd.exe）。
- **发布后核验必须拿本次返回的 `recordId` 对账**（在 `posts` 结果里找到这条 recordId 再确认 stage/postUrl）。

## 能力清单（MCP 工具 ↔ CLI 命令）
- `list_platforms` ↔ CLI `platforms`
  列出 OmniPost 支持的所有平台及其能力：id、名称、capabilities、contentTypes、publishRequires（正式发布必填项）、extrasSchema（该平台专属参数：字段/类型/可选值/默认/是否已真机校准）、contentSpec（标题字数/标签数/图片数等写法规格）、calibratedAt（最近一次真机校准日期，空=未标注）。发布前按 contentSpec 裁标题、按 extrasSchema 决定要不要传 extras。
- `list_accounts` ↔ CLI `accounts`
  列出已登录的平台账号及登录态（valid/expired）。
- `list_alerts`
  登录态告警：哪些账号已失效需重登（expired）、哪些即将到期（expiring，含剩余小时数）、有哪些内容因登录失效正等着补发（retries）。另含授权对定时任务的影响：licensePaused = 因授权回落（试用结束/套餐到期）已暂停的任务数（升级后 48 小时内自动继续），licenseAtRisk = 仍待执行但按当前授权到点必被拦下的任务数。
**分发前先调一次**：目标账号在 expired 里就先让用户重登，否则这次发布必然失败；在 expiring 里就提醒用户「今天内顺手重登一次」。若 retries 非空，说明之前有内容没发出去——重登后会自动补发，不要重复写一篇。licensePaused/licenseAtRisk 非 0 时提醒用户升级专业版，否则定时内容发不出去。
- `list_account_groups` ↔ CLI `groups`
  列出账户分组：用户预先把一批账号命名成组（如「短视频组」=小红书+抖音+快手）。返回 [{name, members:[{platform,accountId,label,valid}]}]。用户可能直接说「发到 X 组」——此时在 create_draft/publish_post/schedule_post 传 groups:["X"] 即可，组内账户会自动并入发布目标。
- `check_auth` ↔ CLI `check-auth`
  检查指定平台账号当前是否处于登录态。
- `request_login` ↔ CLI `login`
  重新登录某个**已存在**的账号（弹登录窗口，真人完成）。新增账号请用 add_account。会阻塞直到登录成功或超时。会话过期（如微信「登录态超时」）时传 fresh=true 先清空旧会话强制重新扫码。
- `add_account` ↔ CLI `account add`
  为某平台**新增一个账号**：自动生成 accountId，弹出登录窗口由真人登录（支持同平台多账号，如多个 CSDN 号）。会阻塞直到登录成功或超时。返回新账号的 platform/accountId/label。
- `set_account_label` ↔ CLI `account label`
  给某账号改备注名（label）。
- `set_account_defaults` ↔ CLI `account defaults`
  锁定某账号的平台专属参数默认值（如抖音号永远勾「内容由 AI 生成」）。锁定后 publish_post/create_draft/schedule_post 省略该平台 extras 时自动套用；显式传入仍优先。不锁定时 OmniPost 会自动沿用该账号上次成功发布用的参数。clear=true 清除锁定。字段以 list_platforms 的 extrasSchema 为准，非法值直接报错。仅浏览器登录账号可设。
- `remove_account` ↔ CLI `account remove`
  移除某账号（登出并清除其本地会话/Cookie）。
- `create_draft` ↔ CLI `publish --mode draft`
  把一篇已写好的文章保存为草稿（不正式发布）。OmniPost 只做分发，不生成内容——请传入完整成品。
正文与视频**二选一**：图文传 markdown（或 html）；视频传 video（本地路径/URL，可无正文），视频平台见 video 字段说明。
**图片直接用文件路径或 http(s) URL，不要自己转 base64**：本地图用绝对路径（如 D:\\out\\cover.png）或相对路径（如 ./cover.png，配合 baseDir），OmniPost 会自动读盘并转存到各平台图床。
目标用 targets（推荐，支持同平台多账号）或 platforms 二选一：先调 list_accounts 拿到各账号的 {platform,accountId}，再用 targets 精确指定要发到哪些账号；只给 platforms 则发到这些平台下的**全部已登录账号**（同步分发）。
- `publish_post` ↔ CLI `publish`
  尝试正式发布文章（参数同 create_draft）。每个目标返回 stage（"draft"|"published"）与 published(bool)，自描述结果：
- 平台 supports.publish="auto" 且过校验 → published；缺必要项 → code "VALIDATION_FAILED" + missing 字段；
- 平台 supports.publish="manual"（如微信）→ 仅建草稿，返回 published:false + code "MANUAL_PUBLISH" + editorUrl（请引导人工到后台发布）。
先用 list_platforms 查 supports.publish / publishRequires 即可预判。
⚠️ 各平台内容规则不同：小红书/抖音/视频号等平台正文出现站外链接、二维码、微信号有**限流或封号风险**。OmniPost 不校验、不修改内容——发布前请按目标平台规则自行调整（装了 omnipost skill 的先读其 rules/<platform>.md）。
- `publish_draft` ↔ CLI `publish-draft`
  把一条**已存在的草稿**提升为正式发布（两步走第二步：先 create_draft 拿到 postId，审核后再调本工具）。用 list_posts({stage:"draft"}) 可查出草稿的 postId。manual 平台会返回 code "MANUAL_ONLY"（需到平台后台人工发布）。正式发布必填项（如**掘金的 category/tags/summary**）建草稿时通常没带——在本工具直接补传即可，不要用同标题重新 publish_post（会触发 24h 去重）。
- `schedule_post` ↔ CLI `schedule`
  把一篇文章安排到**指定时间**自动分发（建草稿或正式发布）。参数同 create_draft，外加触发时间：用 at（ISO8601 或 "YYYY-MM-DD HH:mm" 本地时间）或 scheduledAt（毫秒时间戳）二选一；mode 缺省 draft。创建时即锁定目标账号并留存内容快照。
两种交付方式（deliver，默认 auto）：① 平台自带定时——mode=publish 且目标平台声明了 platformSchedule（list_platforms 可查，如头条 / 抖音 / 快手 / 视频号 / 小红书 / B 站视频）且时间在其窗口内时，**立即**把内容连同发出时间交给平台，由平台到点发出，之后关机、登录失效都不影响（取消要到平台后台）；② 本地定时——其余目标到点由桌面应用后台执行（需保持应用运行；关闭期间错过的任务会在下次启动后立即补发）。平台定时设不上会自动改为本地定时并在任务 error 里说明。
spacingMinutes>0 时各目标按顺序错开 N 分钟。返回任务（多条时带 batch）。用 list_schedules 查看、cancel_schedule 取消。
- `list_schedules` ↔ CLI `schedules`
  查询定时发布任务（含触发时间、目标、模式、状态）。status 可选 pending/running/done/failed/canceled/paused（paused = 授权回落免费版后因需专业版而暂停，升级后 48 小时内自动继续，pauseReason=LICENSE_REQUIRED）。每项可带 deliverMode（platform=已/将交给平台自带定时，publishAt 为平台发出时间；local 或缺省=本地到点发）与 batch（间隔错峰 / 平台定时拆出的一组：size/done/failed/pending/nextAt）。返回 {items,total}。
- `cancel_schedule` ↔ CLI `schedule-cancel`
  取消一条**待执行或已暂停**的定时任务（status=pending/paused），或传 batchId 取消整批里所有未执行的。任务记录保留（状态置 canceled），如需彻底删除用 remove_schedule。id / batchId 来自 list_schedules。
- `get_schedule`
  取一条定时任务的**完整内容**（含 doc 正文快照、目标账号、执行结果）。list_schedules 为省流量不返回正文，要看/改内容前先用它取回。
- `update_schedule`
  修改一条**待执行**的定时任务（仅 status=pending 可改）：改触发时间、改目标账号、改草稿/正式发布、改内容。只传要改的字段，未传的保持不变。改时间用 at 或 scheduledAt；改内容需同时给 title + markdown/html（会整体替换内容快照）。
- `run_schedule`
  **立即执行**一条定时任务，不等到点（用于手动触发或失败重试）。已执行成功（status=done）的任务会被拒绝，避免向平台重复发布同一篇内容——需要再发请用 publish_post 重新提交。
- `remove_schedule`
  **彻底删除**一条定时任务记录（不可恢复）。只是想让它不执行、但保留记录，用 cancel_schedule。
- `save_account_group`
  创建或更新一个账户分组（按名称 upsert：同名则覆盖成员）。分组把一批账号命名成一组（如「短视频组」=小红书+抖音+快手），之后发布时传 groups:["短视频组"] 即可整组分发。members 直接给账号列表，或用 platforms 展开为这些平台下的全部已登录账号。
- `remove_account_group`
  删除一个账户分组（按分组名或 id）。只删分组这个「集合」，组内账号本身不受影响。
- `get_post`
  取一条发布记录的**完整内容**（含正文 body）。list_posts 为省流量只返回元数据 + hasBody 标记，需要看原文（如复用内容、排查发布结果）时用它按 id 取回。
- `get_status` ↔ CLI `status`
  检查 OmniPost 桌面应用是否在运行并就绪（返回运行状态 + 已接入平台数 + 已登录账号数）。建议在批量操作前先调用确认连通。
- `preview_content` ↔ CLI `preview`
  把 Markdown 渲染成 HTML 预览（用与发布相同的渲染器），用于发布前自检内容效果。返回 {html}。
- `list_platform_credentials` ↔ CLI `api-config list`
  列出各平台已配置的 API 凭据（敏感字段已打码）。用于查看微信公众号等平台的 API 配置状态。
- `set_platform_credentials` ↔ CLI `api-config set`
  为某平台配置 API 凭据（如微信公众号 appId/appSecret）。凭据仅保存在本机。海外平台支持多账号：用 accountId 区分（默认 default），各账号彼此隔离。可先用 list_platforms 查看该平台 apiConfig 需要哪些字段。
- `remove_platform_credentials` ↔ CLI `api-config remove`
  删除某平台某账号已配置的 API 凭据。
- `get_policy` ↔ CLI `policy show`
  读取发布策略配置（每账号每日上限 / 同标题去重 / 连续失败熔断 / 禁发时段 / 草稿门禁）。
- `set_policy` ↔ CLI `policy set`
  更新发布策略（合并写入）。global 改全局，platforms 改某平台覆盖。字段：dailyLimitPerAccount(0=不限)、dedupWindowHours(0=关)、circuitBreakerThreshold(0=关)、circuitBreakerCooldownMinutes、blackoutHours(如 [[0,7]])、minSpacingMinutes(多目标分发的最小间隔分钟，0=同时发；未显式传 spacingMinutes 时作为下限，按目标涉及平台取最大值)。
- `list_posts` ↔ CLI `posts`
  查询发布/草稿记录（含平台、账号、状态、编辑器链接），支持筛选与分页。返回 {items,total,limit,offset}。
- `list_stock_providers` ↔ CLI `images providers`
  列出免费图库（Pixabay / Pexels / Unsplash）及其配置状态——**在 search_stock_images 之前先调这个**，看哪些图库用户已配好 API Key（configured:true）。只有已配置的才能搜。返回 [{id, name, configured}]。若全部 configured:false，提示用户去 OmniPost 设置里填对应图库的免费 API Key（图库 Key 只能在应用内配置，agent 无法代设）。
- `search_stock_images` ↔ CLI `images search`
  在免费图库（Pixabay / Pexels / Unsplash）搜索可商用图片，用于给文章配图或做封面。provider 需用户已在 OmniPost 配好该图库的免费 API Key（可先用 list_stock_providers 查哪些已配置）——未配置会报错，此时请提示用户去 OmniPost 里配置。返回 {items:[{id, provider, downloadUrl(可直接作图片地址), thumb, width, height, author, source, trackUrl}], total}。注意：Pexels/Unsplash 授权要求署名——工具不会自动加署名，是否署名由你或用户决定，可用返回的 author/source 自行标注。
- `use_stock_image` ↔ CLI `images use`
  选用一张图库图片，返回可直接用于 publish_post 的公网图片 URL（放进 doc.cover 作封面，或写进正文 markdown 的 ![](url)）。**Unsplash 授权要求「使用时触发下载埋点」，本工具会自动完成**，故用 Unsplash 图前务必调用它。item 传 search_stock_images 返回的整条候选对象。返回 {url, author, source, attribution}（attribution 为建议署名文案，用不用由你决定）。
- `list_platform_categories` ↔ CLI `categories`
  查询某平台发文可选的分类/专栏（发布前调用，把返回的 name 填进 create_draft/publish_post 的 category 字段）。分类影响平台推荐/曝光，正式发布前建议先查。source:"live"=实时查平台（如掘金 8 大分类、CSDN 个人专栏——账号级）；"static"=固定枚举；supported:false 有两种：带 categoryRequired:true 表示**该平台分类必填但无列表接口**（按 note 的说明取值，如 51CTO 只收数字 cate_id），否则表示该平台无分类概念。返回 {supported, source, categoryRequired?, note?, categories:[{id,name}]}。
- `get_post_metrics` ↔ CLI `metrics`
  回采某条已发布文章的运营数据（阅读/点赞/评论/收藏 等）。**各平台维度不一致**——返回的 metrics.fields 是自描述数组，每项 {key, label:{zh-CN,en-US}, value}：掘金/CSDN 给 阅读+点赞+评论+收藏，知乎给 赞同+评论（无阅读），海外平台各异。**渲染时遍历 fields 用 label 显示，不要写死字段名**。支持哪些平台看 list_platforms 里 metrics=true（csdn / juejin / zhihu / dev.to / hashnode / reddit / mastodon 系 / bluesky…），每个平台的 metricFields 预告了会有哪些维度。只读、按需拉取 + 默认 1h 缓存（force=true 强制刷新）。传 recordId（来自 list_posts 的 id，会回写入库并返回 delta 增量）或 platform+postId。返回 {supported, metrics:{fields:[...], ...canonicalFlat}, delta?, cached?}；不支持的平台返回 supported:false。
- `get_publish_status` ↔ CLI `publish-status`
  回查一篇已发布/草稿的**真实存活状态**——解决"发出去到底成没成、是不是被拦/在审核"。归一化枚举：reviewing(审核中) / published(已发布) / rejected(未通过) / offline(已下架) / draft(草稿) / unknown(识别不了)。用发布时同一套登录态到平台自有接口查。传 recordId（来自 list_posts 的 id，最省事：自动取标题+postId 并把状态回写入库）或 platform + (postId / title)。返回 {supported, status, label, url?}；平台没实现回查则 supported:false。适合发布后核对、以及定期巡检"哪几篇被拦了"。
- `check_video`
  视频体检（只读本地文件，不上传、不联网）：读出视频的大小 / 时长 / 宽高 / 横竖版，并按各平台真实规格（取自平台创作者网站前端）给出 errors（平台一定会拒：超大小、超时长、太短、标题字数不够）与 warnings（会被截断或需注意）。发视频前先调它，按结果改文件或文案，省一次注定失败的上传。
- `rehearse_video`
  视频发布彩排（零上传）：对每个目标账号完整走一遍发布流程——查登录态、打开上传页、等文件框出现——在把视频放进文件框之前停下。返回每个目标的 checks（走通了哪些步骤）、page（上传页 URL、文件框、主要按钮、页面提示）、videoWarnings / missing（体检与必填项）。不落发布记录、不占配额。接口直传的平台（百家号/微博/搜狐）只校验登录与体检。正式账号上传有风控成本：真正上传前先彩排。
- `read_platform_page` ↔ CLI `page-read`
  运营观测（只读）：在某平台账号的**登录会话**里打开一个该平台页面，返回页面正文文本 + 页内同域链接列表。评论区、消息通知、创作者后台数据都用它看——你（agent）自己决定看哪个页面、自己读懂内容。返回的 links 可用于「跳页」：从创作者中心页找到评论管理页的链接，再 read 那个 URL。限制：URL 必须属于该平台自己的站点（白名单校验）；只读不点击；每账号 5 分钟最多 20 次。发现值得回复的评论时，用 open_platform_page 弹窗交给真人处理，不要尝试自动回复。
- `open_platform_page` ↔ CLI `page-open`
  运营行动入口：用某平台账号的登录会话弹出一个**可见**窗口并定位到指定页面（如某条评论所在页）。用途：你起草好回复文案后，开窗让**真人**粘贴发送——回复/点赞等互动动作永远由人完成（平台对机器互动风控严格）。同账号重复调用会复用同一窗口。
- `get_account_health` ↔ CLI `health`
  账号健康：查询最近的登录失效 / 限频风控 / 发布失败事件（OmniPost 在发布与数据回采中亲历的平台信号，结构化落盘），含按账号的 24h 分类计数与最近一条事件。排期发布前先看：某账号 rateLimit24h>0 就该避让、needLogin24h>0 就该提示用户重登。
- `get_account_overview`
  账号级运营数据（创作者中心概览）：粉丝/获赞/关注等**总量** + 平台自己给的**近 7 日（或昨日）指标**（含平台标注的环比 vs）+ OmniPost 本地快照算出的**较上次/日/周/月增长**（growth）。与 get_post_metrics（单篇）互补——看账号整体走势、判断发布节奏该不该调时用它。用发布同一套登录态到创作者后台**只读**读取；字段自描述：overview.fields / recent.fields 均为 [{key,label:{zh-CN,en-US},value,vs?,vsPercent?}]，**渲染时遍历 fields 用 label，不要写死字段名**。支持平台看 list_platforms 里 accountOverview=true：小红书/抖音/快手/视频号=读创作者中心页面文本（页面改版可能抓不到，届时带 warning，传 debug=true 可看抓到的文本行）；知乎/B站=站内接口；公众号=API 模式走官方统计（T+1）、扫码模式读后台首页。1h 缓存（force=true 强刷）；cachedOnly=true 只回本地最近一次快照、不触网。返回 {supported, overview, recent:{window:"7d"|"yesterday",fields}, growth:{sinceLast,day,week,month:{at,hours,delta}|null}, snapshots, account?, url?, cached?, warning?, note?}；不支持的平台 supported:false。涨跌好坏的判断是你的事，工具只如实读数。
- `get_metrics_overview` ↔ CLI `dashboard`
  运营看板：一次性汇总所有已发布文章的运营数据——各平台合计 + 分平台 + 逐篇明细，用于"整体运营概览"。字段自描述（totals / platforms[].fields 均为 [{key,label,value}]，跨平台按 canonical key 求和）。默认**只读用已入库数据**（打开即时、不发请求）；refresh=true 会逐条回采最新（走 1h 缓存，force=true 强刷，篇数多时较慢）。返回 {total, withData, totals:[...], platforms:[{platform,count,fields}], items:[{recordId,platform,title,postUrl,status,metrics}]}。

## 发布工作流
1. **`list_platforms`**：看支持哪些平台 + 每个平台的 `contentTypes`（`article`=图文 / 博客文，`video`=视频）。
2. **`list_accounts`**：确认目标平台已登录（`expired` 的账号要提示用户去 OmniPost 重新登录）。
3. **组织 doc**：
   - 通用字段：`title`、`tags`、`summary`。
   - **图文 / 文章** `type:'article'`：正文用 `markdown`；图片用本地**绝对路径**写进 markdown（`![](D:/path/a.png)`）或 `cover`。`cover` 对微信公众号草稿在扫码登录下也自动生效（自动上传素材 + 2.35:1/1:1 默认居中裁剪，v0.5.37+）。抖音/快手/视频号/小红书的图文要 **≥1 张图**。
   - **效果标记（可选，v0.5.39+）**：正文 markdown 里可直接内嵌 HTML 效果子集——
     `<u>下划线</u>`、`<mark>高亮</mark>`、`<span style="color:#e91e63">颜色</span>`、
     `<span style="background-color:#fff176">背景</span>`、`<span style="font-size:20px">字号</span>`、
     `<p style="text-align:center">居中段落</p>`。**微信公众号完整支持**（真机验证）；
     其他平台发布时自动降级为纯文本（剥标签留内容，不会露出裸标签），同一篇稿子可放心多平台同发。
     代码块里的 HTML 示例不受影响。适度使用：一篇文章重点强调 1-3 处即可，别整篇花花绿绿。
   - **视频** `type:'video'`：`video`（视频文件路径/URL）+ `cover`（封面图，**必填**）。
   - **本地文件直接给绝对路径**，OmniPost 自动读取，**不要转 base64**；用相对路径时配 `baseDir`。
   - **没有现成图片时可在线找图**：`list_stock_providers` 看用户配了哪些免费图库 → `search_stock_images` 搜可商用图 → `use_stock_image` 拿到公网 URL，直接放进 `cover` 或写进正文 `![](url)`。适合"要封面但手头没图"、给图文平台凑 ≥1 张图的场景。图库 Key 由用户在 OmniPost 里配置（agent 不能代设），没配会报错就提示用户去配。
4. **`publish_post`**：`targets:[{platform, accountId}]`（accountId 缺省 `default`）；`mode`：`'draft'`=建草稿/填好待人工发（**默认、最稳**），`'publish'`=自动正式发布。
5. **查状态**：用 `get_publish_status`（或发布结果里的 `reviewStatus`）确认真实状态（审核中 / 已发布 / 未通过 / 已下架）。

## 平台内容规则（发布前必读 — 降低限流/封号风险）
**OmniPost 只负责分发，不校验、不修改内容 —— 内容合规由你（agent）和用户负责。**各平台红线差异很大（站外链接 / 二维码 / 微信号 / 营销词等），随本 skill 附带 `rules/` 目录，按平台给出规则速查（含官方来源链接）：
  - `rules/baijiahao.md` — 百家号
  - `rules/bilibili.md` — B站
  - `rules/douyin.md` — 抖音
  - `rules/kuaishou.md` — 快手
  - `rules/shipinhao.md` — 微信视频号
  - `rules/toutiao.md` — 头条号
  - `rules/weibo.md` — 微博
  - `rules/weixin.md` — 微信公众号
  - `rules/xiaohongshu.md` — 小红书
  - `rules/zhihu.md` — 知乎
- **向上述平台建草稿或发布前，先读对应 `rules/<平台id>.md`**，按其红线调整内容（典型动作：删站外链接改为「搜索 XXX」话术、去二维码图、去微信号/手机号）。
- 未列出的平台（CSDN / 掘金 / 博客园 / Dev.to 等技术与海外平台）无特殊红线，正常发布即可。
- 规则为经验性整理，平台随时会调整，**以平台官方最新规则为准**；拿不准就用默认 draft 模式，让用户人工确认后再发。

## 写法规格与专属参数（内容由你生成，这里只给硬规格）
发布前按下表裁标题/标签（超 titleMax 会被 `VALIDATION_FAILED` 拦下）；同一篇稿发多平台要不同标题时，在 `targets[]` 每项带自己的 `title/summary/tags`。
专属参数（如「内容由 AI 生成」声明、可见范围、自制/转载）放在 `extras.<平台>.<键>`；**是否声明 AI 生成由用户决定，默认不勾**——用户说要标就传 `aiGenerated:true`，或用 `set_account_defaults` 给该账号锁定。省略时自动沿用该账号上次成功发布用的参数。标「未校准」的字段按页面可见文字定位，找不到会在结果 `extrasIgnored` 里说明。
| 平台 | 写法规格 | 专属参数（extras.<平台>.<键>） | 最近校准 |
|---|---|---|---|
| weixin | 标题最多 64 字；摘要最多 120 字 | — | 2026-09-08 |
| weibo | — | postType / videoType(未校准) / visibility(未校准) / allowDownload(未校准) | 2026-08-14 |
| xiaohongshu | 标题最多 20 字；正文最多 1000 字；图片最多 18 张 | aiGenerated(未校准) / visibility(未校准) | 2026-09-02 |
| shipinhao | 标题最多 22 字；正文最多 1000 字；图片最多 18 张；图文：标题 ≤22 字、≤18 张图 | original / aiGenerated(未校准) | — |
| douyin | 标题最多 30 字；正文最多 1000 字；图片最多 35 张 | aiGenerated(未校准) / visibility(未校准) / allowDownload(未校准) | — |
| kuaishou | 正文最多 1000 字 | aiGenerated(未校准) / visibility(未校准) / allowDownload(未校准) | — |
| bilibili | 标题最多 80 字；视频标题 ≤80 字 | aiGenerated(未校准) / visibility(未校准) | 2026-09-06 |
| baijiahao | — | aiGenerated(未校准) / statement(未校准) | — |
| sohu | 标题最少 5 字；标题最多 72 字 | — | — |
| cnblogs | — | postType | 2026-09-02 |
| toutiao | 标题最多 30 字 | — | 2026-07-02 |
| devto | 标签最多 4 个 | — | 2026-07-24 |

## 运营巡检（数据 / 评论 / 通知 / 账号健康）
发布之外，OmniPost 还是你做**账号运营**的手：
1. **看数字**：`get_metrics_overview`（合计+分平台+逐篇，含增量）；单篇用 `get_post_metrics`。
2. **看内容（评论/通知/后台）**：`read_platform_page` 在账号登录会话里**只读**打开任意该平台页面，
   返回正文文本 + 页内链接——看哪页、读懂什么是你的职责，OmniPost 只当眼睛。
   返回的 `links` 用于跳页（如从创作者中心找到评论管理入口再读下一页）。常用入口（页面可能改版，以页内链接为准）：
   - zhihu 创作者中心 `https://www.zhihu.com/creator`（评论在「互动管理」）
   - juejin 创作者中心 `https://juejin.cn/creator/home`（左侧「互动管理→评论管理」）
   - csdn 创作者中心 `https://mp.csdn.net/`（「评论管理」）
   - cnblogs 后台 `https://i.cnblogs.com/`（「评论」菜单）
   - segmentfault `https://segmentfault.com/user/notifications` · oschina `https://my.oschina.net/`
3. **回复评论 = 人来发**：发现值得回复的评论 → 起草文案 → `open_platform_page` 弹出可见窗口定位该页，
   请用户粘贴发送。**严禁尝试自动回复/自动点赞**（平台对机器互动的风控远严于阅读，封号红线）。
4. **排期前看健康**：`get_account_health` 汇总最近登录失效/限频风控/发布失败事件（24h 分类计数）。
   某账号 `rateLimit24h>0` → 今日避让；`needLogin24h>0` → 提示用户重登。

## 重要约定
- **默认走 `mode:'draft'`**；只有用户明确要「直接发/正式发布」才用 `mode:'publish'`。
- 正式发布前可先 `list_platforms` 看该平台 `supports.publish` 是 `auto`（能自动发）还是 `manual`（只建草稿，需人工到后台发，如慕课手记 / 语雀）。
- **微信公众号特例**：`supports.publish` 虽是 `auto`，但**只有 API 模式（配置了已认证服务号的 appId/appSecret）**才能自动正式发布——走「发布/freepublish（发表，不群发、不推送粉丝、生成公开链接）」；**仅浏览器扫码登录**的账号请求正式发布时只会建草稿并回报 `MANUAL_PUBLISH`（网页后台的公开动作只有「群发」，不可逆+限次，本工具不自动群发）。据结果里的 `note` 提示用户。此限制只针对「正式发布」这一步——**草稿的封面不受限**：扫码模式建草稿时 `cover` 也会自动上传并裁剪就位（v0.5.37+）。
- **正式发布看 `publishRequires` 补必填项**：有的平台要 `category` / `tags` / `summary`，缺了会返回 `VALIDATION_FAILED` 并列出缺哪些（含可选值）。典型：**掘金**正式发布必填 `category`（可选：后端 / 前端 / Android / iOS / 人工智能 / 开发工具 / 代码人生 / 阅读）+ ≥1 个 `tags` + `summary`。CLI 传分类用 `--category Android`（MCP/HTTP 在 doc 里带 `category` 字段）。
- **UI 自动化平台**（小红书 / 视频号 / 抖音 / 快手）正式发布时可能弹**验证码 / 滑块 / 风控**，需要用户在弹出的窗口里**人工完成**——发布结果会提示，照实告诉用户。
- 一次可发多个平台：`targets` 里列多个 `{platform, accountId}`。

## 接入信息（通用）
- **CLI**：`GET /api/health` 的 `cli.shell`；用法自查 `<cli.shell> --help`。
- **MCP over SSE**（Claude Code 原生支持）：`claude mcp add --transport sse omnipost http://127.0.0.1:<port>/sse`
- **MCP over stdio**（只支持 stdio 的客户端）：把 `GET /api/health` 返回的 `mcp.stdio`（`command` / `args` / `env`）填进客户端配置。
- **HTTP**：`http://127.0.0.1:<port>/api/...`；`/api/health` 永远是「这台机器怎么调」的权威答案。

## 隐私与风险（照实告诉用户）
- 账号登录态只保存在用户电脑的独立会话分区里，OmniPost 不上传凭据、不中转请求；匿名使用统计可在应用内关闭。
- **任何自动化发布都有平台风控风险**，OmniPost 不做也不宣传「防封」：默认进草稿箱、正式发布由用户决定、不自动点赞/评论/回复、不模拟真人行为。多账号、高频、同质内容是封号主因——按 `rules/` 降频、改写、人工确认。
- 内容合规由你和用户负责。

本 Skill 开源于 https://github.com/OmniGoAI/omnipost-skill （MIT）。用得不顺、平台改版发不出去，请开 issue。
