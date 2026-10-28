# OfficeBridge 抖音介绍视频 · 交接说明

给新会话里的 Claude 看的：读完这份就能接着做，不用从头问。文件都在 `claude/handoff` 分支上。

## 当前进度

- 口播稿已定稿（`OfficeBridge口播稿_定稿.txt`，7 段），用户已试听并确认配音
- 配音已生成：`audio/OfficeBridge配音_定稿.mp3`（2 分 49 秒），用 MiniMax 复刻音色，1.1 倍速，再做了后期提亮
- 成片第一版已做好并发给用户（数字人位置是占位框），等用户反馈
- **下一步：用 HeyGen 接口生成数字人视频，替换占位，出正式版**

## 用户与账号

- 抖音「王师兄的AI营地」，这是第一个视频。用户人设：五年后端开发，现在专心做 AI 开发，分享自己的开源项目和好用的开源项目
- 介绍对象：OfficeBridge（办公桥），https://github.com/wjianglong001/OfficeBridge ，写稿只依据 README，不夸大
- 用户不懂技术：回答用简单的中文，不中英混杂，缺信息时用选项卡确认
- **绝不能把任何 key 写进文件、提交到仓库或打印出来**。key 只从环境变量读

## 新会话准备

```bash
bash setup.sh        # 把仓库挂到 /home/user/obvideo，下载字体，整理录屏文件名
bash build_anim.sh   # 导出全部动画到 out/anim/（串行，约十几分钟，建议后台运行）
cd build && python3 make.py   # 合成成片到 out/OfficeBridge_成片_数字人占位版.mp4
```

需要 `pip install fonttools brotli` 才能重新生成字幕字体（`build/fonts/OBSub.ttf` 已提交，一般不用）。

## 已确定的决定

| 项目 | 决定 |
|---|---|
| 画面 | 横屏 1920×1080，30 帧，约 2 分 51 秒 |
| 动画风格 | 科技深色风（深蓝黑底，青到紫渐变），字体思源黑体 Noto Sans SC（OFL，可商用） |
| 数字人 | HeyGen 生成，绿幕背景。开头两段和结尾站在左侧（占位框 x140 y110，600×900）；四段演示时缩成左下角圆形小窗（x40 y770，直径 270） |
| 配音 | MiniMax 国内版 `https://api.minimax.cn`，音色 `wjianglong001_A3plus1_20261027`，模型 speech-2.8-hd，1.1 倍速，音调 0，不设情绪；逐段生成后段间留 0.5 秒拼接，再做后期提亮：`highpass=f=70,equalizer=f=220:t=q:w=1.0:g=-3,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=8000:t=q:w=1.5:g=2,loudnorm=I=-16:TP=-1.5` |
| 结尾引导 | 只引导关注账号 |
| 第 4 段录屏 | 选中豆包后就结束，用户同意就用这版 |

## 剪辑程序（build/）

- `align.py`：把口播稿按标点切成小句，用配音停顿算出每句的起止时间 → `clauses.json`
- `params.py`：由小句时间推算画面段边界、动画时间参数、录屏变速锚点（录屏秒数 ↔ 配音秒数）、叠加元素出场时间
- `make.py`：逐段合成（open、project、d1–d4、outro）→ 拼接 → 烧字幕（subs.ass）→ 配音轨。可单独重做某一步：`python3 make.py d2 final`

画面段（秒）：开场 0–22.21，项目介绍 22.21–46.58，能力一 46.58–68.07，能力二 68.07–97.83，能力三 97.83–126.81，能力四 126.81–135.95，结尾 135.95–170.62

## 录屏（4 段是同一次连续录屏切开的）

全部 1210×784、60 帧，按高度缩放到 1080 后水平居中（x=126）。关键时刻已写在 `params.py` 的 DEMO 锚点里。

## 下一步：HeyGen 数字人

用户已有自己的数字人形象（名字由用户告诉你），已同意通过环境变量 `HEYGEN_API_KEY` 提供 key，并放行 api.heygen.com、upload.heygen.com、docs.heygen.com、developers.heygen.com。

1. **先查官方文档**（docs.heygen.com / developers.heygen.com），确认当前版本的接口：上传音频得到素材 ID、用"音频驱动"方式生成数字人视频、纯色背景、查询生成状态。资料显示 v2 和 v3 接口并存，不要凭记忆
2. 用接口列出账号下的数字人，按用户给的名字找到 ID
3. 上传 `audio/OfficeBridge配音_定稿.mp3`，生成 1280×720、纯绿色背景（#00FF00）的数字人视频
4. 下载视频。下载地址的域名事先不知道，被拦时告诉用户要放行哪个域名
5. 合成：抠绿（chromakey）后替换 `make.py` 里 `placeholder_full.png`（开头结尾）和 `placeholder_pip.png`（演示段圆形小窗）两处占位。数字人视频与配音同步，按全片时间轴取对应时段
6. 提醒用户：接口调用可能和网页会员分开计费；用完把 key 作废

## 安全提醒

用户之前上传过一个含两个 MiniMax key 的配置文件，已出现在旧对话记录里，已建议用户作废重建。新会话里如需重新生成配音，从环境变量读取（`tools/tts.py`）。
