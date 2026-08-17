#!/bin/bash
# update.sh · 文杰学习计划 · 一键更新
# 流程：build-wiki.py → git add → commit → push

set -e

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo -e "${CYAN}🚀 文杰学习计划 · 一键更新${NC}"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 1. Wiki → HTML 构建
echo -e "${GREEN}📚 Step 1/4 · 从 Wiki 构建 HTML...${NC}"
if python3 build-wiki.py 2>&1 | tail -5; then
    echo -e "${GREEN}  ✅ 构建完成${NC}"
else
    echo -e "${RED}  ❌ 构建失败${NC}"
    exit 1
fi

# 2. 检查改动
echo ""
echo -e "${GREEN}📦 Step 2/4 · 检查改动...${NC}"
git add -A
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}  ⏭️  没有改动，跳过推送${NC}"
    exit 0
fi
git status --short

# 3. Commit
echo ""
echo -e "${GREEN}💾 Step 3/4 · Git commit...${NC}"
COMMIT_MSG="${1:-📝 更新文杰学习计划}"
git commit -m "$COMMIT_MSG" > /tmp/commit.log 2>&1 && {
    echo -e "${GREEN}  ✅ $COMMIT_MSG${NC}"
}

# 4. Push
echo ""
echo -e "${GREEN}📤 Step 4/4 · Git push...${NC}"
if git push 2>&1 | tail -3; then
    echo ""
    echo -e "${GREEN}✅ 推送成功！${NC}"
    echo ""
    echo -e "${YELLOW}⏱  GitHub Pages 30-90 秒后自动部署${NC}"
    echo -e "${CYAN}🌐 https://sherryxieli.github.io/wenjie-plan/${NC}"
    echo ""
else
    echo -e "${RED}❌ 推送失败${NC}"
    exit 1
fi