#!/bin/bash
# pushwenjie - 文杰学习计划一键更新脚本
# 用法：在 ~/Documents/Wenjie 目录下执行 ./update.sh

set -e

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}📝 文杰学习计划 · 一键更新${NC}"
echo ""

# 检查是否有更改
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  没有需要提交的更改${NC}"
    echo ""
    exit 0
fi

# 显示将要提交的内容
echo -e "${GREEN}📋 变更预览：${NC}"
git status --short
echo ""

# 询问 commit message
read -p "💬 提交说明（直接回车用默认）：" COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="update $(date '+%Y-%m-%d %H:%M')"
fi

# 添加所有变更
echo ""
echo -e "${GREEN}📦 添加文件...${NC}"
git add -A

# 提交
echo -e "${GREEN}💾 提交...${NC}"
git commit -m "$COMMIT_MSG"

# 推送
echo ""
echo -e "${GREEN}🚀 推送到 GitHub...${NC}"
if git push 2>&1; then
    echo ""
    echo -e "${GREEN}✅ 推送成功！${NC}"
    echo ""
    echo -e "${YELLOW}⏱  GitHub Pages 部署通常需要 30-90 秒${NC}"
    echo -e "${YELLOW}📱 1-2 分钟后家人刷新 URL 即可看到更新${NC}"
    echo ""
    echo "   👉 https://sherryxieli.github.io/wenjie-plan/"
    echo ""
else
    echo ""
    echo -e "${RED}❌ 推送失败${NC}"
    echo ""
    echo "可能原因："
    echo "  1. 需要 GitHub 认证（首次推送）"
    echo "  2. 网络问题"
    echo "  3. 仓库未在 GitHub 上创建"
    echo ""
    exit 1
fi