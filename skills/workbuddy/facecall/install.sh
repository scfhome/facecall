#!/bin/bash

# ==============================================
# FaceCall WorkBuddy Tool 一键安装脚本
# ==============================================

set -e

echo "🚀 FaceCall WorkBuddy Tool 安装程序"
echo "===================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "📦 项目根目录: $PROJECT_ROOT"
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 版本..."
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ 需要 Python >= 3.10"
    exit 1
fi
echo "✅ Python 版本检查通过"
echo ""

# 安装核心库
echo "📚 安装 FaceCall 核心库..."
cd "$PROJECT_ROOT"
pip3 install -e .
echo "✅ 核心库安装完成"
echo ""

# 检测 WorkBuddy 目录
WORKBUDDY_TOOLS_DIR="$HOME/.workbuddy/tools"
if [ ! -d "$WORKBUDDY_TOOLS_DIR" ]; then
    echo "⚠️  未检测到 WorkBuddy，创建目录..."
    mkdir -p "$WORKBUDDY_TOOLS_DIR"
fi

# 链接 Tool 到 WorkBuddy
echo "🔗 链接 Tool 到 WorkBuddy..."
TOOL_TARGET="$WORKBUDDY_TOOLS_DIR/facecall"

if [ -L "$TOOL_TARGET" ] || [ -e "$TOOL_TARGET" ]; then
    echo "⚠️  目标已存在，删除旧链接..."
    rm -rf "$TOOL_TARGET"
fi

ln -sf "$PROJECT_ROOT/skills/workbuddy/facecall" "$TOOL_TARGET"
echo "✅ Tool 已链接到: $TOOL_TARGET"
echo ""

# 复制配置模板
CONFIG_SOURCE="$PROJECT_ROOT/config/config.yaml"
CONFIG_TARGET="$TOOL_TARGET/config.yaml"

if [ -f "$CONFIG_TARGET" ]; then
    echo "⚠️  配置文件已存在"
else
    if [ -f "$CONFIG_SOURCE" ]; then
        cp "$CONFIG_SOURCE" "$CONFIG_TARGET"
        echo "✅ 配置文件已复制"
    fi
fi
echo ""

# 完成
echo "===================================="
echo "✅ 安装完成！"
echo ""
echo "📖 下一步："
echo "   1. 编辑配置: $CONFIG_TARGET"
echo "   2. 准备数据: $PROJECT_ROOT/faces/"
echo ""
echo "🎯 WorkBuddy 会自动发现 facecall 工具"
echo "===================================="
