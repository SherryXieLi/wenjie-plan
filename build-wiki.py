#!/usr/bin/env python3
"""
build-wiki.py · Wiki → HTML 构建脚本（含间隔重复算法）
"""
import json
import re
import yaml
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path(__file__).parent
WIKI_DAILY = BASE / 'wiki' / 'plans' / 'daily'
WIKI_MISTAKES = BASE / 'wiki' / 'mistakes'
OUTPUT_HTML = BASE / 'wenjie-daily-plan.html'
TEMPLATE = BASE / 'wenjie-daily.template.html'
DASHBOARD_OUTPUT = BASE / 'wenjie-progress-dashboard.html'
DASHBOARD_TEMPLATE = BASE / 'wenjie-progress-dashboard.template.html'
ACADEMY_OUTPUT = BASE / 'wenjie-growth-garden.html'
ACADEMY_TEMPLATE = BASE / 'wenjie-academy.template.html'
PLAN_OUTPUT = BASE / 'wenjie-plan.html'
PLAN_TEMPLATE = BASE / 'wenjie-plan.template.html'
PROGRESS_OUTPUT = BASE / 'wenjie-progress.html'
PROGRESS_TEMPLATE = BASE / 'wenjie-progress.template.html'

# 间隔重复算法（Karpathy ML 视角）
SR_INTERVALS = [1, 3, 7, 14, 30]  # days


def parse_md_sections(md_text):
    """简单 Markdown 解析"""
    lines = md_text.split('\n')
    title = ''
    sections = []
    current = None

    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
        elif line.startswith('## '):
            if current:
                sections.append(current)
            current = {'heading': line[3:].strip(), 'body': []}
        elif current is not None:
            current['body'].append(line)

    if current:
        sections.append(current)
    return {'title': title, 'sections': sections}


def md_to_html(md_text):
    """轻量 Markdown → HTML"""
    text = md_text
    text = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\*🎯(.+?)\*\*$', r'<h1>🎯\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    lines = text.split('\n')
    new_lines = []
    in_table = False
    table_lines = []

    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            in_table = True
            table_lines.append(line)
        else:
            if in_table:
                new_lines.append(render_table(table_lines))
                table_lines = []
                in_table = False
            new_lines.append(line)

    if in_table and table_lines:
        new_lines.append(render_table(table_lines))

    text = '\n'.join(new_lines)
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    text = re.sub(r'^---+$', r'<hr>', text, flags=re.MULTILINE)
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', text, flags=re.DOTALL)
    text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    paragraphs = text.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            p = f'<p>{p}</p>'
        new_paragraphs.append(p)
    text = '\n'.join(new_paragraphs)
    return text


def render_table(lines):
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip('|').split('|')]
        rows.append(cells)
    rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]
    if not rows:
        return ''
    html = '<table>'
    if len(rows) >= 1:
        html += '<thead><tr>'
        for cell in rows[0]:
            html += f'<th>{cell}</th>'
        html += '</tr></thead>'
    if len(rows) >= 2:
        html += '<tbody>'
        for row in rows[1:]:
            html += '<tr>'
            for cell in row:
                html += f'<td>{cell}</td>'
            html += '</tr>'
        html += '</tbody>'
    html += '</table>'
    return html


def load_mistake_frontmatter(filepath):
    """读取错题的 frontmatter（YAML）"""
    content = filepath.read_text(encoding='utf-8')
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None, content
    try:
        fm = yaml.safe_load(match.group(1))
        return fm, content
    except:
        return None, content


def find_due_reviews(today_str):
    """找今天需要复习的错题（间隔重复）"""
    today = datetime.strptime(today_str, '%Y-%m-%d').date()
    due_reviews = []
    pending = []  # 未来要复习的

    for md_file in WIKI_MISTAKES.rglob('*.md'):
        if md_file.name == 'index.md':
            continue
        fm, _ = load_mistake_frontmatter(md_file)
        if not fm or fm.get('status') != 'pending':
            continue

        schedule = fm.get('review_schedule', [])
        # 找到第一个 >= today 的复习日期
        for review_date in schedule:
            # yaml 可能返回 date 对象或字符串
            if isinstance(review_date, str):
                rd = datetime.strptime(review_date, '%Y-%m-%d').date()
            else:
                rd = review_date  # 已经是 date 对象
            review_str = rd.strftime('%Y-%m-%d')
            if rd == today:
                due_reviews.append({
                    'id': fm.get('id'),
                    'subject': fm.get('subject'),
                    'type': fm.get('type'),
                    'problem': fm.get('problem'),
                    'wrong': fm.get('wrong'),
                    'right': fm.get('right'),
                    'review_date': review_str,
                    'path': str(md_file.relative_to(BASE))
                })
                break
            elif rd > today:
                pending.append({
                    'id': fm.get('id'),
                    'subject': fm.get('subject'),
                    'type': fm.get('type'),
                    'problem': fm.get('problem'),
                    'wrong': fm.get('wrong'),
                    'right': fm.get('right'),
                    'review_date': review_str,
                    'path': str(md_file.relative_to(BASE))
                })
                break

    pending.sort(key=lambda x: x['review_date'])
    return due_reviews, pending


def render_reviews_section(today_str):
    """渲染「今日复习」HTML"""
    due, pending = find_due_reviews(today_str)

    if due:
        items = ''
        for r in due:
            items += f'''<div class="review-card">
                <div class="review-head">
                    <span class="review-tag" data-subject="{r['subject']}">{r['subject'].upper()}</span>
                    <span class="review-date">📅 {r['review_date']}</span>
                </div>
                <div class="review-problem">
                    <strong>{r['problem']}</strong>
                    · 文杰答：<span class="wrong">{r['wrong']}</span>
                    · 正解：<span class="right">{r['right']}</span>
                </div>
                <div class="review-type">错因：{r['type']}</div>
                <div class="review-id">#{r['id']}</div>
            </div>'''
        return f'''<section class="review-section">
            <h2>🔥 今日复习 · {len(due)} 道错题</h2>
            <p class="review-hint">按 <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f" target="_blank">间隔重复</a> 算法自动安排 · 每道题 5 min 复习</p>
            <div class="review-list">{items}</div>
        </section>'''
    else:
        return '''<section class="review-section">
            <h2>📭 今日复习 · 无任务</h2>
            <p class="review-hint">今天没有错题要复习。专心新内容。</p>
        </section>'''


def build():
    print(f"📚 扫描 {WIKI_DAILY} ...")

    daily_files = sorted(WIKI_DAILY.glob('*.md'))
    if not daily_files:
        print(f"❌ 没找到 Wiki 文件 in {WIKI_DAILY}")
        return False

    daily_data = []
    daily_perf = {}  # date -> {math, mental, phonics, ...}

    for f in daily_files:
        date = f.stem
        md_text = f.read_text(encoding='utf-8')
        parsed = parse_md_sections(md_text)

        for sec in parsed['sections']:
            sec['html'] = md_to_html('\n'.join(sec['body']))

        daily_data.append({
            'date': date,
            'title': parsed['title'],
            'sections': parsed['sections']
        })

        # 提取表现数据（粗略）
        perf = {'math_correct': None, 'mental_correct': None, 'completed': True}
        for sec in parsed['sections']:
            body = '\n'.join(sec['body'])
            if '珠算' in sec['heading']:
                m = re.search(r'(\d+)\s*题.*?错\s*(\d+)', body)
                if m:
                    perf['math_correct'] = int(m.group(1)) - int(m.group(2))
                    perf['math_total'] = int(m.group(1))
            if '心算' in sec['heading']:
                m = re.search(r'(\d+)\s*题.*?错\s*(\d+)', body)
                if m:
                    perf['mental_correct'] = int(m.group(1)) - int(m.group(2))
                    perf['mental_total'] = int(m.group(1))
            if '取消' in body or '眼睛疼' in body:
                perf['completed'] = False
        daily_perf[date] = perf
        print(f"  ✅ {date}: {parsed['title'][:50]}")

    today_str = datetime.now().strftime('%Y-%m-%d')
    default_date = today_str
    for d in daily_data:
        if d['date'] <= today_str:
            default_date = d['date']

    reviews_html = render_reviews_section(default_date)

    daily_json = json.dumps(daily_data, ensure_ascii=False, indent=2)
    default_date_json = json.dumps(default_date)

    if not TEMPLATE.exists():
        print(f"❌ 模板不存在: {TEMPLATE}")
        return False

    template = TEMPLATE.read_text(encoding='utf-8')

    html = template.replace('__DAILY_DATA__', daily_json)
    html = html.replace('__DEFAULT_DATE__', default_date_json)
    html = html.replace('__BUILD_TIME__', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    html = html.replace('__TOTAL_DAYS__', str(len(daily_data)))
    html = html.replace('__REVIEWS_HTML__', reviews_html)

    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(f"\n✅ 生成 {OUTPUT_HTML}")
    print(f"   - {len(daily_data)} 天的内容已烤入")
    print(f"   - 默认日期: {default_date}")
    print(f"   - 复习提醒: {len(find_due_reviews(default_date)[0])} 道")
    print(f"   - 文件大小: {OUTPUT_HTML.stat().st_size:,} 字节")

    # ===== 生成仪表盘 =====
    print(f"\n📊 生成仪表盘...")
    build_dashboard(daily_perf)

    # ===== 旧仪表盘改跳转 =====
    redirect_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=wenjie-progress.html">
  <title>页面已迁移</title>
  <style>
    body { font-family: -apple-system, sans-serif; background: #f7f5f0; color: #2a2a2a;
      display: flex; align-items: center; justify-content: center; min-height: 100vh;
      margin: 0; text-align: center; padding: 24px; }
    .box { background: white; padding: 32px; border-radius: 14px; border: 1px solid #e9e3d6; max-width: 400px; }
    h1 { color: #2f6f5e; margin: 0 0 12px; font-size: 22px; }
    p { color: #7c7a72; font-size: 14px; line-height: 1.6; margin: 8px 0; }
    a { display: inline-block; margin-top: 16px; padding: 8px 16px; background: #2f6f5e;
      color: white; text-decoration: none; border-radius: 6px; font-size: 13px; }
  </style>
</head>
<body>
  <div class="box">
    <h1>页面已迁移 🚀</h1>
    <p>仪表盘 + CCA 已合并到 wenjie-progress.html</p>
    <p>正在自动跳转...</p>
    <a href="wenjie-progress.html">手动跳转 →</a>
  </div>
</body>
</html>'''
    DASHBOARD_OUTPUT.write_text(redirect_html, encoding='utf-8')
    print(f"  🔄 {DASHBOARD_OUTPUT} → wenjie-progress.html")

    # ===== 生成 6 年规划页 =====
    print(f"\n🗺 生成 6 年规划...")
    build_plan_page()

    # ===== 生成进度 + CCA 页 =====
    print(f"\n📈 生成进度 + CCA...")
    build_progress_page(daily_perf)

    # ===== 生成英雄学院 =====
    print(f"\n🦸 生成英雄学院...")
    build_academy(daily_data, daily_perf, default_date)

    return True


def build_dashboard(daily_perf):
    """生成仪表盘 HTML"""
    if not DASHBOARD_TEMPLATE.exists():
        print(f"⚠️  仪表盘模板不存在: {DASHBOARD_TEMPLATE}")
        return

    today_str = datetime.now().strftime('%Y-%m-%d')

    # KPI: 累计学习天数
    total_days = sum(1 for d in daily_perf.values() if d.get('completed', True))
    if daily_perf:
        first_date = min(daily_perf.keys())
        last_date = max(daily_perf.keys())
        week_range = f'{first_date[5:]} ~ {last_date[5:]}'
    else:
        week_range = '—'

    # KPI: 待复习错题 + 已掌握
    all_mistakes = []
    for md_file in WIKI_MISTAKES.rglob('*.md'):
        if md_file.name == 'index.md':
            continue
        fm, _ = load_mistake_frontmatter(md_file)
        if fm:
            all_mistakes.append(fm)

    due_count = sum(1 for m in all_mistakes if m.get('status') == 'pending')
    mastered_count = sum(1 for m in all_mistakes if m.get('status') == 'mastered')
    total_mistakes = len(all_mistakes)
    mastered_pct = f'{mastered_count/total_mistakes*100:.0f}% 掌握率' if total_mistakes > 0 else '—'

    # KPI: 本周完成度
    week_dates = [d for d in daily_perf.keys() if d <= today_str]
    week_completed = sum(1 for d in week_dates if daily_perf[d].get('completed', True))
    week_completion = int(week_completed / len(week_dates) * 100) if week_dates else 0

    # 珠算曲线
    math_curve_html, math_labels = render_curve(daily_perf, 'math_correct', 'math_total', '珠算')

    # 心算曲线
    mental_curve_html, mental_labels = render_curve(daily_perf, 'mental_correct', 'mental_total', '心算')

    # 错题表
    mistake_table = render_mistake_table(all_mistakes)

    # 读取模板并替换
    template = DASHBOARD_TEMPLATE.read_text(encoding='utf-8')
    html = template
    html = html.replace('__TOTAL_DAYS__', str(total_days))
    html = html.replace('__WEEK_RANGE__', week_range)
    html = html.replace('__DUE_COUNT__', str(due_count))
    html = html.replace('__DUE_TREND__', 'down' if due_count > 0 else 'flat')
    html = html.replace('__DUE_TREND_TEXT__', f'{due_count} 道待复习' if due_count > 0 else '全部复习完 ✅')
    html = html.replace('__MASTERED_COUNT__', str(mastered_count))
    html = html.replace('__MASTERED_PCT__', mastered_pct)
    html = html.replace('__WEEK_COMPLETION__', str(week_completion))
    html = html.replace('__WEEK_TREND_TEXT__', f'已 {week_completed}/{len(week_dates)} 天' if week_dates else '—')
    html = html.replace('__MATH_CURVE_HTML__', math_curve_html)
    html = html.replace('__MATH_LABELS__', math_labels)
    html = html.replace('__MENTAL_CURVE_HTML__', mental_curve_html)
    html = html.replace('__MENTAL_LABELS__', mental_labels)
    html = html.replace('__MISTAKE_TABLE_HTML__', mistake_table)
    html = html.replace('__BUILD_TIME__', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    DASHBOARD_OUTPUT.write_text(html, encoding='utf-8')
    print(f"  ✅ 生成 {DASHBOARD_OUTPUT}")
    print(f"  - 待复习: {due_count} · 已掌握: {mastered_count}")
    print(f"  - 本周完成度: {week_completion}%")


def render_curve(daily_perf, correct_key, total_key, label):
    """渲染简单曲线（柱状图）"""
    dates = sorted(daily_perf.keys())
    today_str = datetime.now().strftime('%Y-%m-%d')

    bars = ''
    labels = ''
    for date in dates:
        perf = daily_perf[date]
        correct = perf.get(correct_key)
        total = perf.get(total_key)

        if correct is None or total is None or total == 0:
            bars += '<div class="spark-bar zero" style="height: 10%;" title="' + date + ' 无数据"></div>'
        else:
            pct = correct / total * 100
            height = max(10, pct)
            future = ' future' if date > today_str else ''
            bars += f'<div class="spark-bar{future}" style="height: {height:.0f}%;" title="{date} · {correct}/{total} ({pct:.0f}%)"></div>'

        labels += f'<div class="spark-label">{date[5:]}</div>'

    if all(daily_perf[d].get(correct_key) is None for d in dates):
        bars = '<div class="empty-state" style="grid-column: 1 / -1;">还没数据 · 多做几天就有曲线</div>'
        labels = ''

    return f'<div class="spark-line">{bars}</div>', labels


def render_mistake_table(mistakes):
    """渲染错题表"""
    if not mistakes:
        return '<div class="empty-state">还没错题 · 做得太好了！</div>'

    rows = ''
    for m in mistakes[:20]:  # 最多 20 条
        status_badge = '<span class="badge badge-pending">待复习</span>' if m.get('status') == 'pending' else '<span class="badge badge-mastered">已掌握</span>'
        rows += f'''<tr>
            <td>{status_badge}</td>
            <td><strong>{m.get('id', '?')}</strong></td>
            <td>{m.get('subject', '?')}</td>
            <td>{m.get('type', '?')}</td>
            <td><code>{m.get('problem', '?')}</code></td>
            <td>{m.get('date', '?')}</td>
        </tr>'''

    return f'''<table class="mistake-table">
        <thead>
            <tr>
                <th>状态</th>
                <th>ID</th>
                <th>科目</th>
                <th>错因</th>
                <th>题面</th>
                <th>发现日</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>'''


def build_academy(daily_data, daily_perf, today_date):
    """生成奥特曼英雄学院页面"""
    if not ACADEMY_TEMPLATE.exists():
        print(f"⚠️  英雄学院模板不存在: {ACADEMY_TEMPLATE}")
        return

    template = ACADEMY_TEMPLATE.read_text(encoding='utf-8')

    # 计算统计数据
    total_days = sum(1 for d in daily_perf.values() if d.get('completed', True))
    xp = total_days * 90  # 每个完成日 90 XP
    monsters_defeated = sum(1 for m in _get_all_mistakes() if m.get('status') == 'mastered')
    streak = 1  # TODO: 计算 streak

    # 计算大 Boss 击败（基于 subject 进度 > 80% 算打败）
    math_p_v = _subject_progress(daily_perf, 'math_correct', 'math_total')
    bosses_defeated = 0
    if math_p_v >= 0.8:
        bosses_defeated += 1  # 加法怪兽

    # 钢琴 Trinity 通过 = 钢琴 Boss 打败
    if any(m.get('status') == 'mastered' for m in _get_all_mistakes() if m.get('subject') == 'piano'):
        bosses_defeated += 1

    # 计算特殊奖杯
    trophies = 0
    if streak >= 7:
        trophies += 1  # 周冠军
    if monsters_defeated >= 50:
        trophies += 1  # 怪兽猎人
    if bosses_defeated >= 1:
        trophies += 1  # Boss 杀手

    level = max(1, total_days // 2 + 1)
    xp_max = level * 100

    # 进度百分比（每个 subject）
    math_p = int(_subject_progress(daily_perf, 'math_correct', 'math_total') * 100)
    english_p = 0  # TODO: 跟踪 English 进度
    chinese_p = 0
    piano_p = 0
    reading_p = 0

    # 渲染今日怪兽任务
    today_day = next((d for d in daily_data if d['date'] == today_date), None)
    missions_html = render_monster_missions(today_day, daily_perf, today_date)

    # 渲染娃版今日任务（基于 daily plan 时间表）
    todays_tasks_html = render_todays_tasks_for_kid(today_date, daily_perf)

    # 渲染本周计划（七日视图 · 当周 7 天）
    week_plan_html = render_week_plan_for_kid(today_date)

    # 替换占位符
    html = template
    html = html.replace('__LEVEL__', str(level))
    html = html.replace('__XP__', str(xp))
    html = html.replace('__XP_MAX__', str(xp_max))
    html = html.replace('__POWER__', str(min(100, total_days * 10)))
    html = html.replace('__INTEL__', str(min(100, xp // 5)))
    html = html.replace('__SPEED__', str(min(100, 50 + total_days * 5)))
    html = html.replace('__MISSIONS_HTML__', missions_html)
    html = html.replace('__TODAYS_TASKS_HTML__', todays_tasks_html)
    html = html.replace('__WEEK_PLAN_HTML__', week_plan_html)
    html = html.replace('__MISSION_COUNT__', str(missions_html.count('mission-card')))
    html = html.replace('__MATH_PROGRESS__', f'{math_p}% 击败')
    html = html.replace('__ENGLISH_PROGRESS__', f'{english_p}% 击败')
    html = html.replace('__CHINESE_PROGRESS__', f'{chinese_p}% 击败')
    html = html.replace('__PIANO_PROGRESS__', f'{piano_p}% 击败')
    html = html.replace('__READING_PROGRESS__', f'{reading_p}% 击败')
    # 视觉进度条（娃版用）
    html = html.replace('__MATH_PCT__', str(math_p))
    html = html.replace('__ENGLISH_PCT__', str(english_p))
    html = html.replace('__CHINESE_PCT__', str(chinese_p))
    html = html.replace('__PIANO_PCT__', str(piano_p))
    html = html.replace('__READING_PCT__', str(reading_p))
    html = html.replace('__MONSTERS_DEFEATED__', str(monsters_defeated))
    html = html.replace('__BOSSES_DEFEATED__', str(bosses_defeated))
    html = html.replace('__TROPHIES__', str(trophies))
    html = html.replace('__STREAK__', str(streak))

    # 战斗回放 defeat 标记（基于 daily_perf 各科完成度）
    math_done = daily_perf.get(today_date, {}).get('math_total', 0) > 0 and daily_perf.get(today_date, {}).get('math_correct', 0) >= daily_perf.get(today_date, {}).get('math_total', 0) * 0.7
    html = html.replace('__MATH_DEFEATED__', '1' if math_done else '0')
    html = html.replace('__ENGLISH_DEFEATED__', '0')  # 暂无数据
    html = html.replace('__CHINESE_DEFEATED__', '0')
    html = html.replace('__PIANO_DEFEATED__', '1' if daily_perf.get(today_date, {}).get('piano_done', False) else '0')
    html = html.replace('__READING_DEFEATED__', '0')

    html = html.replace('__BUILD_TIME__', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    ACADEMY_OUTPUT.write_text(html, encoding='utf-8')
    print(f"  ✅ 生成 {ACADEMY_OUTPUT}")
    print(f"  - 等级 {level} · XP {xp}/{xp_max}")
    print(f"  - 怪兽任务 {missions_html.count('mission-card')} 个")


def render_monster_missions(day_data, daily_perf, today_date):
    """渲染怪兽任务卡"""
    if not day_data:
        return '<div class="mission-card"><div class="mission-body">今天没有任务哦！休息一下 💤</div></div>'

    monsters = []
    perf = daily_perf.get(today_date, {})

    # 珠算怪兽
    if perf.get('math_correct') is not None:
        monsters.append({
            'emoji': '🦖',
            'name': '数学怪兽·进位加法',
            'subject': 'math',
            'tag': 'MATH',
            'hp': f'HP {perf["math_correct"]}/{perf["math_total"]}',
            'desc': f'做 {perf["math_total"]} 道进位加法 · 已击败 {perf["math_total"] - perf["math_correct"]} 个怪兽',
            'rewards': ['+50 XP', '⚡闪电拳', '💎 宝石']
        })

    # 心算怪兽
    if perf.get('mental_correct') is not None:
        monsters.append({
            'emoji': '👾',
            'name': '心算怪兽·快速计算',
            'subject': 'math',
            'tag': 'MATH',
            'hp': f'HP {perf["mental_correct"]}/{perf["mental_total"]}',
            'desc': f'3 min 心算挑战 · 已击败 {perf["mental_total"] - perf["mental_correct"]} 个怪兽',
            'rewards': ['+30 XP', '🛡️防护盾']
        })

    # Phonics 怪兽
    for sec in day_data.get('sections', []):
        if 'Phonics' in sec['heading'] or 'phonics' in sec['heading'].lower():
            monsters.append({
                'emoji': '🦕',
                'name': '英文怪兽·Long E 怪兽',
                'subject': 'english',
                'tag': 'EN',
                'hp': 'HP ???/10',
                'desc': 'KAK Vowel Sounds · Long E: ee, ea',
                'rewards': ['+30 XP', '📚 词汇书']
            })
            break

    # 主练习册怪兽
    for sec in day_data.get('sections', []):
        if '主练习册' in sec['heading'] or 'Intensive Maths' in sec['heading']:
            monsters.append({
                'emoji': '🐲',
                'name': '练习册怪兽·4-6 页',
                'subject': 'math',
                'tag': 'MATH',
                'hp': 'HP 4-6 页',
                'desc': 'Intensive Maths Drills P1 · 加减计算 + 英文应用题',
                'rewards': ['+40 XP', '🏆 奖杯']
            })
            break

    # 副练习册怪兽
    for sec in day_data.get('sections', []):
        if '副练习册' in sec['heading'] or '快乐练习' in sec['heading']:
            monsters.append({
                'emoji': '👹',
                'name': '中文怪兽·识字 + 描红',
                'subject': 'chinese',
                'tag': '中文',
                'hp': 'HP 5+1 字',
                'desc': '快乐练习2.0 · 识字 L5 抽测 + 1 个新字描红',
                'rewards': ['+40 XP', '🖌️ 毛笔']
            })
            break

    # 钢琴怪兽
    monsters.append({
        'emoji': '🎹',
        'name': '钢琴怪兽·节拍挑战',
        'subject': 'piano',
        'tag': 'PIANO',
        'hp': 'HP 20 min',
        'desc': '17:15-17:35 · 钢琴练习（妈妈陪或独立）',
        'rewards': ['+25 XP', '🎵 音符']
    })

    # 如果没怪兽，加占位
    if not monsters:
        return '<div class="mission-card"><div class="mission-body">🎮 今天没有怪兽！休息日或自由日 💤</div></div>'

    # 渲染
    html = ''
    for m in monsters:
        rewards_html = ''.join([f'<span class="reward-item">{r}</span>' for r in m['rewards']])
        html += f'''<div class="mission-card">
            <div class="mission-head">
                <div class="monster-emoji">{m['emoji']}</div>
                <div class="monster-info">
                    <h3 class="monster-name">{m['name']}</h3>
                    <span class="monster-tag tag-{m['subject']}">{m['tag']}</span>
                    <span class="monster-hp">{m['hp']}</span>
                </div>
            </div>
            <div class="mission-body">{m['desc']}</div>
            <div class="mission-reward">🎁 击败奖励：{rewards_html}</div>
        </div>'''

    return html


def render_todays_tasks_for_kid(today_date, daily_perf):
    """渲染娃版今日任务（来自 wiki/plans/daily/今日.md · 只取学习时段）"""
    import re

    def clean_md(s):
        """清除 markdown 格式符号"""
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)  # bold
        s = re.sub(r'~~([^~]+)~~', r'', s)  # strikethrough（删除）
        s = re.sub(r'__([^_]+)__', r'\1', s)  # underline
        s = re.sub(r'\*([^*]+)\*', r'\1', s)  # italic
        return s.strip()

    daily_md = BASE / 'wiki' / 'plans' / 'daily' / f'{today_date}.md'
    if not daily_md.exists():
        return '<div class="todays-task-card"><div class="todays-task-name">今天无任务 ✨</div></div>'

    md_text = daily_md.read_text(encoding='utf-8')

    tasks = []
    in_first_table = False
    table_ended = False

    for line in md_text.split('\n'):
        # 找到第一个表格（包含 '| 时段 |' 头）
        if not in_first_table:
            if '|' in line and '时段' in line and '任务' in line:
                in_first_table = True
            continue

        # 已经离开了第一个表格就停止
        if not (line.startswith('|') and '|' in line):
            if in_first_table:
                # 离开表格 → 停止
                break
            continue
        if '---' in line:
            continue

        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) < 2:
            continue

        time_slot = clean_md(cells[0])
        task = clean_md(cells[1])

        # 跳过空任务
        if not task or task == '—':
            continue
        # 跳过非学习活动
        skip_keywords = ['完全自由', '玩耍', '晚饭', '洗澡', '睡觉', '户外', '项目日']
        if any(k in task for k in skip_keywords):
            continue
        # 跳过已被删除的（~~）
        if '~~' in line:
            continue

        # 判断任务类型
        emoji = '📝'
        reward = '+10 XP'
        if '钢琴' in task:
            emoji = '🎹'
            reward = '+15 XP'
        elif '汉字' in task or '写字' in task:
            emoji = '✍️'
            reward = '+5 XP'
        elif '珠算' in task or '心算' in task or '数学' in task or 'Maths' in task:
            emoji = '🔢'
            reward = '+15 XP'
        elif '英文' in task or 'English' in task or 'Phonics' in task or 'KAK' in task:
            emoji = '📚'
            reward = '+10 XP'
        elif '中文' in task or '练习' in task or '识字' in task:
            emoji = '📗'
            reward = '+10 XP'
        elif '阅读' in task:
            emoji = '📖'
            reward = '+10 XP'

        # 提取简短任务名（移除括号内容）
        short_task = re.sub(r'[（(][^）)]*[）)]', '', task).strip()
        # 截短
        if len(short_task) > 8:
            short_task = short_task[:8]

        tasks.append({
            'time': time_slot,
            'name': short_task,
            'emoji': emoji,
            'reward': reward
        })

    if not tasks:
        return '<div class="todays-task-card"><div class="todays-task-name">今天无学习任务 🎉</div></div>'

    cards = ''
    for i, t in enumerate(tasks[:6]):
        cards += f'''
        <div class="todays-task-card" data-task-id="{today_date}-{i}" data-task-index="{i}">
          <div class="todays-task-emoji">{t['emoji']}</div>
          <div class="todays-task-name">{t['name']}</div>
          <div class="todays-task-time">{t['time']}</div>
          <div class="todays-task-reward">{t['reward']}</div>
          <button class="task-done-btn" data-task-id="{today_date}-{i}">⚔️ 打败它</button>
        </div>'''

    defeat_btn = f'''
    <div class="defeat-monster-btn-wrapper" id="defeat-btn-wrapper" style="display:none;">
      <button class="defeat-monster-btn" id="defeat-monster-btn">
        🎉 打败今天的怪兽！
      </button>
      <p style="text-align:center; color: rgba(135, 206, 235, 0.9); font-size: 11px; margin-top: 8px;">
        点击看文杰奥特曼打败怪兽 ⚡
      </p>
    </div>'''

    return f'<div class="todays-tasks-grid">{cards}</div>{defeat_btn}'


def render_week_plan_for_kid(today_date):
    """渲染娃版本周计划（七日视图 · 当周 7 天）"""
    import re
    from datetime import datetime, timedelta

    def clean_md(s):
        s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
        s = re.sub(r'~~([^~]+)~~', r'', s)
        s = re.sub(r'__([^_]+)__', r'\1', s)
        return s.strip()

    # 找出本周的 7 天（周一到周日）
    today = datetime.strptime(today_date, '%Y-%m-%d').date()
    # 智能选择：周一-周三显示本周；周四-周日显示下周（即将到来的周）
    if today.weekday() >= 3:  # 周四-周日
        days_to_next_mon = 7 - today.weekday()
        monday = today + timedelta(days=days_to_next_mon)
    else:
        monday = today - timedelta(days=today.weekday())
    week_dates = [(monday + timedelta(days=i)) for i in range(7)]

    # 每天的类型 + 主要任务
    day_type_emoji = {
        '周一': ('🟢', '常规'),
        '周二': ('🟡', '半休'),
        '周三': ('🟡', '半休'),
        '周四': ('🟢', '轻量'),
        '周五': ('🟢', '常规'),
        '周六': ('🟠', '项目'),
        '周日': ('🟠', '复盘'),
    }

    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    cards = ''

    for date_obj in week_dates:
        date_str = date_obj.strftime('%Y-%m-%d')
        weekday = weekday_names[date_obj.weekday()]
        emoji, day_type = day_type_emoji[weekday]

        # 读取当天的计划
        daily_md = BASE / 'wiki' / 'plans' / 'daily' / f'{date_str}.md'
        tasks_short = []

        if daily_md.exists():
            md_text = daily_md.read_text(encoding='utf-8')

            # 找第一个表格 + 提取关键任务
            in_first_table = False
            for line in md_text.split('\n'):
                if not in_first_table:
                    if '|' in line and '时段' in line and '任务' in line:
                        in_first_table = True
                    continue
                if not (line.startswith('|') and '|' in line):
                    if in_first_table:
                        break
                    continue
                if '---' in line:
                    continue

                cells = [c.strip() for c in line.strip('|').split('|')]
                if len(cells) < 2:
                    continue

                task = clean_md(cells[1])
                if not task or task == '—':
                    continue
                if '~~' in line:
                    continue
                skip_kw = ['完全自由', '玩耍', '晚饭', '洗澡', '睡觉', '户外', '项目日活动']
                if any(k in task for k in skip_kw):
                    continue

                # 选择 emoji
                task_emoji = '📝'
                if '考级' in task:
                    task_emoji = '🎯'
                elif '钢琴' in task:
                    task_emoji = '🎹'
                elif '汉字' in task or '写字' in task:
                    task_emoji = '✍️'
                elif '珠算' in task or '心算' in task or '数学' in task:
                    task_emoji = '🔢'
                elif '英文' in task or 'English' in task or 'Phonics' in task:
                    task_emoji = '📚'
                elif '阅读' in task or '读' in task:
                    task_emoji = '📖'
                elif 'Wiki' in task or '复盘' in task:
                    task_emoji = '📋'

                short = re.sub(r'[（(][^）)]*[）)]', '', task).strip()[:6]
                task_entry = f'{task_emoji} {short}'

                # 跳过"写汉字"（每天 8:15 的微习惯 · 不在周视图显示）
                if '写汉字' in task or task.strip().startswith('写汉字'):
                    continue

                tasks_short.append(task_entry)

                if len(tasks_short) >= 4:
                    break

        if not tasks_short:
            tasks_short = ['—']

        # 状态 class
        is_today = (date_str == today_date)
        is_past = (date_obj < today)
        classes = 'week-day-card'
        if is_today:
            classes += ' today'
        elif is_past:
            classes += ' past'

        badge = '<div class="week-day-badge">TODAY</div>' if is_today else ''
        tasks_html = '<br>'.join(tasks_short)

        cards += f'''
        <div class="{classes}" data-date="{date_str}">
          <div class="week-day-name">{weekday}</div>
          <div class="week-day-emoji">{emoji}</div>
          <div class="week-day-tasks">{tasks_html}</div>
          <div class="week-day-date">{date_str[5:]}</div>
          {badge}
        </div>'''

    return f'<div class="week-plan-grid">{cards}</div>'


def _get_all_mistakes():
    """获取所有错题"""
    all_mistakes = []
    for md_file in WIKI_MISTAKES.rglob('*.md'):
        if md_file.name == 'index.md':
            continue
        fm, _ = load_mistake_frontmatter(md_file)
        if fm:
            all_mistakes.append(fm)
    return all_mistakes


def _subject_progress(daily_perf, correct_key, total_key):
    """计算某科的整体正确率"""
    correct_sum = 0
    total_sum = 0
    for perf in daily_perf.values():
        c = perf.get(correct_key)
        t = perf.get(total_key)
        if c is not None and t:
            correct_sum += c
            total_sum += t
    return correct_sum / total_sum if total_sum > 0 else 0


def build_plan_page():
    """生成 6 年规划页（合并 overview + readiness）"""
    if not PLAN_TEMPLATE.exists():
        print(f"⚠️  模板不存在: {PLAN_TEMPLATE}")
        return

    template = PLAN_TEMPLATE.read_text(encoding='utf-8')

    # 6 年时间轴
    timeline_html = render_timeline()

    # 6 年目标
    goals_html = load_and_render_wiki('wiki/profile/goals.md')

    # 12 维度评分
    dimensions_html = render_dimensions()

    # 资源清单
    resources_html = render_resources()

    # DSA
    dsa_html = load_and_render_wiki('wiki/dsa/requirements.md')

    html = template
    html = html.replace('__TIMELINE_HTML__', timeline_html)
    html = html.replace('__GOALS_HTML__', goals_html)
    html = html.replace('__DIMENSIONS_HTML__', dimensions_html)
    html = html.replace('__RESOURCES_HTML__', resources_html)
    html = html.replace('__DSA_HTML__', dsa_html)
    html = html.replace('__BUILD_TIME__', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    PLAN_OUTPUT.write_text(html, encoding='utf-8')
    print(f"  ✅ 生成 {PLAN_OUTPUT}")


def render_timeline():
    """渲染 6 年时间轴"""
    today_str = datetime.now().strftime('%Y-%m-%d')
    grades = [
        ('K2', '2026', '现在'),
        ('P1', '2027', '小学'),
        ('P2', '2028', ''),
        ('P3', '2029', 'Trinity 4'),
        ('P4', '2030', 'SYF'),
        ('P5', '2031', 'DSA 准备'),
    ]
    items = ''
    for grade, year, milestone in grades:
        cls = 'current' if grade == 'K2' else ''
        items += f'''<div class="timeline-item {cls}">
            <div class="grade">{grade}</div>
            <div class="year">{year}</div>
            <div style="font-size: 9px; color: var(--primary); margin-top: 2px;">{milestone}</div>
        </div>'''
    return f'<div class="timeline">{items}</div>'


def load_and_render_wiki(path):
    """加载并渲染 Wiki markdown"""
    file_path = BASE / path
    if not file_path.exists():
        return f'<p style="color: var(--muted);">⚠️ 文件不存在：{path}</p>'

    md_text = file_path.read_text(encoding='utf-8')
    parsed = parse_md_sections(md_text)

    html = ''
    if parsed['title']:
        html += f'<h1>{parsed["title"]}</h1>'

    for sec in parsed['sections']:
        sec_html = md_to_html('\n'.join(sec['body']))
        html += f'<h2>{sec["heading"]}</h2>{sec_html}'

    return html


def render_dimensions():
    """渲染 12 维度评分（暂时硬编码默认值）"""
    dims = [
        ('🗣 英语听说', 4, 'ok'),
        ('📖 英语阅读', 3, 'warn'),
        ('✍️ 英语书写', 3, 'warn'),
        ('🔢 数学计算', 4, 'ok'),
        ('🧩 数学应用', 3, 'warn'),
        ('📐 数学思维', 3, 'warn'),
        ('🀄 中文听说', 5, 'strong'),
        ('📜 中文阅读', 4, 'ok'),
        ('🖌 汉字书写', 3, 'warn'),
        ('🎹 音乐/钢琴', 4, 'ok'),
        ('🏃 运动体能', 4, 'ok'),
        ('👥 社交情感', 5, 'strong'),
    ]
    cards = ''
    for name, score, tier in dims:
        cards += f'''<div class="dim-card" data-tier="{tier}">
            <div class="name">{name}</div>
            <div class="score">
                <div class="score-num">{score}</div>
                <div class="score-bar"><div class="score-fill" style="width: {score*20}%"></div></div>
            </div>
        </div>'''
    return f'<div class="dim-grid">{cards}</div>'


def render_resources():
    """渲染资源清单"""
    items = [
        ('📚 Intensive Maths Drills P1', '已购 · Issac'),
        ('📚 One-stop English P1', '已购 · CASCO'),
        ('📚 快乐练习 2.0', '已购 · 识字 + 拼音'),
        ('🎵 KAK Vowel Sounds', '已购 · Grade 2'),
        ('📖 牛津树 Oxford Reading Tree', '已购 · Level 1-3'),
        ('🧮 算盘 + 心算卡', '已购'),
        ('🎹 钢琴课', '进行中 · Trinity'),
    ]
    cards = ''
    for name, status in items:
        cards += f'''<div class="resource-card">
            <div class="name">{name}</div>
            <div class="status">{status}</div>
        </div>'''
    return f'<div class="resource-grid">{cards}</div>'


def build_progress_page(daily_perf):
    """生成进度 + CCA 页（合并 dashboard + cca-tracker）"""
    if not PROGRESS_TEMPLATE.exists():
        print(f"⚠️  模板不存在: {PROGRESS_TEMPLATE}")
        return

    template = PROGRESS_TEMPLATE.read_text(encoding='utf-8')
    today_str = datetime.now().strftime('%Y-%m-%d')

    # KPI 数据
    total_days = sum(1 for d in daily_perf.values() if d.get('completed', True))
    if daily_perf:
        first_date = min(daily_perf.keys())
        last_date = max(daily_perf.keys())
        week_range = f'{first_date[5:]} ~ {last_date[5:]}'
    else:
        week_range = '—'

    all_mistakes = _get_all_mistakes()
    due_count = sum(1 for m in all_mistakes if m.get('status') == 'pending')
    mastered_count = sum(1 for m in all_mistakes if m.get('status') == 'mastered')
    mastered_pct = f'{mastered_count}/{len(all_mistakes)} · {mastered_count/len(all_mistakes)*100:.0f}% 掌握率' if all_mistakes else '—'

    week_dates = [d for d in daily_perf.keys() if d <= today_str]
    week_completed = sum(1 for d in week_dates if daily_perf[d].get('completed', True))
    week_completion = int(week_completed / len(week_dates) * 100) if week_dates else 0

    # 曲线
    math_curve, math_labels = render_curve(daily_perf, 'math_correct', 'math_total', '珠算')
    mental_curve, mental_labels = render_curve(daily_perf, 'mental_correct', 'mental_total', '心算')

    # 错题表
    mistake_table = render_mistake_table(all_mistakes)

    # CCA 钢琴里程碑
    piano_milestones = render_piano_milestones()

    # CCA 钢琴曲库
    piano_repertoire = render_piano_repertoire()

    # CCA 游泳里程碑
    swimming_milestones, swimming_ability = render_swimming_milestones()

    html = template
    html = html.replace('__TOTAL_DAYS__', str(total_days))
    html = html.replace('__WEEK_RANGE__', week_range)
    html = html.replace('__DUE_COUNT__', str(due_count))
    html = html.replace('__DUE_TREND_CLASS__', 'down' if due_count > 0 else 'flat')
    html = html.replace('__DUE_TREND_TEXT__', f'{due_count} 道待复习' if due_count > 0 else '全部复习完 ✅')
    html = html.replace('__MASTERED_COUNT__', str(mastered_count))
    html = html.replace('__MASTERED_PCT__', mastered_pct)
    html = html.replace('__WEEK_COMPLETION__', str(week_completion))
    html = html.replace('__WEEK_TREND_TEXT__', f'已 {week_completed}/{len(week_dates)} 天' if week_dates else '—')
    html = html.replace('__MATH_CURVE_HTML__', math_curve)
    html = html.replace('__MATH_LABELS__', math_labels)
    html = html.replace('__MENTAL_CURVE_HTML__', mental_curve)
    html = html.replace('__MENTAL_LABELS__', mental_labels)
    html = html.replace('__MISTAKE_TABLE_HTML__', mistake_table)
    html = html.replace('__PIANO_MILESTONES_HTML__', piano_milestones)
    html = html.replace('__PIANO_REPERTOIRE_HTML__', piano_repertoire)
    html = html.replace('__SWIMMING_MILESTONES_HTML__', swimming_milestones)
    html = html.replace('__SWIMMING_ABILITY_HTML__', swimming_ability)
    html = html.replace('__BUILD_TIME__', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    PROGRESS_OUTPUT.write_text(html, encoding='utf-8')
    print(f"  ✅ 生成 {PROGRESS_OUTPUT}")


def render_piano_milestones():
    """渲染钢琴里程碑"""
    milestones = [
        ('K2 末', 'Trinity 1', 'done', '已考完 Distinct'),
        ('P1', '⏭ Trinity 2 跳过', 'done', '直跳 Trinity 3'),
        ('P2 末', 'Trinity 3 + SPAF 1', 'active', '2025-09 SPAF Gold'),
        ('P3 末', 'Trinity 4 + SPAF 2', 'future', '2029'),
        ('P4 末', 'SYF 校内选拔 + SPAF 3', 'future', '2030'),
        ('P5 末', 'SYF 主奏 + Trinity 6', 'future', '2031'),
        ('P6 末', 'Trinity 7 + DSA', 'future', '2032'),
    ]
    rows = ''
    for grade, milestone, status, note in milestones:
        status_class = f'status-{status}'
        rows += f'''<div class="cca-row">
            <div class="grade">{grade}</div>
            <div class="milestone">{milestone} · <small>{note}</small></div>
            <div class="status {status_class}">
                {'✅' if status == 'done' else '🔄' if status == 'active' else '⏳'}
            </div>
        </div>'''
    return f'<div class="cca-timeline">{rows}</div>'


def render_piano_repertoire():
    """渲染钢琴曲库（从 wiki/cca/piano.md 读取）"""
    piano_md = BASE / 'wiki' / 'cca' / 'piano.md'
    if not piano_md.exists():
        return '<div class="empty-state">曲库数据未找到</div>'

    md_text = piano_md.read_text(encoding='utf-8')
    sections = parse_md_sections(md_text)

    # 找曲库 section
    repertoire_html = ''
    in_repertoire = False
    for sec in sections['sections']:
        if '曲库' in sec['heading']:
            in_repertoire = True
            # 找子 sections
            body = '\n'.join(sec['body'])
            sub_sections = re.split(r'### (.+)', body)
            # sub_sections[0] = intro, then alternating title + content
            i = 1
            current_title = ''
            rows = ''
            while i < len(sub_sections):
                current_title = sub_sections[i].strip()
                content = sub_sections[i + 1] if i + 1 < len(sub_sections) else ''
                i += 2

                # 提取列表项
                pieces = re.findall(r'[-*]\s*(.+?)(?:\n|$)', content)
                for piece in pieces:
                    piece = piece.strip()
                    # 判断级别和状态
                    if 'Trinity 1' in current_title:
                        level = 'Trinity 1'
                        badge = '<span class="badge badge-done">✅ 已通过</span>'
                    elif 'Trinity 3' in current_title:
                        level = 'Trinity 3'
                        badge = '<span class="badge badge-active">🔄 练习中</span>'
                    else:
                        level = current_title.replace('### ', '').strip()
                        badge = ''

                    rows += f'<tr><td>{piece}</td><td>{level}</td><td>{badge}</td></tr>'

            if rows:
                repertoire_html = f'''<table class="data-table">
                    <thead>
                        <tr><th>曲目</th><th>级别</th><th>状态</th></tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>'''
            break

    if not repertoire_html:
        return '<div class="empty-state">曲库数据待补</div>'

    return repertoire_html


def render_swimming_milestones():
    """渲染游泳里程碑（从 wiki/subjects/swimming/milestones.md 读取）"""
    milestones_md = BASE / 'wiki' / 'subjects' / 'swimming' / 'milestones.md'
    if not milestones_md.exists():
        return '<div class="empty-state">游泳里程碑数据未找到</div>', ''

    md_text = milestones_md.read_text(encoding='utf-8')

    # 解析 M1-M6 里程碑
    # 匹配 "## M1 · ...\n- 详情"
    milestone_blocks = re.findall(r'## (M\d+) · ([^\n]+)\n((?:-[^\n]+\n?)+)', md_text)
    # 也匹配没有 bullets 的（以防格式不同）
    if not milestone_blocks:
        milestone_blocks = re.findall(r'## (M\d+) · ([^\n]+)\n([^#]+?)(?=\n##|\Z)', md_text, re.DOTALL)

    # 当前时间判断状态（基于 P1=2027 等时间）
    current_year = 2026
    p_grades = {
        'M1': ('P1', 2027),
        'M2': ('P2', 2028),
        'M3': ('P3', 2029),
        'M4': ('P4', 2030),
        'M5': ('P5', 2031),
        'M6': ('P6', 2032),
    }

    rows = ''
    for m_id, m_title, m_body in milestone_blocks:
        # 提取 bullets
        bullets = re.findall(r'-\s*(.+)', m_body)
        bullets_html = '<ul style="margin: 4px 0; padding-left: 20px; font-size: 12px; color: var(--ink-2);">' + \
                       ''.join(f'<li>{b.strip()}</li>' for b in bullets) + '</ul>'

        # 状态判断
        p_grade, target_year = p_grades.get(m_id, ('?', 0))
        if target_year <= current_year:
            status_class = 'status-done'
            status_icon = '✅'
        elif target_year == current_year + 1:
            status_class = 'status-active'
            status_icon = '🔄'
        else:
            status_class = 'status-future'
            status_icon = '⏳'

        rows += f'''<div class="cca-row">
            <div class="grade">{m_id}<br><small>{p_grade}</small></div>
            <div class="milestone">
                <strong>{m_title.strip()}</strong>
                {bullets_html}
            </div>
            <div class="status {status_class}">
                {status_icon}<br><small>{target_year}</small>
            </div>
        </div>'''

    milestones_html = f'''<div class="cca-timeline">{rows}</div>'''

    # 游泳当前能力（从 mastery.md 读取）
    mastery_md = BASE / 'wiki' / 'subjects' / 'swimming' / 'mastery.md'
    ability_html = ''
    if mastery_md.exists():
        mastery_text = mastery_md.read_text(encoding='utf-8')
        # 找"## 当前能力"section
        ability_match = re.search(r'## 当前能力\s*\n((?:\|[^\n]+\n?)+)', mastery_text)
        if ability_match:
            table_text = ability_match.group(1).strip()
            lines = table_text.split('\n')
            if len(lines) >= 3:
                # 解析 markdown 表格
                header = [c.strip() for c in lines[0].strip('|').split('|')]
                rows_data = []
                for line in lines[2:]:  # skip separator
                    cells = [c.strip() for c in line.strip('|').split('|')]
                    rows_data.append(cells)

                table_rows = ''.join(
                    '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>'
                    for r in rows_data
                )

                ability_html = f'''<table class="data-table">
                    <thead>
                        <tr>{''.join(f'<th>{h}</th>' for h in header)}</tr>
                    </thead>
                    <tbody>{table_rows}</tbody>
                </table>'''

    if not ability_html:
        ability_html = '''<div class="empty-state">
            <table class="data-table">
                <tr><th>泳姿</th><th>进度</th><th>备注</th></tr>
                <tr><td>自由泳</td><td>50m ≈ 1:10</td><td>主攻项目</td></tr>
                <tr><td>仰泳</td><td>50m ≈ 1:10</td><td>主攻项目</td></tr>
                <tr><td>Board Kicking</td><td>业余银牌</td><td>海豚腿 / 打水</td></tr>
                <tr><td>蛙泳</td><td>基础</td><td>待加强</td></tr>
                <tr><td>蝶泳</td><td>入门</td><td>待加强</td></tr>
            </table>
        </div>'''

    return milestones_html, ability_html


if __name__ == '__main__':
    build()