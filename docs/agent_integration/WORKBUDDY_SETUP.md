# 🤖 WorkBuddy Agent 集成指南

> 将 FaceCall 集成到 WorkBuddy Agent 系统

---

## 📋 目录

- [简介](#简介)
- [快速安装](#快速安装)
- [使用方式](#使用方式)
- [Tool Schema](#tool-schema)
- [开发集成](#开发集成)
- [故障排查](#故障排查)

---

## 简介

### 什么是 WorkBuddy Tool？

WorkBuddy Tool 是标准化的能力接口，让 AI Agent 可以调用外部功能。

**FaceCall WorkBuddy Tool** 提供：
- 📸 人脸识别能力
- 📊 考勤数据处理
- 📤 自动提交功能
- 🔌 即插即用

### 架构图

```
WorkBuddy Agent
    ↓
Tool Registry (工具注册中心)
    ↓
FaceCall Tool (tool.py)
    ↓
FaceCall Core Library (核心库)
    ↓
DeepFace + TensorFlow (AI 模型)
```

---

## 快速安装

### 前提条件
- Python >= 3.10
- WorkBuddy Agent 已安装
- 2GB+ RAM

### 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 2. 运行安装脚本
bash skills/workbuddy/facecall/install.sh

# 3. 自动完成
# - 安装核心库
# - 链接 Tool 到 WorkBuddy
# - 复制配置模板
```

**安装成功**：
```
✅ 安装完成！

📖 下一步：
   1. 编辑配置: ~/.workbuddy/tools/facecall/config.yaml
   2. 准备数据: /path/to/facecall/faces/

🎯 WorkBuddy 会自动发现 facecall 工具
```

### 验证安装

```bash
# 检查 Tool 是否已注册
cd ~/.workbuddy/tools/facecall
python tool.py --help
```

---

## 使用方式

### 1. WorkBuddy Agent 调用

```python
from workbuddy import Agent

agent = Agent()

# 调用 facecall 工具
result = agent.use_tool(
    "facecall",
    photo="/path/to/class.jpg",
    course="体育3",
    submit=True,
    threshold=0.70
)

print(result)
```

**输出**：
```json
{
  "success": true,
  "data": {
    "total": 37,
    "present": 35,
    "absent": 2,
    "uncertain": 0,
    "students": [...],
    "submitted": true,
    "annotated_image": "/tmp/annotated_xxx.jpg"
  }
}
```

### 2. 命令行测试

```bash
cd ~/.workbuddy/tools/facecall

# 仅识别
python tool.py --photo class.jpg --course "体育3"

# 识别+提交
python tool.py --photo class.jpg --course "体育3" --submit

# 自定义阈值
python tool.py --photo class.jpg --course "体育3" --threshold 0.75
```

### 3. 自然语言调用

```
User: 帮我识别今天体育课的班级照片

WorkBuddy: 好的，我来识别一下。
            [调用 facecall 工具]
            识别完成！
            应到: 37 人
            实到: 35 人
            缺席: 2 人
            ...
```

---

## Tool Schema

### 工具元数据

```python
{
  "name": "facecall",
  "version": "1.0.0",
  "description": "人脸识别考勤工具，支持自动识别和提交"
}
```

### 输入 Schema

```json
{
  "type": "object",
  "properties": {
    "photo": {
      "type": "string",
      "description": "班级照片路径",
      "required": true
    },
    "course": {
      "type": "string",
      "description": "课程名称（如：体育3）",
      "required": true
    },
    "submit": {
      "type": "boolean",
      "description": "是否自动提交到教务系统",
      "default": false
    },
    "threshold": {
      "type": "number",
      "description": "人脸识别阈值（0-1）",
      "default": 0.70,
      "minimum": 0.0,
      "maximum": 1.0
    }
  },
  "required": ["photo", "course"]
}
```

### 输出 Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "执行是否成功"
    },
    "data": {
      "type": "object",
      "properties": {
        "total": {"type": "integer", "description": "应到人数"},
        "present": {"type": "integer", "description": "实到人数"},
        "absent": {"type": "integer", "description": "缺席人数"},
        "uncertain": {"type": "integer", "description": "不确定人数"},
        "students": {"type": "array", "description": "学生列表"},
        "submitted": {"type": "boolean", "description": "是否已提交"},
        "annotated_image": {"type": "string", "description": "标注图片路径"}
      }
    },
    "error": {
      "type": "string",
      "description": "错误信息（如果失败）"
    }
  }
}
```

---

## 开发集成

### Python SDK 集成

```python
from workbuddy_tools.facecall import FaceCallTool

# 初始化工具
tool = FaceCallTool(config_path="config.yaml")

# 执行识别
result = tool.execute(
    photo="class.jpg",
    course="体育3",
    submit=False,
    threshold=0.70
)

# 处理结果
if result["success"]:
    data = result["data"]
    print(f"实到: {data['present']}/{data['total']}")
    print(f"缺席: {data['absent']} 人")
    
    if data["uncertain"] > 0:
        print(f"⚠️  不确定: {data['uncertain']} 人")
else:
    print(f"错误: {result['error']}")
```

### 工具注册

```python
# WorkBuddy 自动调用
from workbuddy_tools.facecall.tool import register

schema = register()
# 返回完整的 Tool Schema
```

### 自定义适配器

```python
from workbuddy_tools.facecall import FaceCallTool

class MyCustomTool(FaceCallTool):
    """自定义扩展"""
    
    def execute(self, photo, course, **kwargs):
        # 前置处理
        result = super().execute(photo, course, **kwargs)
        
        # 后置处理（如发送通知）
        if result["success"]:
            self._send_notification(result["data"])
        
        return result
    
    def _send_notification(self, data):
        # 自定义逻辑
        pass
```

---

## 配置管理

### 配置文件

位置：`~/.workbuddy/tools/facecall/config.yaml`

```yaml
# 人脸识别配置
face_recognition:
  model: "Facenet512"      # 识别模型
  detector: "retinaface"   # 检测器
  threshold: 0.70          # 默认阈值

# 插件配置
plugins:
  rollcall:
    enabled: true
    config:
      username: "你的学号"
      password: "你的密码"
      base_url: "https://jwgl.cucn.edu.cn"
      timeout: 30

# 数据路径
data:
  faces_dir: "/path/to/faces"
  classes_file: "/path/to/classes.yaml"
```

### 环境变量

```bash
# .env 文件
FACECALL_USERNAME=your_username
FACECALL_PASSWORD=your_password
FACECALL_THRESHOLD=0.70
```

---

## 故障排查

### 1. Tool 未注册

**症状**: WorkBuddy 找不到 facecall 工具

**排查**:
```bash
# 检查文件
ls -la ~/.workbuddy/tools/facecall/

# 检查 register() 函数
python -c "from tool import register; print(register())"
```

**解决**:
```bash
# 重新安装
bash skills/workbuddy/facecall/install.sh

# 手动注册
workbuddy register-tool ~/.workbuddy/tools/facecall
```

### 2. 导入错误

**症状**: `ModuleNotFoundError: No module named 'facecall'`

**解决**:
```bash
# 检查核心库
pip list | grep facecall

# 重新安装
cd /path/to/facecall
pip install -e .
```

### 3. 配置错误

**症状**: `KeyError: 'username'`

**解决**:
```bash
# 检查配置文件
cat ~/.workbuddy/tools/facecall/config.yaml

# 复制模板
cp /path/to/facecall/config/config.yaml ~/.workbuddy/tools/facecall/
```

### 4. 识别失败

**症状**: `success: false, error: "..."`

**调试**:
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

from workbuddy_tools.facecall import FaceCallTool
tool = FaceCallTool()
result = tool.execute(photo="test.jpg", course="体育3")
```

---

## 性能优化

### 1. GPU 加速

```yaml
# config.yaml
face_recognition:
  use_gpu: true  # 需要 CUDA
```

### 2. 批量处理

```python
from workbuddy_tools.facecall import FaceCallTool

tool = FaceCallTool()

# 批量识别多个班级
courses = ["体育3", "体育4", "体育5"]
photos = ["class1.jpg", "class2.jpg", "class3.jpg"]

results = []
for photo, course in zip(photos, courses):
    result = tool.execute(photo=photo, course=course, submit=True)
    results.append(result)
```

### 3. 缓存优化

```python
# 缓存人脸数据库（加快后续识别）
tool = FaceCallTool()
tool.recognizer.load_faces_cache()  # 预加载
```

---

## 高级用法

### 1. 异步调用

```python
import asyncio
from workbuddy_tools.facecall import FaceCallTool

async def batch_recognize():
    tool = FaceCallTool()
    
    tasks = [
        tool.execute_async(photo=f"class{i}.jpg", course=f"体育{i}")
        for i in range(1, 6)
    ]
    
    results = await asyncio.gather(*tasks)
    return results
```

### 2. 流式输出

```python
# 实时获取识别进度
for progress in tool.execute_stream(photo="class.jpg", course="体育3"):
    print(f"进度: {progress['percent']}%")
```

### 3. 钩子函数

```python
tool = FaceCallTool()

# 识别前钩子
@tool.before_recognize
def preprocess(photo_path):
    # 预处理照片
    return enhanced_photo

# 识别后钩子
@tool.after_recognize
def postprocess(result):
    # 发送通知
    send_notification(result)
```

---

## 📚 相关文档

- [项目主页](../../README.md)
- [架构设计](../PROJECT_DESIGN.md)
- [Hermes 集成](HERMES_QUICKSTART.md)
- [插件开发](../PLUGIN_DEVELOPMENT.md)

---

## 🤝 贡献

欢迎贡献！请参考 [贡献指南](../../CONTRIBUTING.md)

---

**维护者**: scfmac  
**版本**: v1.0.0  
**更新**: 2026-10-20
