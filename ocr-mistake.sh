#!/bin/bash
# ocr-mistake.sh · 从图片提取错题信息
# 用法：./ocr-mistake.sh inbox/filename.png

set -e

if [ -z "$1" ]; then
    echo "用法：./ocr-mistake.sh <图片路径>"
    echo ""
    echo "inbox 当前文件："
    ls -la ~/Documents/Wenjie/inbox/ 2>/dev/null | tail -n +2
    exit 1
fi

IMG="$1"

# 默认从 inbox 找
if [[ "$IMG" != *"/"* ]]; then
    IMG="$HOME/Documents/Wenjie/inbox/$IMG"
fi

if [ ! -f "$IMG" ]; then
    echo "❌ 文件不存在：$IMG"
    exit 1
fi

echo "📷 OCR 提取：$IMG"
echo "================================================"
tesseract "$IMG" stdout -l chi_sim+eng 2>/dev/null
echo ""
echo "================================================"
echo "✅ OCR 完成"
echo ""
echo "接下来告诉我提取的内容，我帮你写入 wiki/mistakes/"