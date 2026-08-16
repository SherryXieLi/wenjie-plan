# 同步策略 · SYNC

> 这是 Mavis（minimax agent）和 Obsidian 之间的同步说明。

## 同步模式

**采用"半自动"模式**（最实用 + 最稳）：

| 数据更新 | 同步位置 | 谁做 |
|---|---|---|
| 用户在 Mavis 里说新信息 | Mavis 自动写到 3 个地方 | Mavis |
| Obsidian watch 文件 | 自动 reload | Obsidian |
| Mavis 工作目录的 wenjie-wiki/ | 同步到 ~/Documents/Wenjie/wiki/ | Mavis |
| UI HTML 文件（6 个，含儿童视图 growth-garden.html） | 同步到 ~/Documents/Wenjie/*.html | Mavis |

**用户需要做的**：在 Obsidian 里 "Open folder as vault" → 选 `~/Documents/Wenjie/wiki/`，之后 Mavis 改任何文件，Obsidian 会自动 reload。

## 触发流程

1. **你**告诉 Mavis 新信息（例：今天 Phonics 错 6 个）
2. **Mavis** 决定归到哪个文件，更新：
   - `~/Documents/Wenjie/wiki/subjects/english/mastery.md`（更新评分）
   - `~/Documents/Wenjie/wiki/subjects/english/mistakes/pattern-001-long-short-vowels.md`（更新频率）
   - `~/Documents/Wenjie/wiki/log.md`（追加事件）
3. **Obsidian** 自动 watch 到文件变化 → 立刻在 UI 显示更新
4. **不需要你**手动复制/刷新

## Mavis 的写入位置（每次同步）

```
~/Documents/Wenjie/wiki/                      ← Obsidian vault（你打开的位置）
~/.minimax-agent-cn/projects/wenjie-wiki/      ← Mavis 项目副本
~/Documents/Wenjie/*.html                     ← 5 个 HTML UI
~/.mavis/memory/user.md                        ← 长期 memory
```

## 高级方案（如果需要"完全自动"）

### 方案 B：Obsidian Local REST API
- 在 Obsidian 装 "Local REST API" 插件
- Mavis 通过 HTTP 直接写到 Obsidian
- 配置步骤：设置 → 第三方插件 → 装 "Local REST API" → 复制 API key
- 然后告诉 Mavis："API key 是 xxxxx"

### 方案 C：本地 watch + sync 脚本
- 装 fswatch / launchd 监控 wenjie-wiki/ 目录
- Mavis 改动 → 自动 sync 到 ~/Documents/Wenjie/wiki/
- 适合"完全无人值守"场景

## 当前选择：**方案 A（半自动）**
- 原因：Mavis 必须由用户告知新数据才能更新（LLM 不主动监听生活）
- "半自动" = 用户告知 → Mavis 写 → Obsidian 自动 reload
- 这是 LLM Wiki 模式最自然的形态

## 关联
- [[README#怎么打开]] · [[README#怎么更新]]
- [[index]]
