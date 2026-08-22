#!/usr/bin/env python3
"""
题目生成器 · wenjie-plan
输入：题目类型 + 难度 + 数量
输出：可打印的练习册（带答案）

妈妈用法：
  python3 generate-worksheet.py math-add --difficulty 2 --count 10
  python3 generate-worksheet.py phonics --focus "ea" --count 10
"""
import random
import argparse
from datetime import datetime
from pathlib import Path

OUT_DIR = Path('/Users/xieli/Documents/Wenjie/worksheets')
OUT_DIR.mkdir(exist_ok=True)


def gen_addition(level, count=10):
    """加法生成器"""
    problems = []
    for _ in range(count):
        if level == 1:  # 1位+1位（不进位）
            a, b = random.randint(2, 8), random.randint(2, 9 - a)
        elif level == 2:  # 1位+1位（进位）
            a = random.randint(5, 9)
            b = random.randint(11 - a, 9)
            a, b = max(a, b), min(a, b)
        elif level == 3:  # 2位+1位（无进位）
            a = random.randint(11, 99)
            b = random.randint(2, 9)
            if (a % 10 + b) >= 10:
                continue
        elif level == 4:  # 2位+1位（进位）
            a = random.randint(11, 99)
            b = random.randint(2, 9)
            if (a % 10 + b) < 10:
                continue
        elif level == 5:  # 2位+2位（进位）
            a = random.randint(11, 99)
            b = random.randint(11, 99)
            if (a % 10 + b % 10) < 10:
                continue
        else:
            a, b = random.randint(11, 99), random.randint(2, 9)

        problems.append((a, b, a + b))
    return problems


def gen_subtraction(level, count=10):
    """减法生成器"""
    problems = []
    for _ in range(count):
        if level == 1:  # 1位-1位（不退位）
            a = random.randint(5, 9)
            b = random.randint(1, a - 1)
            if a - b >= 5:
                problems.append((a, b, a - b))
        elif level == 2:  # 1位-1位（结果=0）
            a, b = random.randint(2, 9), random.randint(2, 9)
            if a > b:
                problems.append((a, b, a - b))
        elif level == 3:  # 2位-1位（无借位）
            a = random.randint(11, 99)
            b = random.randint(2, 9)
            if a % 10 >= b:
                problems.append((a, b, a - b))
        elif level == 4:  # 2位-1位（借位）
            a = random.randint(11, 99)
            b = random.randint(2, 9)
            if a % 10 < b:
                problems.append((a, b, a - b))
        elif level == 5:  # 2位-2位（借位）
            a = random.randint(21, 99)
            b = random.randint(11, a - 10)
            if a % 10 < b % 10:
                problems.append((a, b, a - b))
    return problems[:count]


def gen_word_problems(count=5):
    """应用题生成器（基于场景）"""
    templates = [
        # 加法场景
        ("小红有{a}个苹果，妈妈又给她{b}个，现在小红有几个？", lambda: (random.randint(5, 15), random.randint(3, 12))),
        ("停车场有{a}辆车，又开进来{b}辆，现在有几辆？", lambda: (random.randint(8, 20), random.randint(5, 15))),
        ("小明有{a}元零花钱，爷爷又给他{b}元，现在有多少元？", lambda: (random.randint(10, 25), random.randint(5, 20))),
        # 减法场景
        ("树上有{a}只鸟，飞走了{b}只，还剩几只？", lambda: (random.randint(10, 25), random.randint(3, 10))),
        ("妈妈买了{a}个橙子，吃了{b}个，还剩几个？", lambda: (random.randint(8, 20), random.randint(2, 8))),
        ("公交车上有{a}人，到站下车{b}人，还有几人？", lambda: (random.randint(15, 30), random.randint(3, 12))),
    ]

    problems = []
    for _ in range(count):
        template, gen = random.choice(templates)
        a, b = gen()
        if '还剩' in template or '下车' in template:
            answer = a - b
        else:
            answer = a + b
        problems.append((template.format(a=a, b=b), a, b, answer))
    return problems


def gen_phonics(focus, count=10):
    """Phonics 生成器"""
    word_banks = {
        'ea': ['bread', 'head', 'ready', 'steady', 'weather', 'feather', 'instead', 'thread'],
        'ai': ['rain', 'train', 'pain', 'main', 'sail', 'tail', 'snail', 'paint'],
        'oo': ['book', 'look', 'took', 'cook', 'good', 'foot', 'wood', 'hook'],
        'ee': ['tree', 'see', 'bee', 'feet', 'meet', 'week', 'three', 'green'],
        'ar': ['car', 'far', 'star', 'park', 'dark', 'farm', 'bark', 'shark'],
        'or': ['for', 'fork', 'horse', 'storm', 'born', 'horn', 'torch', 'north'],
        'ou': ['house', 'mouse', 'cloud', 'loud', 'round', 'sound', 'found', 'ground'],
        'sh': ['ship', 'shop', 'shoe', 'fish', 'wish', 'dish', 'crash', 'brush'],
        'ch': ['chair', 'cheese', 'church', 'lunch', 'beach', 'peach', 'teach', 'much'],
        'th': ['this', 'that', 'the', 'then', 'them', 'with', 'bath', 'math'],
    }
    bank = word_banks.get(focus, word_banks['ea'])
    selected = random.sample(bank, min(count, len(bank)))
    while len(selected) < count:
        selected.append(random.choice(bank))
    return selected


def gen_chinese_chars(level, count=10):
    """汉字生成器"""
    # K2 常用字（妈妈可以根据需要扩展）
    k2_chars = [
        '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
        '人', '口', '手', '足', '目', '耳', '心', '日', '月', '水',
        '火', '木', '山', '石', '田', '禾', '竹', '雨', '雪', '风',
        '爸', '妈', '哥', '姐', '弟', '妹', '爷', '奶', '我', '你',
    ]
    if level == 1:  # 简单数字
        return ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'][:count]
    elif level == 2:  # 基础字
        return random.sample(k2_chars[:20], min(count, 20))
    else:
        return random.sample(k2_chars, min(count, len(k2_chars)))


def format_worksheet_md(title, problems, has_answer=True):
    """格式化为 Markdown"""
    md = f'# {title}\n\n'
    md += f'> 📅 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n'
    md += f'> 🎯 共 {len(problems)} 题\n\n'
    md += '---\n\n## 题目\n\n'

    # 判断题目类型
    if not problems:
        return md

    first = problems[0]

    if isinstance(first, tuple):
        if len(first) == 3 and isinstance(first[0], int):
            # 算术题 (a, b, answer)
            for i, (a, b, ans) in enumerate(problems, 1):
                op = '+' if ans > max(a, b) else '-'
                md += f'{i}. {a} {op} {b} = ____\n'
        elif len(first) == 4:
            # 应用题 (template, a, b, answer)
            for i, p in enumerate(problems, 1):
                md += f'{i}. {p[0]}\n'
        elif len(first) == 2:
            # Phonics/汉字 (word, action)
            for i, p in enumerate(problems, 1):
                md += f'{i}. {p[0]} ({p[1]})\n'

    md += '\n'

    if has_answer:
        md += '---\n\n## 答案（家长版）\n\n'
        for i, p in enumerate(problems, 1):
            if isinstance(p, tuple):
                if len(p) == 3 and isinstance(p[0], int):
                    md += f'{i}. {p[2]}\n'
                elif len(p) == 4:
                    # 应用题答案：拆解算式
                    is_add = '还' not in p[0] and '下' not in p[0]
                    op = '+' if is_add else '-'
                    md += f'{i}. {p[1]} {op} {p[2]} = {p[3]}\n'
                elif len(p) == 2:
                    md += f'{i}. {p[0]}\n'

    return md


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('type', choices=['math-add', 'math-sub', 'word', 'phonics', 'chinese'])
    parser.add_argument('--difficulty', type=int, default=2)
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--focus', default='ea')
    parser.add_argument('--title', default=None)
    args = parser.parse_args()

    title = args.title or f'{args.type} 练习'

    if args.type == 'math-add':
        problems = gen_addition(args.difficulty, args.count)
        title = f'加法 · 难度 {args.difficulty} · {args.count} 题'
    elif args.type == 'math-sub':
        problems = gen_subtraction(args.difficulty, args.count)
        title = f'减法 · 难度 {args.difficulty} · {args.count} 题'
    elif args.type == 'word':
        problems = gen_word_problems(args.count)
        title = f'应用题 · {args.count} 题'
    elif args.type == 'phonics':
        problems = [(w, '读') for w in gen_phonics(args.focus, args.count)]
        title = f'Phonics · {args.focus} · {args.count} 词'
    elif args.type == 'chinese':
        chars = gen_chinese_chars(args.difficulty, args.count)
        problems = [(c, '读') for c in chars]
        title = f'汉字 · 难度 {args.difficulty} · {args.count} 字'

    md = format_worksheet_md(title, problems)
    fname = OUT_DIR / f'{datetime.now().strftime("%Y%m%d-%H%M")}-{args.type}-L{args.difficulty}.md'
    fname.write_text(md, encoding='utf-8')
    print(f'✅ {fname}')
    print(f'\n{md}')


if __name__ == '__main__':
    main()