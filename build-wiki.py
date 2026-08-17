#!/usr/bin/env python3
"""
build-wiki.py · Wiki → HTML 构建脚本
读取 wiki/plans/daily/*.md，生成 wenjie-daily-plan.html（烤进 HTML）

用法：
    python3 build-wiki.py
    # 或 wenjieplan build
"""
import json
import re
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
WIKI_DAILY = BASE / 'wiki' / 'plans' / 'daily'
OUTPUT_HTML = BASE / 'wenjie-daily-plan.html'
TEMPLATE = BASE / 'wenjie-daily-plan.template.html'


def parse_md_sections(md_text):
    """简单 Markdown 解析：提取 ## 段落"""
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
    """轻量 Markdown → HTML 转换（不依赖外部库）"""
    text = md_text

    # 代码块
    text = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', text, flags=re.DOTALL)
    # 行内代码
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # 标题
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\*🎯(.+?)\*\*$', r'<h1>🎯\1</h1>', text, flags=re.MULTILINE)
    # 粗体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # 斜体
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
    # 链接
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # 表格（简化）
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

    # 引用
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)
    # 水平线
    text = re.sub(r'^---+$', r'<hr>', text, flags=re.MULTILINE)
    # 无序列表
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>\n?)+', lambda m: '<ul>' + m.group(0) + '</ul>', text, flags=re.DOTALL)
    # 有序列表
    text = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    # 段落
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
    """Markdown 表格 → HTML 表格"""
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip('|').split('|')]
        rows.append(cells)

    # 跳过分隔行（如 |---|---|）
    rows = [r for r in rows if not all(set(c) <= set('-: ') for c in r)]

    if not rows:
        return ''

    html = '<table>'
    # 第一行是表头
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


def build():
    """主构建流程"""
    print(f"📚 扫描 {WIKI_DAILY} ...")

    # 读取所有每日计划
    daily_files = sorted(WIKI_DAILY.glob('*.md'))
    if not daily_files:
        print(f"❌ 没找到 Wiki 文件 in {WIKI_DAILY}")
        return False

    daily_data = []
    for f in daily_files:
        date = f.stem  # 例如 '2026-08-17'
        md_text = f.read_text(encoding='utf-8')
        parsed = parse_md_sections(md_text)

        # 渲染每个 section 的 body
        for sec in parsed['sections']:
            sec['html'] = md_to_html('\n'.join(sec['body']))

        daily_data.append({
            'date': date,
            'title': parsed['title'],
            'sections': parsed['sections']
        })
        print(f"  ✅ {date}: {parsed['title'][:50]}")

    # 找到今天（最近的日期 <= 今天）
    today_str = datetime.now().strftime('%Y-%m-%d')
    default_date = today_str
    for d in daily_data:
        if d['date'] <= today_str:
            default_date = d['date']

    # 序列化为 JSON 嵌入 HTML
    daily_json = json.dumps(daily_data, ensure_ascii=False, indent=2)
    default_date_json = json.dumps(default_date)

    # 读取模板
    if not TEMPLATE.exists():
        print(f"❌ 模板不存在: {TEMPLATE}")
        return False

    template = TEMPLATE.read_text(encoding='utf-8')

    # 替换占位符
    html = template.replace('__DAILY_DATA__', daily_json)
    html = html.replace('__DEFAULT_DATE__', default_date_json)
    html = html.replace('__BUILD_TIME__', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    html = html.replace('__TOTAL_DAYS__', str(len(daily_data)))

    # 写入
    OUTPUT_HTML.write_text(html, encoding='utf-8')
    print(f"\n✅ 生成 {OUTPUT_HTML}")
    print(f"   - {len(daily_data)} 天的内容已烤入")
    print(f"   - 默认日期: {default_date}")
    print(f"   - 文件大小: {OUTPUT_HTML.stat().st_size:,} 字节")
    return True


if __name__ == '__main__':
    build()