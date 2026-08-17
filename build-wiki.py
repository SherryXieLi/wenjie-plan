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
TEMPLATE = BASE / 'wenjie-daily-plan.template.html'
DASHBOARD_OUTPUT = BASE / 'wenjie-progress-dashboard.html'
DASHBOARD_TEMPLATE = BASE / 'wenjie-progress-dashboard.template.html'

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


if __name__ == '__main__':
    build()