# 🎯 FaceCall

**智能人脸识别考勤系统 + 多 AI Agent 集成**

一键安装的 Skill，支持 Hermes、WorkBuddy 等 AI Agent 系统。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ 核心特性

- 🎭 **人脸识别考勤** - DeepFace + RetinaFace + Facenet512
- 🔌 **插件式架构** - 动态加载，易于扩展
- 🤖 **多 Agent 集成** - 支持 Hermes、WorkBuddy 等
- ⚡ **一键安装** - 3 分钟部署，开箱即用
- 🛡️ **隐私优先** - 本地处理，仅传输学号
- 📱 **多平台支持** - Telegram Bot / CLI / 定时任务

---

## 🚀 快速开始

### Hermes Agent 用户

```bash
# 1. 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 2. 一键安装
bash skills/hermes/attend/install.sh

# 3. 配置数据
vim config/config.yaml
# 填写教务系统账号、课程信息

# 4. 准备人脸数据库
mkdir -p faces
# 将学生照片放入 faces/ 目录（以学号命名，如 20210001.jpg）

# 5. 立即使用
/attend @photo.jpg course=体育3
```

**详细说明**: [skills/hermes/attend/README.md](skills/hermes/attend/README.md)

### WorkBuddy Agent 用户

```bash
# 1. 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 2. 一键安装
bash skills/workbuddy/facecall/install.sh

# 3. WorkBuddy 自动发现工具
# 立即可用
```

**详细说明**: [skills/workbuddy/facecall/README.md](skills/workbuddy/facecall/README.md)

### 直接使用核心库

```bash
# 安装
pip install -e .

# Python 调用
from facecall import FaceRecognizer, PluginManager

recognizer = FaceRecognizer()
result = recognizer.recognize("photo.jpg", course="体育3")
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

### 分层架构

```
┌─────────────────────────────────────────┐
│  Agent 生态层                            │
│  Hermes | WorkBuddy | AutoGPT | ...    │  ← 易于扩展
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  适配层（薄包装）                         │
│  executor.py | tool.py                  │  ← <100 行
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  核心业务层                              │
│  FaceRecognizer | PluginManager         │  ← 单点维护
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│  基础设施层                              │
│  DeepFace | TensorFlow | OpenCV        │
└─────────────────────────────────────────┘
```

**设计原则**:
- ✅ 核心库独立，不依赖任何 Agent
- ✅ 适配层极薄，易于维护
- ✅ 插件式扩展，动态加载
- ✅ 符合 SOLID 原则

详细架构: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 📁 项目结构

```
facecall/
├── README.md                    # 本文档
├── LICENSE                      # MIT 许可证
├── CHANGELOG.md                 # 版本历史
├── CONTRIBUTING.md              # 贡献指南
│
├── src/facecall/               # 核心库
│   ├── core/                   # 核心模块
│   │   ├── plugin.py           # 插件协议
│   │   ├── plugin_manager.py  # 插件管理器
│   │   └── workflow.py         # 工作流
│   ├── face/                   # 人脸识别
│   ├── rollcall/               # 考勤提交
│   └── config/                 # 配置管理
│
├── skills/                     # Agent 适配器 ⭐
│   ├── hermes/attend/          # Hermes Skill
│   │   ├── install.sh          # 一键安装
│   │   ├── requirements.txt
│   │   └── README.md
│   └── workbuddy/facecall/     # WorkBuddy Tool
│       ├── install.sh
│       ├── tool.py
│       └── README.md
│
├── hermes_integration/         # Hermes 原生集成
│   ├── skills/attend/
│   │   ├── executor.py         # Skill 执行器
│   │   ├── config.yaml         # 配置文件
│   │   └── SKILL.md            # 使用手册
│   └── plugins/rollcall/
│       └── plugin.py           # Plugin 实现
│
├── docs/                       # 文档
│   ├── ARCHITECTURE.md         # 架构设计
│   └── PLUGIN_DEVELOPMENT.md   # 插件开发
│
├── tests/                      # 测试
├── config/                     # 配置模板
│   ├── config.yaml
│   └── classes.yaml
│
├── requirements.txt            # 生产依赖
├── requirements-dev.txt        # 开发依赖
└── pyproject.toml              # 项目配置
```

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
