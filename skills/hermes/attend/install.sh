#!/bin/bash

# ==============================================
# FaceCall Hermes Skill 一键安装脚本
# ==============================================

set -e  # 出错立即退出

echo "🚀 FaceCall Hermes Skill 安装程序"
echo "=================================="
echo ""

# 检测当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

echo "📦 项目根目录: $PROJECT_ROOT"
echo ""

# 检查 Python 版本
echo "🔍 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "❌ 错误: 需要 Python >= 3.10，当前版本: $python_version"
    exit 1
fi
echo "✅ Python 版本: $python_version"
echo ""

# 安装核心库
echo "📚 安装 FaceCall 核心库..."
cd "$PROJECT_ROOT"
pip3 install -e . || {
    echo "❌ 安装失败，请检查 requirements.txt"
    exit 1
}
echo "✅ 核心库安装完成"
echo ""

# 检测 Hermes 目录
HERMES_SKILLS_DIR="$HOME/.hermes/skills"
if [ ! -d "$HERMES_SKILLS_DIR" ]; then
    echo "⚠️  未检测到 Hermes Agent，创建目录..."
    mkdir -p "$HERMES_SKILLS_DIR"
fi

# 链接 Skill 到 Hermes
echo "🔗 链接 Skill 到 Hermes..."
SKILL_TARGET="$HERMES_SKILLS_DIR/attend"

if [ -L "$SKILL_TARGET" ] || [ -e "$SKILL_TARGET" ]; then
    echo "⚠️  目标已存在，删除旧链接..."
    rm -rf "$SKILL_TARGET"
fi

ln -sf "$PROJECT_ROOT/hermes_integration/skills/attend" "$SKILL_TARGET"
echo "✅ Skill 已链接到: $SKILL_TARGET"
echo ""

# 复制配置模板
echo "📝 设置配置文件..."
CONFIG_SOURCE="$PROJECT_ROOT/config/config.yaml"
CONFIG_TARGET="$SKILL_TARGET/config.yaml"

if [ -f "$CONFIG_TARGET" ]; then
    echo "⚠️  配置文件已存在，跳过复制"
else
    if [ -f "$CONFIG_SOURCE" ]; then
        cp "$CONFIG_SOURCE" "$CONFIG_TARGET"
        echo "✅ 配置文件已复制"
    else
        echo "⚠️  未找到配置模板，请手动创建配置"
    fi
fi
echo ""

# 检查人脸数据库
FACES_DIR="$PROJECT_ROOT/faces"
if [ ! -d "$FACES_DIR" ] || [ -z "$(ls -A $FACES_DIR 2>/dev/null)" ]; then
    echo "⚠️  人脸数据库为空"
    echo "📋 请将学生照片放入: $FACES_DIR"
    echo "   格式: faces/学号.jpg"
fi
echo ""

# 完成
echo "=================================="
echo "✅ 安装完成！"
echo ""
echo "📖 下一步操作："
echo "   1. 编辑配置文件: $CONFIG_TARGET"
echo "   2. 准备人脸数据: $FACES_DIR"
echo "   3. 配置班级信息: $PROJECT_ROOT/config/classes.yaml"
echo ""
echo "🎯 使用方式："
echo "   # Telegram Bot"
echo "   /attend @photo.jpg course=体育3"
echo ""
echo "   # 命令行测试"
echo "   cd $SKILL_TARGET"
echo "   python executor.py --photo /path/to/photo.jpg --course 体育3"
echo ""
echo "📚 完整文档: $PROJECT_ROOT/docs/INDEX.md"
echo "=================================="
