#!/bin/bash
# 验证 Qwen 3 VL 配置

echo "=== 1. 检查 API Key ==="
if [ -z "$DASHSCOPE_API_KEY" ]; then
  echo "❌ DASHSCOPE_API_KEY 未设置"
  echo ""
  echo "设置方法："
  echo "  1. 编辑 ~/.zshrc"
  echo "  2. 替换 '你的_API_KEY_在这里' 为真 API key"
  echo "  3. 运行: source ~/.zshrc"
  echo "  4. 重新运行此脚本"
  exit 1
else
  echo "✅ API Key 已设置（前 8 位）: ${DASHSCOPE_API_KEY:0:8}..."
fi

echo ""
echo "=== 2. 检查 Python SDK ==="
python3 -c "import dashscope; print('✅ dashscope 版本:', dashscope.__version__)" 2>&1

echo ""
echo "=== 3. 测试 API 连接 ==="
curl -s -X POST "$QWEN_VL_ENDPOINT" \
  -H "Authorization: Bearer $DASHSCOPE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-vl-plus",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 10
  }' | head -100