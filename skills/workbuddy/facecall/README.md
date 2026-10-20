# FaceCall WorkBuddy Tool

> 人脸识别考勤工具，适配 WorkBuddy Agent 系统

---

## 📦 简介

这是 **FaceCall** 的 WorkBuddy Tool 适配器，提供标准化的工具接口。

**核心功能**：
- 🎯 人脸识别考勤
- 🤖 自动提交教务系统
- 📊 结构化输出
- 🔌 即插即用

---

## 🚀 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 2. 运行安装脚本
bash skills/workbuddy/facecall/install.sh

# 3. WorkBuddy 自动发现工具
# 无需手动注册，自动可用
```

**耗时**: 约 3 分钟

---

## 🎯 使用方式

### WorkBuddy Agent
```python
# WorkBuddy 会自动发现并注册工具
agent.use_tool(
    "facecall",
    photo="/path/to/photo.jpg",
    course="体育3",
    submit=True
)
```

### 命令行测试
```bash
cd ~/.workbuddy/tools/facecall

# 仅识别
python tool.py --photo class.jpg --course "体育3"

# 识别+提交
python tool.py --photo class.jpg --course "体育3" --submit
```

---

## 📋 Tool Schema

### 输入参数
```json
{
  "photo": "string (required)",     // 照片路径
  "course": "string (required)",    // 课程名称
  "submit": "boolean (optional)",   // 是否提交（默认 false）
  "threshold": "number (optional)"  // 识别阈值（默认 0.70）
}
```

### 输出格式
```json
{
  "success": true,
  "data": {
    "total": 37,        // 应到人数
    "present": 35,      // 实到人数
    "absent": 2,        // 缺席人数
    "uncertain": 0,     // 不确定人数
    "students": [...],  // 学生列表
    "submitted": true,  // 是否已提交
    "annotated_image": "/tmp/xxx.jpg"  // 标注图片
  }
}
```

---

## ⚙️ 配置

配置文件：`~/.workbuddy/tools/facecall/config.yaml`

```yaml
face_recognition:
  model: "Facenet512"
  detector: "retinaface"
  threshold: 0.70

plugins:
  rollcall:
    enabled: true
    config:
      username: "你的学号"
      password: "你的密码"
```

---

## 🔧 开发集成

### Python SDK
```python
from workbuddy_tools.facecall import FaceCallTool

tool = FaceCallTool()
result = tool.execute(
    photo="class.jpg",
    course="体育3",
    submit=True,
    threshold=0.75
)

if result["success"]:
    data = result["data"]
    print(f"实到: {data['present']}/{data['total']}")
else:
    print(f"错误: {result['error']}")
```

### 工具注册
```python
# WorkBuddy 自动调用 register()
from workbuddy_tools.facecall.tool import register

schema = register()
# WorkBuddy 根据 schema 注册工具
```

---

## 📚 完整文档

- [项目主页](../../../README.md)
- [架构设计](../../../docs/PROJECT_DESIGN.md)
- [插件开发](../../../docs/PLUGIN_DEVELOPMENT.md)

---

**维护者**: scfmac  
**版本**: v1.0.0  
**更新**: 2026-10-20
