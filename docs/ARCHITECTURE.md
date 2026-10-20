# 🤖 AI Agent 集成架构

> FaceCall 多 Agent 系统集成完整方案

---

## 📋 目录

- [架构概览](#架构概览)
- [设计理念](#设计理念)
- [集成方案](#集成方案)
- [目录结构](#目录结构)
- [快速开始](#快速开始)
- [扩展指南](#扩展指南)

---

## 架构概览

### 核心设计

```
┌─────────────────────────────────────────────────────────┐
│                   AI Agent 生态系统                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ Hermes   │  │WorkBuddy │  │ AutoGPT  │  │  ...   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │
└───────┼─────────────┼─────────────┼─────────────┼───────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
        ┌─────────────▼────────────────┐
        │   Agent 适配层（薄包装）      │
        │  ┌────────┐    ┌──────────┐  │
        │  │ Skill  │    │   Tool   │  │
        │  │Wrapper │    │ Adapter  │  │
        │  └────┬───┘    └────┬─────┘  │
        └───────┼──────────────┼────────┘
                │              │
        ┌───────▼──────────────▼────────┐
        │     FaceCall 核心库            │
        │  ┌──────┐  ┌──────┐  ┌──────┐ │
        │  │ Face │  │Plugin│  │Config│ │
        │  │ Core │  │System│  │ Mgr  │ │
        │  └──────┘  └──────┘  └──────┘ │
        └───────┬────────────────────────┘
                │
        ┌───────▼────────────┐
        │  底层依赖框架       │
        │  DeepFace          │
        │  TensorFlow        │
        │  OpenCV            │
        └────────────────────┘
```

### 关键特性

| 特性 | 说明 |
|------|------|
| **核心库独立** | 业务逻辑与 Agent 解耦 |
| **适配层薄** | Agent 适配器 < 100 行代码 |
| **即插即用** | 一键安装脚本 |
| **多 Agent 复用** | 核心库共享，降低维护成本 |
| **易于扩展** | 新增 Agent 只需加适配器 |

---

## 设计理念

### 1. 分层架构

```
Layer 4: Agent 生态层    (Hermes, WorkBuddy, ...)
         ↓
Layer 3: 适配层          (Skill/Tool Wrapper)
         ↓
Layer 2: 核心业务层      (FaceCall Core Library)
         ↓
Layer 1: 基础设施层      (DeepFace, TensorFlow)
```

**原则**：
- ✅ 上层依赖下层，下层不知道上层
- ✅ 核心逻辑在 Layer 2，Agent 适配在 Layer 3
- ✅ Layer 3 是薄层，仅做数据转换和协议适配

### 2. 职责分离

| 层级 | 职责 | 示例 |
|------|------|------|
| **Agent 层** | 任务调度、对话管理 | Hermes Bot 接收消息 |
| **适配层** | 协议转换、参数映射 | executor.py 解析参数 |
| **核心层** | 业务逻辑、算法实现 | FaceRecognizer.recognize() |
| **基础层** | 模型推理、数据处理 | DeepFace.verify() |

### 3. 最小依赖原则

```python
# ✅ 好：核心库不依赖任何 Agent
from facecall import FaceRecognizer

# ❌ 差：核心库依赖 Hermes
from hermes import Skill
from facecall import FaceRecognizer  # 继承 Skill
```

---

## 集成方案

### 方案对比

| 方案 | 部署 | 维护 | 扩展 | 推荐度 |
|------|------|------|------|--------|
| **A. 独立项目** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ |
| **B. All-in-One** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ❌ |
| **C. 微服务** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⚠️ |
| **D. 混合方案** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ |

### 当前实现：方案 D（混合方案）

**特点**：
- 核心库 + 预打包适配器 + 一键安装脚本
- 兼顾专业性和易用性
- 符合 AI Agent 生态最佳实践

**结构**：
```
facecall/
├── src/facecall/           # 核心库（pip install）
├── skills/                 # 预打包适配器
│   ├── hermes/
│   │   └── attend/
│   │       ├── install.sh  # 一键安装
│   │       └── README.md
│   └── workbuddy/
│       └── facecall/
│           ├── install.sh
│           └── tool.py
└── docs/agent_integration/ # 集成文档
```

---

## 目录结构

### 完整结构

```
facecall/
├── src/facecall/                    # 核心库
│   ├── core/                        # 核心模块
│   │   ├── plugin.py                # 插件协议
│   │   ├── plugin_manager.py       # 插件管理器
│   │   └── workflow.py             # 工作流
│   ├── face/                        # 人脸识别
│   │   ├── recognizer.py           # 识别器
│   │   └── detector.py             # 检测器
│   ├── rollcall/                    # 考勤提交
│   │   ├── models.py               # 数据模型
│   │   └── client.py               # API 客户端
│   ├── config/                      # 配置管理
│   └── utils/                       # 工具函数
│
├── skills/                          # Agent 适配器
│   ├── hermes/                      # Hermes Agent
│   │   └── attend/
│   │       ├── install.sh           # 一键安装脚本
│   │       ├── requirements.txt     # 依赖列表
│   │       └── README.md            # 使用文档
│   │
│   └── workbuddy/                   # WorkBuddy Agent
│       └── facecall/
│           ├── tool.py              # Tool 适配器
│           ├── install.sh
│           └── README.md
│
├── hermes_integration/              # Hermes 原生集成
│   ├── skills/attend/               # Skill 实现
│   │   ├── executor.py
│   │   ├── SKILL.md
│   │   └── config.yaml
│   └── plugins/rollcall/            # Plugin 实现
│       └── plugin.py
│
├── docs/                            # 文档
│   ├── agent_integration/           # Agent 集成文档
│   │   ├── ARCHITECTURE.md          # 本文档
│   │   ├── HERMES_QUICKSTART.md     # Hermes 快速开始
│   │   └── WORKBUDDY_SETUP.md       # WorkBuddy 设置
│   ├── PROJECT_DESIGN.md
│   ├── HERMES_INTEGRATION.md
│   └── INDEX.md
│
├── config/                          # 配置模板
│   ├── config.yaml
│   └── classes.yaml
│
├── tests/                           # 测试
├── README.md                        # 主文档
├── LICENSE                          # 许可证
└── pyproject.toml                   # 项目配置
```

### 核心文件说明

| 文件 | 用途 | 目标用户 |
|------|------|----------|
| `skills/hermes/attend/install.sh` | Hermes 一键安装 | Hermes 用户 |
| `skills/workbuddy/facecall/tool.py` | WorkBuddy 适配器 | WorkBuddy 用户 |
| `src/facecall/` | 核心业务逻辑 | 所有用户 |
| `docs/agent_integration/` | 集成文档 | 开发者 |

---

## 快速开始

### Hermes Agent 用户

```bash
# 1. 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 2. 一键安装
bash skills/hermes/attend/install.sh

# 3. 配置数据
vim ~/.hermes/skills/attend/config.yaml

# 4. 使用
/attend @photo.jpg course=体育3
```

**详细文档**: [HERMES_QUICKSTART.md](HERMES_QUICKSTART.md)

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

**详细文档**: [WORKBUDDY_SETUP.md](WORKBUDDY_SETUP.md)

### 其他 Agent 系统

```python
# 直接使用核心库
pip install facecall

from facecall import FaceRecognizer, PluginManager

# 写个薄适配器即可
def your_agent_integration():
    recognizer = FaceRecognizer()
    result = recognizer.recognize(photo, course)
    # 接入你的 Agent 系统
```

---

## 扩展指南

### 新增 Agent 系统支持

#### Step 1: 创建目录

```bash
mkdir -p skills/your_agent/facecall
```

#### Step 2: 编写适配器

```python
# skills/your_agent/facecall/adapter.py

from facecall import FaceRecognizer, PluginManager

class FaceCallAdapter:
    """你的 Agent 系统适配器"""
    
    def __init__(self, config_path):
        self.recognizer = FaceRecognizer()
        self.plugin_manager = PluginManager(config_path)
    
    def execute(self, photo, course, submit=False):
        # 1. 人脸识别（复用核心库）
        result = self.recognizer.recognize(photo, course)
        
        # 2. 可选提交（复用插件系统）
        if submit:
            self.plugin_manager.execute_plugin(
                "rollcall",
                {"students": result["students"], "course": course}
            )
        
        # 3. 转换为你的 Agent 的输出格式
        return your_format(result)
```

#### Step 3: 编写安装脚本

```bash
# skills/your_agent/facecall/install.sh

#!/bin/bash
set -e

# 安装核心库
pip install -e .

# 链接到你的 Agent 目录
ln -sf $(pwd)/skills/your_agent/facecall ~/.your_agent/tools/facecall

echo "✅ 安装完成"
```

#### Step 4: 编写文档

```markdown
# skills/your_agent/facecall/README.md

# FaceCall YourAgent Tool

## 安装
\`\`\`bash
bash skills/your_agent/facecall/install.sh
\`\`\`

## 使用
\`\`\`
your_agent_command facecall photo.jpg 体育3
\`\`\`
```

#### Step 5: 测试

```bash
# 测试安装
bash skills/your_agent/facecall/install.sh

# 测试运行
python skills/your_agent/facecall/adapter.py
```

---

## 最佳实践

### 1. 适配器设计原则

```python
# ✅ 好：薄适配器
class Adapter:
    def execute(self, **kwargs):
        # 1. 参数转换
        params = self._convert_params(kwargs)
        
        # 2. 调用核心库
        result = core_library.execute(params)
        
        # 3. 结果转换
        return self._convert_result(result)

# ❌ 差：重复实现业务逻辑
class BadAdapter:
    def execute(self, **kwargs):
        # 重复实现人脸识别逻辑
        faces = self._detect_faces(photo)  # ❌
        matches = self._match_faces(faces)  # ❌
        ...
```

### 2. 配置管理

```yaml
# 统一配置格式
face_recognition:
  model: "Facenet512"
  threshold: 0.70

plugins:
  rollcall:
    enabled: true

# 各 Agent 加载同一份配置
```

### 3. 错误处理

```python
# 统一错误格式
{
    "success": False,
    "error": "错误描述",
    "error_code": "FACE_NOT_DETECTED",
    "details": {...}
}
```

### 4. 版本管理

```bash
# 核心库语义化版本
facecall==1.0.0

# 适配器跟随核心库版本
hermes-skill-attend==1.0.0
```

---

## 性能优化

### 1. 共享缓存

```python
# 核心库预加载人脸数据库
recognizer = FaceRecognizer()
recognizer.load_cache()  # 一次加载，多次使用
```

### 2. 批量处理

```python
# 多个 Agent 同时调用，复用模型
results = recognizer.batch_recognize([photo1, photo2, photo3])
```

### 3. GPU 加速

```yaml
# 所有 Agent 共享 GPU
face_recognition:
  use_gpu: true
  gpu_device: 0
```

---

## 监控和调试

### 1. 日志系统

```python
import logging

logger = logging.getLogger("facecall")
logger.setLevel(logging.DEBUG)

# 统一日志格式
logger.info(f"[{agent_name}] 开始识别...")
```

### 2. 性能追踪

```python
import time

start = time.time()
result = recognizer.recognize(photo, course)
elapsed = time.time() - start

logger.info(f"识别耗时: {elapsed:.2f}s")
```

### 3. 错误追踪

```python
try:
    result = recognizer.recognize(photo, course)
except Exception as e:
    logger.error(f"识别失败: {e}", exc_info=True)
    # 发送到监控系统
    sentry.capture_exception(e)
```

---

## 安全考虑

### 1. 隔离原则

```
Agent 1 → 独立进程 → 核心库（共享）
Agent 2 → 独立进程 → 核心库（共享）
```

### 2. 配置隔离

```bash
~/.hermes/skills/attend/config.yaml      # Hermes 配置
~/.workbuddy/tools/facecall/config.yaml  # WorkBuddy 配置
# 互不干扰
```

### 3. 权限控制

```python
# 敏感操作需要明确授权
if submit:
    # 检查权限
    if not has_permission("rollcall.submit"):
        raise PermissionError("无提交权限")
```

---

## 未来规划

### 短期（1 个月）
- [ ] 完善 WorkBuddy 适配器测试
- [ ] 添加 AutoGPT 支持
- [ ] 性能优化（批量处理）

### 中期（3 个月）
- [ ] 支持更多 Agent 系统
- [ ] 微服务部署方案
- [ ] 监控和日志系统

### 长期（6 个月）
- [ ] Agent 生态标准化
- [ ] 跨 Agent 协作
- [ ] 联邦学习集成

---

## 📚 相关文档

- [项目主页](../../README.md)
- [架构设计](../PROJECT_DESIGN.md)
- [Hermes 快速开始](HERMES_QUICKSTART.md)
- [WorkBuddy 设置](WORKBUDDY_SETUP.md)
- [插件开发](../PLUGIN_DEVELOPMENT.md)

---

## 🤝 贡献

欢迎贡献新的 Agent 适配器！

1. Fork 项目
2. 创建 `skills/your_agent/` 目录
3. 编写适配器和文档
4. 提交 Pull Request

详见 [贡献指南](../../CONTRIBUTING.md)

---

**维护者**: scfmac  
**版本**: v1.0.0  
**更新**: 2026-10-20
