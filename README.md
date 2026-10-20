# 🎯 FaceCall

**智能人脸识别考勤 Skill**

一个独立的、完整的 Skill 包，适配 Hermes、WorkBuddy 等 AI Agent 系统。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ 核心特性

- 🎭 **人脸识别考勤** - DeepFace + RetinaFace + Facenet512
- 🔌 **独立 Skill 包** - 一键安装到 Hermes/WorkBuddy
- 🤖 **多 Agent 支持** - 自动适配不同 Agent 系统
- ⚡ **开箱即用** - 克隆即可运行，无外部依赖
- 🛡️ **隐私优先** - 本地处理，仅传输学号
- 📦 **完全自包含** - 所有代码都在项目内

---

## 🚀 快速开始

### 一键安装（推荐）

```bash
# 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 一键安装（自动检测 Hermes/WorkBuddy）
bash install.sh

# 安装完成！
```

安装脚本会自动：
- ✅ 安装 Python 依赖
- ✅ 安装 FaceCall 核心库
- ✅ 检测并安装到 Hermes/WorkBuddy（如果存在）
- ✅ 复制配置文件

### Hermes Agent 用户

安装后立即可用：

```bash
# Telegram Bot
/attend @photo.jpg course=体育3

# 自动提交到教务系统
/attend @photo.jpg course=体育3 submit=true
```

**详细说明**: [hermes_integration/skills/attend/SKILL.md](hermes_integration/skills/attend/SKILL.md)

### WorkBuddy Agent 用户

安装后自动发现：

```python
# WorkBuddy 自动发现 facecall 工具
agent.use_tool(
    "facecall",
    photo="photo.jpg",
    course="体育3",
    submit=True
)
```

### 独立使用

```bash
# 直接使用 tool.py
python tool.py --photo photo.jpg --course "体育3" --submit

# 或导入为 Python 包
pip install -e .
```

```python
from facecall.face import FaceDetector, FaceMatcher
from facecall.rollcall import AttendanceSubmitter

detector = FaceDetector()
faces = detector.detect_faces("photo.jpg")
# ...
```

---

## 📖 使用场景

### 场景 1: Telegram Bot 日常点名

```
老师: [上传班级合照]
老师: /attend 体育3

Bot: ✅ 识别完成！
     📊 到课: 35/37人
     ✓ 正常: 35人
     ⚠️ 缺勤: 2人
     
     详细名单:
     [显示学生列表]
```

### 场景 2: 一键识别 + 自动提交

```bash
/attend @photo.jpg course=体育3 submit=true

# 自动完成:
# 1. 人脸识别
# 2. 提交到教务系统
# 3. 返回结果
```

### 场景 3: 定时自动点名

```bash
# 每周一、三、五早上 8:00 自动点名
/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

### 场景 4: 不确定项审核

```
识别结果:
✅ 35人确定到课
⚠️  2人不确定 (相似度低)

请审核: [显示不确定人脸]
老师: 确认/修正

系统: 已更新，是否提交？
老师: 提交
系统: ✅ 提交成功
```

---

## 🏗️ 架构设计

### FaceCall 是一个完整的 Skill 包

```
┌─────────────────────────────────────────┐
│  Agent Systems (Hermes/WorkBuddy/...)   │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  FaceCall Skill                   │ │
│  │  (独立、自包含)                   │ │
│  │                                   │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │  入口层                     │ │ │
│  │  │  executor.py / tool.py     │ │ │
│  │  └─────────────────────────────┘ │ │
│  │           ↓                       │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │  业务模块                   │ │ │
│  │  │  face/ + rollcall/         │ │ │
│  │  └─────────────────────────────┘ │ │
│  │           ↓                       │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │  基础设施                   │ │ │
│  │  │  DeepFace/TensorFlow       │ │ │
│  │  └─────────────────────────────┘ │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**设计原则**：
- ✅ **Self-Contained**: 所有功能代码都在项目内
- ✅ **Single Skill**: 对外是一个完整的 Skill，不是 Skill 框架
- ✅ **Multi-Agent**: 提供不同 Agent 的适配入口
- ✅ **No External Deps**: 不依赖任何外部项目

---

## 📁 项目结构

```
facecall/                            # 独立 Skill 包
├── skill.yaml                       # Skill 元数据
├── executor.py                      # Hermes 执行器（符号链接）
├── tool.py                          # WorkBuddy 工具入口
├── install.sh                       # 一键安装脚本 ⭐
│
├── src/facecall/                   # 核心库（完全自包含）
│   ├── face/                       # 人脸识别模块 ✅
│   │   ├── detector.py            # 人脸检测
│   │   ├── matcher.py             # 人脸匹配
│   │   ├── database.py            # 人脸数据库
│   │   └── annotator.py           # 图片标注
│   ├── rollcall/                   # 考勤提交模块 ✅
│   │   ├── client.py              # API 客户端
│   │   ├── crypto.py              # 加密工具
│   │   └── rollcall_client.py     # 考勤客户端
│   └── core/                       # 核心逻辑
│       ├── plugin.py
│       ├── plugin_manager.py
│       └── workflow.py
│
├── hermes_integration/             # Hermes 集成
│   └── skills/attend/
│       ├── executor.py             # 实际执行器
│       ├── config.yaml
│       └── SKILL.md
│
├── config/                         # 配置模板
│   ├── config.yaml
│   └── classes.yaml
│
├── docs/                           # 文档
├── tests/                          # 测试
├── requirements.txt
├── pyproject.toml
└── README.md
```

**关键点**：
- ✅ 所有功能代码都在 `src/facecall/` 内
- ✅ 无任何外部项目依赖
- ✅ 克隆即可运行

---

## 🔧 开发指南

### 环境要求

- Python 3.10+
- TensorFlow 2.15.0
- OpenCV 4.9.0
- 8GB+ RAM (人脸识别模型)

### 安装开发环境

```bash
# 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装为可编辑模式
pip install -e .
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 测试覆盖率
pytest --cov=src/facecall tests/

# 代码格式化
black src/ tests/
isort src/ tests/

# 代码检查
ruff check src/ tests/
mypy src/
```

### 开发新插件

参考 [docs/PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md)

```python
# 1. 实现插件协议
class MyPlugin:
    name = "my_plugin"
    version = "1.0.0"
    
    def execute(self, data): ...
    def validate(self, data): ...
    def get_info(self): ...

# 2. 注册到配置
# config/config.yaml
plugins:
  my_plugin:
    enabled: true
    module_path: "path.to.plugin"

# 3. 使用
manager = PluginManager("config.yaml")
result = manager.execute_plugin("my_plugin", data)
```

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **识别速度** | ~8 秒 | 37 人班级，CPU |
| **提交耗时** | ~5 秒 | 网络请求 |
| **总耗时** | 15-20 秒 | 完整流程 |
| **准确率** | 95%+ | 正常光照条件 |
| **内存占用** | ~2GB | 模型加载后 |

**优化潜力**:
- GPU 加速: 3-5x 提升
- 批量处理: 2-3x 提升
- 模型量化: 1.5-2x 提升

---

## 🔒 安全性

### 隐私保护

- ✅ 人脸数据本地处理
- ✅ 仅传输学号（不传图片）
- ✅ 配置文件可加密
- ✅ 支持环境变量存储密码

### 输入验证

- ✅ Plugin Protocol 强制 validate()
- ✅ Pydantic 数据验证
- ✅ 异常捕获和处理

### 依赖管理

- ✅ 版本固定（requirements.txt）
- ✅ 定期更新（安全补丁）
- ⚠️ 建议添加 `safety` 扫描

---

## 🤝 贡献

欢迎贡献代码、文档、问题反馈！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 开源协议

本项目采用 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

### 核心技术

- [DeepFace](https://github.com/serengil/deepface) - 人脸识别框架
- [TensorFlow](https://www.tensorflow.org/) - 深度学习框架
- [OpenCV](https://opencv.org/) - 计算机视觉库

### 灵感来源

感谢所有为开源社区做出贡献的开发者！

---

## 📞 联系方式

- **项目主页**: https://github.com/scfhome/facecall
- **问题反馈**: [GitHub Issues](https://github.com/scfhome/facecall/issues)
- **维护者**: scfmac

---

## 📈 版本历史

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

**当前版本**: v1.0.0

---

## 🎓 相关资源

### 文档
- [架构设计](docs/ARCHITECTURE.md)
- [插件开发](docs/PLUGIN_DEVELOPMENT.md)
- [Skill 使用手册](hermes_integration/skills/attend/SKILL.md)

### 安装指南
- [Hermes 安装](skills/hermes/attend/README.md)
- [WorkBuddy 安装](skills/workbuddy/facecall/README.md)

### 示例
- [配置示例](config/)
- [测试示例](tests/)

---

**FaceCall - 让 AI Agent 帮你点名！** 🎉
