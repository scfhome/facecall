#!/bin/bash
#
# FaceCall Skill 一键安装脚本
#
# 支持：
#   - Hermes Agent
#   - WorkBuddy Agent
#   - 独立使用
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# 检测当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR" && pwd)"

info "FaceCall Skill 一键安装"
echo ""

# 检测 Python 版本
if ! command -v python3 &> /dev/null; then
    error "未找到 Python 3，请先安装 Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
info "Python 版本: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.10" | bc -l) -eq 1 ]]; then
    error "Python 版本过低，需要 3.10+，当前: $PYTHON_VERSION"
    exit 1
fi

# 检测安装目标
echo ""
info "检测安装目标..."

INSTALL_TARGET=""

# 检测 Hermes（统一设置 HERMES_HOME）
if [ -n "$HERMES_HOME" ] && [ -d "$HERMES_HOME" ]; then
    INSTALL_TARGET="hermes"
    HERMES_SKILLS_DIR="$HERMES_HOME/skills"
    info "检测到 Hermes Agent: $HERMES_HOME"
elif [ -d "$HOME/.hermes" ]; then
    INSTALL_TARGET="hermes"
    HERMES_HOME="$HOME/.hermes"  # 统一设置变量
    HERMES_SKILLS_DIR="$HERMES_HOME/skills"
    info "检测到 Hermes Agent: $HERMES_HOME"
fi

# 检测 WorkBuddy
if [ -n "$WORKBUDDY_HOME" ] && [ -d "$WORKBUDDY_HOME" ]; then
    if [ -z "$INSTALL_TARGET" ]; then
        INSTALL_TARGET="workbuddy"
    else
        INSTALL_TARGET="both"
    fi
    WORKBUDDY_TOOLS_DIR="$WORKBUDDY_HOME/tools"
    info "检测到 WorkBuddy Agent: $WORKBUDDY_HOME"
elif [ -d "$HOME/.workbuddy" ]; then
    if [ -z "$INSTALL_TARGET" ]; then
        INSTALL_TARGET="workbuddy"
    else
        INSTALL_TARGET="both"
    fi
    WORKBUDDY_TOOLS_DIR="$HOME/.workbuddy/tools"
    info "检测到 WorkBuddy Agent: $HOME/.workbuddy"
fi

if [ -z "$INSTALL_TARGET" ]; then
    warning "未检测到 Hermes 或 WorkBuddy Agent"
    info "将仅安装 FaceCall 核心库"
    INSTALL_TARGET="standalone"
fi

echo ""
info "安装目标: $INSTALL_TARGET"
echo ""

# 检测正确的 pip 路径
if [ "$INSTALL_TARGET" = "hermes" ] || [ "$INSTALL_TARGET" = "both" ]; then
    # 尝试多个可能的 Hermes venv 路径
    HERMES_VENV_CANDIDATES=(
        "$HERMES_HOME/hermes-agent/venv"
        "$HERMES_HOME/.venv"
        "$HERMES_HOME/venv"
    )
    
    HERMES_PYTHON=""
    for candidate in "${HERMES_VENV_CANDIDATES[@]}"; do
        if [ -f "$candidate/bin/python" ]; then
            HERMES_PYTHON="$candidate/bin/python"
            HERMES_PIP="$candidate/bin/pip"
            break
        fi
    done
    
    if [ -z "$HERMES_PYTHON" ]; then
        warning "未找到 Hermes venv，将使用系统 Python"
        PIP_CMD="pip3"
    else
        info "使用 Hermes Python: $HERMES_PYTHON"
        PIP_CMD="$HERMES_PIP"
    fi
else
    # 独立安装使用系统 pip
    PIP_CMD="pip3"
fi

# 1. 安装 Python 依赖
info "步骤 1/3: 安装 Python 依赖..."
$PIP_CMD install -q -r requirements.txt
success "依赖安装完成"

# 2. 安装 FaceCall 核心库
info "步骤 2/3: 安装 FaceCall 核心库..."
$PIP_CMD install -q -e .
success "核心库安装完成"

# 3. 安装到 Agent（如果检测到）
if [ "$INSTALL_TARGET" = "hermes" ] || [ "$INSTALL_TARGET" = "both" ]; then
    info "步骤 3/3: 安装 Hermes Skill..."

    # 修正：使用正确的 skill 名称 attend
    mkdir -p "$HERMES_SKILLS_DIR/attend"

    # 复制必要文件
    cp SKILL.md "$HERMES_SKILLS_DIR/attend/"
    
    # 修正 executor.py 的 shebang 为 Hermes venv Python
    sed "1s|^#!/usr/bin/env python3|#!$HERMES_PYTHON|" \
        hermes_integration/skills/attend/executor.py \
        > "$HERMES_SKILLS_DIR/attend/executor.py"
    chmod +x "$HERMES_SKILLS_DIR/attend/executor.py"
    
    cp hermes_integration/skills/attend/config.yaml "$HERMES_SKILLS_DIR/attend/"

    success "Hermes Skill 安装完成"
    success "安装路径: $HERMES_SKILLS_DIR/attend"
fi

if [ "$INSTALL_TARGET" = "workbuddy" ] || [ "$INSTALL_TARGET" = "both" ]; then
    info "步骤 3/3: 安装 WorkBuddy Tool..."

    mkdir -p "$WORKBUDDY_TOOLS_DIR/facecall"

    # 复制必要文件
    cp tool.py "$WORKBUDDY_TOOLS_DIR/facecall/"
    cp -r config "$WORKBUDDY_TOOLS_DIR/facecall/"

    success "WorkBuddy Tool 安装完成"
    success "安装路径: $WORKBUDDY_TOOLS_DIR/facecall"
fi

# 完成
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "FaceCall Skill 安装成功！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 显示后续步骤
info "后续步骤:"
echo ""
echo "1️⃣  配置数据:"
echo "   编辑 config/config.yaml 填写教务系统账号"
echo ""
echo "2️⃣  准备人脸数据库:"
echo "   将学生照片放入 faces/ 目录（以学号命名）"
echo "   例如: faces/20210001.jpg"
echo ""
echo "3️⃣  准备班级名单:"
echo "   编辑 rosters/class_2024_1.yaml"
echo ""
echo "4️⃣  开始使用:"

if [ "$INSTALL_TARGET" = "hermes" ] || [ "$INSTALL_TARGET" = "both" ]; then
    echo "   Hermes: /attend @photo.jpg course=体育3"
fi

if [ "$INSTALL_TARGET" = "workbuddy" ] || [ "$INSTALL_TARGET" = "both" ]; then
    echo "   WorkBuddy: agent.use_tool('facecall', photo='photo.jpg', course='体育3')"
fi

if [ "$INSTALL_TARGET" = "standalone" ]; then
    echo "   Python: python tool.py --photo photo.jpg --course 体育3"
fi

echo ""
info "文档: $PROJECT_ROOT/README.md"
echo ""
