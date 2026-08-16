# 文杰学习 Wiki · 使用说明

## 这是什么

这是按 **Karpathy LLM Wiki 模式** 为 Huo Wenjie（文杰）建立的个人学习知识库，可以作为 Obsidian vault 打开。

LLM Wiki 的核心理念：
- 不是"每次查询重新发现知识"，而是 LLM 持续维护一个**结构化、互相链接的 markdown 文件集合**
- 学生在文件系统里成长，LLM 负责把新信息归到正确的 entity / pattern / plan
- 家长作为 "co-pilot"，定期 review 确认

## 怎么打开

1. 下载 `wenjie-wiki.zip`
2. 解压到任意位置
3. 打开 Obsidian → "Open folder as vault" → 选择解压出来的 `wenjie-wiki/` 文件夹
4. 看到左侧侧栏有完整的目录树

## 目录结构

```
wenjie-wiki/
├── index.md                  ← 主页（从这里开始）
├── README.md                 ← 本文件
├── profile/                  ← 学生画像
│   ├── basic.md              基本信息（年龄、学校、家庭）
│   ├── learning-style.md     学习风格（听觉+动觉偏强）
│   ├── motivation.md         动机特征
│   └── goals.md              6 年目标（PSLE 4-6 + RI/HCI IP）
├── subjects/                 ← 5 个学科
│   ├── english/
│   │   ├── mastery.md        英文总体掌握度
│   │   ├── entities/         知识实体（letter-sounds / cvc / sight-words 等）
│   │   └── mistakes/         错误模式（pattern-001 等）
│   ├── chinese/
│   │   ├── mastery.md
│   │   ├── entities/
│   │   └── mistakes/
│   ├── math/                 数学
│   │   ├── mastery.md
│   │   ├── entities/         mental-arithmetic / abacus / math-vocab / word-problems
│   ├── swimming/             游泳
│   │   ├── mastery.md
│   │   ├── entities/         4 泳姿 + Swim Safe + NSG
│   │   └── milestones/       M1-M6
│   └── piano/                钢琴
│       ├── mastery.md
│       ├── entities/         Trinity / SPAF / SYF / CCA 角色
│       └── milestones/
├── cca/                      ← CCA 综合视图
│   ├── swimming.md
│   ├── piano.md
│   └── conduct-grade.md     操行记录
├── plans/                    ← 计划
│   ├── index.md              计划入口
│   ├── quarterly.md          季度目标
│   ├── weekly/               周计划
│   │   ├── W01.md
│   │   ├── W02.md
│   │   └── ...
│   └── daily/                日计划
│       ├── 2026-08-15.md
│       └── ...
├── school-readiness/         ← 6 年小学课程进度
│   ├── p1-curriculum.md
│   ├── p2-curriculum.md
│   ├── p3-curriculum.md
│   ├── p4-curriculum.md
│   ├── p5-curriculum.md
│   ├── p6-curriculum.md
│   └── dsa-overview.md
├── dsa/                      ← DSA-Sec 信息
│   ├── raffles-institution.md
│   ├── hwa-chong-institution.md
│   ├── dsa-application-timeline.md
│   └── requirements.md
├── resources/                ← 资源购买清单
│   ├── bought.md
│   ├── to-buy-now.md
│   └── to-buy-by-september.md
└── log.md                    ← 时序日志（不可变）
```

## 怎么更新

每次有新信息进来（测评结果、考试、观察），告诉 LLM：
- "今天 8/17 Phonics 错了 6 个"
- "文杰心算今天 75% 正确率"
- "今天他突然能自己读完 L7"

LLM 会：
1. 决定归到哪个 entity / pattern / plan
2. 更新 mastery.md 的进度
3. 追加到 log.md
4. 触发 pattern 时新建 mistakes/pattern-XXX.md
5. 询问家长确认（co-pilot 模式）

## wikilinks 用法

文件之间用 `[[文件路径]]` 链接，例如：
- `[[subjects/english/mastery]]` 链接到英文掌握度
- `[[subjects/english/mistakes/pattern-001-long-short-vowels]]` 链接到具体错误模式
- `[[plans/weekly/W01]]` 链接到 W01 计划

Obsidian 的 backlinks 功能会自动显示"哪些文件链接了这里"。

## 同步 UI

工作目录 `~/Documents/Wenjie/` 里的 HTML UI（master-overview、growth-garden 等）会和这个 wiki 保持同步更新。每个 UI 底部都有跳转到具体 wiki 文档的链接。

| UI 文件 | 受众 | 用途 |
|---|---|---|
| `master-overview.html` | 家长 | 6 年全景速览 |
| `progress-dashboard.html` | 家长 | 12 维度 + 14 天倒计时 |
| `daily-plan.html` | 家长 | 每日时间表 + 任务清单 |
| `school-readiness.html` | 家长 | 入学前 20 周冲刺路线图 |
| `cca-tracker.html` | 家长 | 游泳 + 钢琴双通道 |
| **`growth-garden.html`** | **文杰** | **每日打开看的成长花园（儿童视图）** |

> 🌸 `growth-garden.html` 是**儿童视图**——文杰每天打开看自己的花，不显示分数，只显示"今天长出了几瓣"。**只看见生长，看不见失败**。家长每天晚上 21:00 前编辑顶部 `GARDEN` 数据对象即可。
>
> **结构**（从上到下）：
> 1. 🗺️ 探险地图 —— 5 座岛 + 5 个里程碑小路 + 探险家 🧒 + 今日花开
> 2. 🌸 今日花朵 —— 5 张技能卡（花瓣 1-5 + 妈妈备注）
> 3. ✨ 今日最棒 —— 一句话高亮
> 4. 🌳 本周花园 —— 7 天可视化
> 5. 💛 妈妈的话 —— 每日一句温暖的话
