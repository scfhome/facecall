#!/bin/bash
#
# 测试 install.sh 的环境检测逻辑（不真正安装）
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 install.sh 环境检测"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. 检测 Python 版本
echo "1️⃣  Python 版本检测"
python3 --version
echo ""

# 2. 检测 Hermes
echo "2️⃣  Hermes 环境检测"
if [ -d "$HOME/.hermes" ]; then
    echo "✓ 检测到 Hermes: $HOME/.hermes"
    
    # 检测 venv
    HERMES_HOME="$HOME/.hermes"
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
            echo "✓ 找到 Hermes venv: $candidate"
            echo "  Python: $($HERMES_PYTHON --version)"
            echo "  pip: $($HERMES_PIP --version)"
            break
        fi
    done
    
    if [ -z "$HERMES_PYTHON" ]; then
        echo "✗ 未找到 Hermes venv"
    fi
else
    echo "✗ 未检测到 Hermes"
fi
echo ""

# 3. 检查当前 facecall 包状态
echo "3️⃣  FaceCall 包状态"
if [ -n "$HERMES_PYTHON" ]; then
    if $HERMES_PYTHON -c "import facecall" 2>/dev/null; then
        echo "✓ facecall 已安装到 Hermes venv"
        $HERMES_PYTHON -c "import facecall; print(f'  版本: {facecall.__version__}')"
    else
        echo "✗ facecall 未安装到 Hermes venv"
    fi
else
    echo "⚠ 跳过（未找到 Hermes venv）"
fi
echo ""

# 4. 检查 Skill 安装状态
echo "4️⃣  Hermes Skill 状态"
if [ -d "$HOME/.hermes/skills/attend" ]; then
    echo "✓ Skill 已安装: $HOME/.hermes/skills/attend"
    ls -lh "$HOME/.hermes/skills/attend/"
else
    echo "✗ Skill 未安装"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "环境检测完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
