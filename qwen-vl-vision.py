#!/usr/bin/env python3
"""
Qwen 3 VL Vision 客户端
用法：
  python3 qwen-vl-vision.py image.png "请描述这张图片"
  python3 qwen-vl-vision.py image.png "请提取图片中的所有数学题目和答案"
"""
import os
import sys
import base64
import argparse
from pathlib import Path
import urllib.request
import urllib.error
import json


def encode_image_to_base64(image_path):
    """把图片转成 base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def detect_mime(image_path):
    """根据后缀判断 MIME 类型"""
    ext = Path(image_path).suffix.lower()
    mime_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.heic': 'image/heic',
    }
    return mime_map.get(ext, 'image/jpeg')


def call_qwen_vl(image_path, prompt, model='qwen3-vl-plus'):
    """调用 Qwen 3 VL API"""
    api_key = os.environ.get('DASHSCOPE_API_KEY')
    if not api_key:
        print('❌ 错误：未设置 DASHSCOPE_API_KEY')
        print('   运行: export DASHSCOPE_API_KEY="你的_API_KEY"')
        sys.exit(1)

    endpoint = os.environ.get(
        'QWEN_VL_ENDPOINT',
        'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
    )

    image_data = encode_image_to_base64(image_path)
    mime = detect_mime(image_path)
    image_url = f'data:{mime};base64,{image_data}'

    payload = {
        'model': model,
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'image_url', 'image_url': {'url': image_url}},
                    {'type': 'text', 'text': prompt},
                ],
            }
        ],
        'max_tokens': 2000,
        'temperature': 0.1,
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        return f'❌ HTTP 错误 {e.code}: {e.read().decode("utf-8")}'
    except Exception as e:
        return f'❌ 错误: {str(e)}'


def extract_math_mistakes(image_path):
    """专门提取数学错题"""
    prompt = """请仔细看这张图片中的数学题目，提取所有题目（包括错题和正确的题），按以下格式输出：

错题：
1. 题目：___  正确答案：___  文杰的答案：___
2. ...

正确的题：
1. 题目：___  答案：___
2. ...

如果题目是计算题（如 7+5=13），请拆解为：
- 题目类型：（加法/减法/进位加法/借位减法/...）
- 数字范围：（如 1位+1位 / 2位+1位）
- 错误模式：（进位忘了/借位错了/抄错数字/计算错误）

最后给一个简短的总结：这道题主要考察什么能力？"""
    return call_qwen_vl(image_path, prompt)


def describe_image(image_path):
    """通用描述图片"""
    prompt = "请详细描述这张图片的内容，包括所有文字、数字、公式。"
    return call_qwen_vl(image_path, prompt)


def main():
    parser = argparse.ArgumentParser(description='Qwen 3 VL Vision 客户端')
    parser.add_argument('image', help='图片路径')
    parser.add_argument('prompt', nargs='?', default=None, help='提示词')
    parser.add_argument('--mode', choices=['describe', 'math', 'custom'],
                        default='describe', help='预设模式')
    parser.add_argument('--model', default='qwen3-vl-plus', help='模型名')
    args = parser.parse_args()

    if not Path(args.image).exists():
        print(f'❌ 找不到图片: {args.image}')
        sys.exit(1)

    print(f'📸 读取图片: {args.image}')
    print(f'🤖 模型: {args.model}')
    print('---')

    if args.mode == 'math':
        result = extract_math_mistakes(args.image)
    elif args.mode == 'custom' and args.prompt:
        result = call_qwen_vl(args.image, args.prompt, args.model)
    else:
        result = describe_image(args.image)

    print(result)


if __name__ == '__main__':
    main()