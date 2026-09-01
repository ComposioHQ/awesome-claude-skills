# md2video-audio-skill

One Markdown file + a one-click command = professional-grade talking-head videos. ｜ 一个 Markdown 文件 + 一键命令 = 专业级口播视频。

- ✨ `/md2video-audio` 是什么神仙技能？

这是一个**完全免费**的 Markdown 转视频技能，能把你的 `.md` 文件直接编译成带真人配音的 MP4 视频：

```
Markdown 文档 → Marp 幻灯片 + Edge-TTS 晓晓配音 → 成品 MP4
```

- 🔥 核心亮点

| 特性           | 说明                                         |
| -------------- | -------------------------------------------- |
| 💰 **零成本**   | 不用 OpenAI、不用阿里云、不用任何付费 API    |
| 🎙️ **真人配音** | 微软 Edge-TTS 晓晓音色，自然到以为是真人录的 |
| 🖼️ **自动配图** | Marp 渲染精美幻灯片作为讲解画面              |
| ⚡ **一键生成** | 一条命令搞定全部流程                         |
| **标准输出**   | 直接产出可上传抖音/B 站/YouTube 的 MP4       |

---

## 🚀 怎么用？超简单！

```bash
#安装方法
#1 npx安装
npx skills add https://www.modelscope.cn/skills/nihaoModelscope/amd2video-audio
#2 SDK安装
pip install --upgrade modelscope
modelscope skills add nihaoModelscope/amd2video-audio
#3 bash安装
curl -fsSL https://www.modelscope.cn/skills/install.sh | bash -s -- nihaoModelscope/amd2video-audio

#使用方法
# 在 Claude Code 里输入： 其他agent也可轻松适配
/md2video-audio your-presentation.md
```

就这样。没有复杂配置，没有 API 密钥，没有第三方依赖。

----

- 适合什么场景？

-  **知识分享**：技术教程、读书笔记、概念讲解
-  💼 **工作汇报**：项目复盘、数据分析、进度同步  
-  **在线课程**：课件转视频、微课制作
-  📢 **营销内容**：产品介绍、功能演示、活动预告
-  **个人 IP**：日更视频、观点输出、经验总结

---

- 💡 为什么推荐它？

1. **真的免费** —— 很多类似工具最后都要你买积分、充会员，这个是纯本地方案
2. **质量靠谱** —— 晓晓音色是目前最自然的中文 TTS 之一
3. **门槛极低** —— 会写 Markdown 就会用，不用学 Premiere
4. **可控性强** —— 文案改 MD 就行，不用重新录制

-----

# md2video-audio-skill- EN

One Markdown file + a one-click command = professional-grade talking-head videos.

✨ What kind of magical skill is `/md2video-audio`?

This is a completely free Markdown-to-video skill that directly compiles your `.md` files into MP4 videos with realistic human-like voiceovers:

Markdown Document → Marp Slides + Edge-TTS Xiaoxiao Voice → Finished MP4

🔥 Core Highlights

| **Feature**              | **Description**                                              |
| ------------------------ | ------------------------------------------------------------ |
| 💰 Zero Cost              | No OpenAI, no Alibaba Cloud, no paid APIs required.          |
| 🎙️ Realistic Voiceover    | Powered by Microsoft Edge-TTS Xiaoxiao voice, so natural it sounds like a real person. |
| 🖼️ Auto-Generated Visuals | Uses Marp to render stunning slides as presentation visuals. |
| ⚡ One-Click Generation   | Complete the entire workflow with a single command.          |
| 📦 Standard Output        | Directly produces MP4 videos ready to upload to TikTok, Bilibili, or YouTube. |

🚀 How to use? Super simple!

- Installation Methods

1. npx installation

`npx skills add https://www.modelscope.cn/skills/nihaoModelscope/amd2video-audio`

2. SDK installation

`pip install --upgrade modelscope`

`modelscope skills add nihaoModelscope/amd2video-audio`

3. bash installation

`curl -fsSL https://www.modelscope.cn/skills/install.sh | bash -s -- nihaoModelscope/amd2video-audio`

## Usage

- Type in Claude Code (easily adaptable for other agents):

`/md2video-audio your-presentation.md`

That's it. No complicated setup, no API keys, no third-party dependencies.

- Suitable Scenarios?

  - Knowledge Sharing: Tech tutorials, reading notes, concept explanations

  - 💼 Work Reports: Project reviews, data analysis, progress updates

  - Online Courses: Slide-to-video conversion, micro-lesson production

  - 📢 Marketing Content: Product introductions, feature demos, event announcements

  - Personal Branding: Daily video updates, opinion publishing, experience summaries

- 💡 Why recommend it?

  - Truly Free: Many similar tools eventually require buying credits or memberships; this is a purely local solution.

  - Reliable Quality: The Xiaoxiao voice is one of the most natural Chinese TTS options available.

  - Extremely Low Barrier: If you can write Markdown, you can use it—no Premiere required.

  - High Controllability: Just edit the Markdown text to make changes, no need to re-record.
