#!/bin/bash
# start-mobile · 启动 DSH 移动端访问
# 用法：~/Documents/Wenjie/start-mobile.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🚀 启动文杰学习计划 · 移动端访问${NC}"
echo ""

# 1. 检查 DSH 是否在运行
DSH_PID=$(lsof -ti :3080 2>/dev/null | head -1)
if [ -z "$DSH_PID" ]; then
    echo -e "${YELLOW}⚠️  DSH 不在运行，正在启动...${NC}"
    cd /Users/xieli/.npm/_npx/1e7f6d9597241db0
    nohup dsh web > /tmp/dsh.log 2>&1 &
    sleep 3
    DSH_PID=$(lsof -ti :3080 2>/dev/null | head -1)
    if [ -z "$DSH_PID" ]; then
        echo -e "${RED}❌ DSH 启动失败，请检查${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ DSH 已启动 (PID: $DSH_PID)${NC}"
else
    echo -e "${GREEN}✅ DSH 已在运行 (PID: $DSH_PID)${NC}"
fi

# 2. 检查 ngrok 是否在运行
NGROK_PID=$(pgrep -f "ngrok http 3080" | head -1)
if [ -n "$NGROK_PID" ]; then
    echo -e "${GREEN}✅ ngrok 已在运行 (PID: $NGROK_PID)${NC}"
    echo ""
    echo -e "${CYAN}📱 你的手机 URL：${NC}"
    curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    for t in data.get('tunnels', []):
        if 'https' in t.get('public_url', ''):
            print('   👉', t['public_url'])
except:
    print('   ⚠️  无法获取 URL，请访问 http://localhost:4040')
" 2>/dev/null
    exit 0
fi

# 3. 启动 ngrok
echo ""
echo -e "${YELLOW}🚀 启动 ngrok 隧道...${NC}"
echo ""
echo -e "${CYAN}📋 ngrok 启动后会显示一个 https://xxxx.ngrok-free.app 的 URL${NC}"
echo -e "${CYAN}   把这个 URL 发到手机 Safari 即可访问 DSH${NC}"
echo -e "${CYAN}   ⚠️  免费版每次重启 URL 会变（按 Ctrl+C 停止）${NC}"
echo ""
echo -e "${CYAN}   按 Ctrl+C 停止 ngrok${NC}"
echo ""

# 实际启动 ngrok（前台运行，这样能看到 URL）
ngrok http 3080 --log=stdout