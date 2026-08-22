# 文杰学习计划 · 项目交接文档

> 给新 agent 看的"项目全貌"，5 分钟读完即可上手。

---

## 🎯 项目目标

为 **文杰（霍文杰，5岁11个月，K2 末）** 搭建学习计划系统，所有者是妈妈 **谢莉 (SherryXieLi)**。
- **目标学校**：Singapore RI / HCI（顶级学校）
- **关键时间**：P3 (2030) DSA 申请
- **2026-08-22 周六 当前进度**：节奏建立 W01 完成，进入 W02 稳态期

---

## 📁 项目位置

- **工作目录**：`~/Documents/Wenjie/`
- **主项目子目录**：`wiki/` `wenjie-*.html` `build-wiki.py` `update.sh`
- **部署**：GitHub Pages 自动部署（`wenjieplan` alias 一键 build+push）

---

## 🌐 4 页 IA（6→3 页已重构）

| 页面 | 用途 | 适用 |
|---|---|---|
| `wenjie-plan.html` | 6 年总战略 + 时间线 + 维度 | 家长 |
| `wenjie-progress.html` | 进度仪表板 + CCA + 错题 | 家长 |
| `wenjie-daily-plan.html` | 今日任务 | 家长 |
| **`wenjie-growth-garden.html`** | **英雄学院 · 娃看版** | **娃 + 家长** |

**共享组件**：`wenjie-shared.css` + `wenjie-shared.js`（面包屑、页脚）

---

## 🎨 娃看版设计原则

1. **娃看版默认**：极简、大 emoji、视觉化
2. **家长看模式**：手动切换（右上角按钮）
3. **任务完成互动**：每个任务卡有 [⚔️ 打败它] 按钮，localStorage 记忆
4. **战斗动画**：完成所有任务 → [🎉 打败怪兽] 按钮 → 全屏庆祝覆盖层

---

## 🤖 当前状态（重要）

### DSH 模型配置
- 文件：`~/.dsh/settings.yaml`
- **当前默认模型**：`qwen3-vl-plus`（视觉语言）
- 视觉模型支持：`qwen3-vl-plus`, `qwen3-vl-flash`, `qwen-vl-ocr`
- API endpoint：`https://ws-7z36atunwt2uhkmr.cn-beijing.maas.aliyuncs.com/compatible-mode/v1`
- API key：`~/.config/wenjie-plan/qwen-api-key`（权限 600）

### 历史背景
- 之前用 MiniMax-M3（文本模型，看不到图）
- 妈妈有 Qwen 3 VL workspace API key（JWT 格式 `sk-ws-...`）
- 配置好 `input: [text, image]` 才能让模型支持视觉
- DSH 进程需要重启才能让 settings.yaml 生效

---

## 🔧 关键工具脚本

| 文件 | 用途 |
|---|---|
| `qwen-vl-vision.py` | Qwen 3 VL 调用（看图 + 数学错题提取）|
| `generate-worksheet.py` | 数学/Phonics/汉字练习册生成器 |
| `ocr-mistake.sh` | tesseract OCR 错题 |
| `update.sh` (alias `wenjieplan`) | build + commit + push 一键 |
| `build-wiki.py` | Wiki → HTML 渲染 |

### Qwen 3 VL 调用方法

```bash
source ~/.zshrc  # 加载 DASHSCOPE_API_KEY
python3 qwen-vl-vision.py photo.jpg --mode math
```

输出包括：题目类型、错题 + 正确题、错误模式、能力总结。

---

## 📅 当前周计划 (W02 · 8/24-8/30)

| 日 | 类型 | 重点 |
|---|---|---|
| 8/24 周一 | 🟢 常规 | 60 min 学习 |
| 8/25 周二 | 🟡 半休 | 钢琴课 + 奶奶陪做 30 min |
| 8/26 周三 | 🟡 半休 | 钢琴 |
| 8/27 周四 | 🟢 轻量 | 20 min 轻量学习 |
| 8/28 周五 | 🟢 常规 | 60 min 学习 |
| **8/29 周六** | 🟠 **考级日** | **上午 10:30 珠算考级**（项目 + 钢琴移到傍晚）|
| 8/30 周日 | 🟠 复盘 | 项目 + Wiki 复盘 21:00-21:30 |

**🆕 W02 新增**：每天 19:15-19:30 珠算 15 min（妈妈 8/22 要求）
**W01（8/15-8/21）**：节奏建立周（已完成）

---

## 🎯 关键决策历史

### v4.3 时间表（8/18 妈妈定）
- 周末项目日改到早上 8:30-9:30（精力最好时段）
- 周末钢琴早上版 9:30-9:50（v4.3 第五次变化）
- 工作日保持晚上学习（19:15-20:15）
- 21:00 早睡

### 5:2:1 节奏
- 5 天常规 + 2 天轻量 + 1 天项目
- 周二/周三 半休（钢琴 + 自由）
- 周四 轻量
- 周末 项目日早上版

### 考级日特殊 (8/29)
- 上午 9:30 出发
- 10:00 到考场
- 10:30-11:30 考级
- 下午休息
- 17:00-18:00 项目（傍晚版）
- 18:00-18:30 钢琴（傍晚版）
- 19:15 考级日特殊自由

### 设计哲学
- **不猜数据**：错题必须有真实题面，不编
- **考级 baseline**：珠算 70 分过关，错 >1 题 = 不及格
- **DSA 学术**：P5 + P6 上半年平均分 ≥ 50%（底线），RI/HCI 实际录取需 75%+
- **DSA 游泳路径**：M3 → M5 (P5 NSG 区前 4) → M6 (P6 NSG 全国前 8)
- **总学习时长**：270 min/周（4.5 小时/周）

---

## 🎬 英雄学院 · 奥特曼元素

- **Ultraman Tiga v3 SVG**：高尖头冠 + 紫色护甲 V 形 + 浅蓝计时器 + 外眼角下垂眼睛（旋转 ±22° 椭圆）
- 战斗回放：5 个怪兽自动循环动画
- 互动完成：所有任务完成 → 庆祝覆盖层 → 奥特曼打败怪兽动画
- 迪迦眼睛关键：外眼角下垂（不是大圆眼睛）

---

## 🛠️ 常用命令

```bash
# 妈妈常用
wenjieplan              # build + commit + push 一键
ocrmistake photo.heic   # OCR 错题图片

# 工具调用
python3 qwen-vl-vision.py photo.jpg --mode math
python3 generate-worksheet.py math-add --difficulty 2 --count 10

# DSH
dsh web                 # 启动 web GUI（端口 3080）
```

---

## 📱 访问方式

- **本机**：`http://127.0.0.1:3080`
- **手机（ngrok）**：`https://reply-dexterous-steerable.ngrok-free.dev`
- **部署**：`https://sherryxieli.github.io/wenjie-plan/`

---

## 🎯 新 agent 应该做的第一件事

1. **读这个文件** ✅（妈妈让你读的）
2. **问妈妈**：今天有什么需要？错题照片？改进？测试？
3. **不要重新问基础问题**：项目结构、计划、决策都已经定了

---

## ⚠️ 待办事项（妈妈还没确认/完成）

- [ ] 8/22 真实错题（之前我编的 7+5=13 不算）
- [ ] 8/29 考场地点 + 考级级别
- [ ] 8/22 晚上数学错题（待妈妈做完后告诉我）
- [ ] 8/18 Phonics 4 个新发音具体内容
- [ ] ngrok URL 测试手机 DSH

---

## 📞 妈妈偏好

- **沟通**：直接、不啰嗦、产品思维强
- **设计**：极简、视觉化、娃优先
- **决策**：用事实和数据，不靠猜
- **工具**：自动化优先（OCR、自动生成、互动按钮）

---

**当前 agent 上次工作：2026-08-22 晚（妈妈在 DSH 切到 qwen3-vl-plus + 设置 `input: [text, image]` + 重启 DSH）**

**下一步**：妈妈发送错题照片 → 视觉识别 → 生成针对练习册
