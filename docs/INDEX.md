# 📚 FaceCall 集成文档索引

## 核心文档

### 🎯 快速开始
- [项目 README](../README.md) - 项目概述和快速开始
- [品牌手册](BRANDING.md) - 品牌理念和使用规范

### 🏗️ 架构设计
- [项目设计文档](../PROJECT_DESIGN.md) - 完整架构设计
- [插件开发指南](PLUGIN_DEVELOPMENT.md) - 如何开发插件

### 🔗 集成指南
- [Hermes 集成](HERMES_INTEGRATION.md) - Hermes Agent 深度集成分析
- [Hermes 快速开始](../hermes_integration/QUICKSTART.md) - 5分钟上手
- [深度分析](../DEEP_INTEGRATION_ANALYSIS.md) - 技术架构深度分析

---

## Hermes 集成

### 📦 组件

#### Skills (技能)
- **attend** - 人脸识别考勤 Skill
  - 📄 [SKILL.md](../hermes_integration/skills/attend/SKILL.md) - 完整使用文档
  - 🔧 [config.yaml](../hermes_integration/skills/attend/config.yaml) - 配置文件
  - ⚙️ [executor.py](../hermes_integration/skills/attend/executor.py) - 执行器

#### Plugins (插件)
- **rollcall** - 教务系统提交插件
  - 🔌 [plugin.py](../hermes_integration/plugins/rollcall/plugin.py) - 插件实现

#### Core (核心)
- 🧩 [plugin.py](../src/facecall/core/plugin.py) - 插件协议
- 🎛️ [plugin_manager.py](../src/facecall/core/plugin_manager.py) - 插件管理器

---

## 使用场景

### 场景1: Telegram Bot 日常点名
```
老师: [上传照片]
老师: /attend 体育3

Bot: ✅ 识别完成！
     📊 到课: 35/37人
```

### 场景2: 定时自动点名
```bash
/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

### 场景3: 一键完成
```
/attend @photo.jpg course=体育3 submit=true
```

---

## 技术架构

```
Hermes Agent
    ↓
attend Skill (识别)
    ↓
Plugin Manager
    ↓
rollcall Plugin (提交)
    ↓
教务系统 API
```

---

## 快速链接

| 文档 | 用途 | 适合人群 |
|------|------|---------|
| [QUICKSTART](../hermes_integration/QUICKSTART.md) | 快速开始 | 所有用户 |
| [SKILL.md](../hermes_integration/skills/attend/SKILL.md) | Skill 使用手册 | 终端用户 |
| [HERMES_INTEGRATION](HERMES_INTEGRATION.md) | 深度集成分析 | 开发者 |
| [PLUGIN_DEVELOPMENT](PLUGIN_DEVELOPMENT.md) | 插件开发 | 开发者 |
| [DEEP_ANALYSIS](../DEEP_INTEGRATION_ANALYSIS.md) | 架构深度分析 | 架构师 |

---

## 开发流程

### 1. 基础使用
1. 阅读 [QUICKSTART](../hermes_integration/QUICKSTART.md)
2. 安装配置
3. 测试基本功能

### 2. 进阶使用
1. 阅读 [SKILL.md](../hermes_integration/skills/attend/SKILL.md)
2. 了解所有参数和场景
3. 配置自动化流程

### 3. 插件开发
1. 阅读 [PLUGIN_DEVELOPMENT](PLUGIN_DEVELOPMENT.md)
2. 参考 rollcall 插件实现
3. 开发自定义插件

### 4. 架构理解
1. 阅读 [HERMES_INTEGRATION](HERMES_INTEGRATION.md)
2. 阅读 [DEEP_ANALYSIS](../DEEP_INTEGRATION_ANALYSIS.md)
3. 理解设计决策

---

## 测试

### 单元测试
```bash
pytest tests/test_rollcall_plugin.py -v
```

### 集成测试
```bash
python hermes_integration/skills/attend/executor.py \
  --photo test.jpg \
  --course "体育3"
```

---

## 贡献

欢迎贡献！请先阅读：
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [PLUGIN_DEVELOPMENT.md](PLUGIN_DEVELOPMENT.md)

---

**更新时间**: 2026-10-20  
**维护者**: scfmac
