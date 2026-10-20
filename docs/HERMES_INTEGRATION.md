# 🤖 Hermes 接入 FaceCall 深度分析

## 📋 目录

- [1. Hermes 系统概述](#1-hermes-系统概述)
- [2. 接入方案对比](#2-接入方案对比)
- [3. 推荐方案：插件式集成](#3-推荐方案插件式集成)
- [4. 技术实现](#4-技术实现)
- [5. 使用体验](#5-使用体验)
- [6. 完整工作流](#6-完整工作流)

---

## 1. Hermes 系统概述

### 1.1 什么是 Hermes？

**Hermes** 是一个 AI Agent 执行平台，支持多种接入方式：

```
Hermes Agent
├── CLI (命令行)
├── Telegram Bot (即时通讯)
├── Discord Bot
├── Slack Bot
├── Cron (定时任务)
└── API (RESTful)
```

### 1.2 Skill 机制

```
┌────────────────────────────────────┐
│ Hermes Agent (AI 大脑)              │
│ - 理解自然语言                      │
│ - 参数提取                          │
│ - 任务编排                          │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ Skill (可执行任务)                  │
│ - SKILL.md (说明文档)               │
│ - executor.py (执行器)              │
└──────────────┬─────────────────────┘
               │
               ▼
┌────────────────────────────────────┐
│ 底层工具                            │
│ - CLI 脚本                          │
│ - Python 库                         │
│ - API 调用                          │
└────────────────────────────────────┘
```

### 1.3 现有 Skill: rollcall

**位置**: `cucn-rollcall-cli/hermes_skill/`

**功能**: 自动提交考勤到教务系统

**使用**:
```bash
# Hermes 中调用
/rollcall date=today course=体育3 mode=auto
```

**限制**: 
- ❌ 只能提交考勤
- ❌ 不能识别人脸
- ❌ 无法验证真实到课

---

## 2. 接入方案对比

### 方案 A: 独立 Skill（松耦合）⭐⭐⭐

```
┌─────────────────────────────────┐
│ Hermes Agent                     │
└──────┬──────────────┬───────────┘
       │              │
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│ facecall    │  │ rollcall     │
│ Skill       │  │ Skill        │
└──────┬──────┘  └──────┬───────┘
       │                │
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│ FaceCall    │  │ CUCN         │
│ CLI         │  │ Rollcall CLI │
└─────────────┘  └──────────────┘
```

**特点**:
- 两个独立 Skill
- 用户先调用 `facecall`，再调用 `rollcall`
- Hermes 作为编排层

**优点**:
- ✅ 解耦清晰
- ✅ 各自独立开发
- ✅ 可单独使用
- ✅ 易于测试

**缺点**:
- ❌ 用户需要两步操作
- ❌ 需要传递中间文件
- ❌ 体验不够流畅

**使用示例**:
```bash
# 步骤1: 人脸识别
/facecall check @class.jpg course=体育3 output=attendance.json

# 步骤2: 提交考勤
/rollcall date=today course=体育3 input=@attendance.json
```

---

### 方案 B: 一体化 Skill（紧耦合）⭐⭐⭐⭐⭐

```
┌─────────────────────────────────┐
│ Hermes Agent                     │
└──────────────┬──────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ attend Skill (一体化)             │
│ - 人脸识别                        │
│ - 考勤提交                        │
│ - 结果报告                        │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ FaceCall 统一工作流               │
│ - face module                     │
│ - rollcall module                 │
│ - workflow orchestrator           │
└──────────────────────────────────┘
```

**特点**:
- 一个 Skill 完成全流程
- 内部调用 FaceCall 工作流
- 自动流转，无需中间文件

**优点**:
- ✅ 一条命令完成
- ✅ 用户体验最佳
- ✅ 自动流转
- ✅ 统一错误处理

**缺点**:
- ❌ 紧耦合
- ❌ 需要 FaceCall 完整实现

**使用示例**:
```bash
# 一条命令完成
/attend @class.jpg course=体育3

# 或自然语言
"识别这张照片并提交体育3的考勤"
```

---

### 方案 C: 插件式集成（推荐）⭐⭐⭐⭐⭐

```
┌─────────────────────────────────┐
│ Hermes Agent                     │
└──────────────┬──────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│ attend Skill (核心)               │
│ - 人脸识别                        │
│ - 审核确认                        │
│ - 结果输出                        │
└──────────────┬───────────────────┘
               │
               │ [可选插件]
               ▼
┌──────────────────────────────────┐
│ rollcall Plugin                   │
│ - auto_submit: true/false         │
│ - 自动提交到教务系统               │
└──────────────────────────────────┘
```

**特点**:
- Skill 专注人脸识别
- 提交作为可选插件
- 用户可控

**优点**:
- ✅ 解耦清晰
- ✅ 灵活可控
- ✅ 可配置化
- ✅ 渐进增强

**缺点**:
- ⚠️ 需要插件机制

**使用示例**:
```bash
# 默认：仅识别
/attend @class.jpg course=体育3

# 启用自动提交
/attend @class.jpg course=体育3 submit=true

# 配置文件
config.yaml:
  plugins:
    rollcall:
      enabled: true
      auto_submit: false  # 需手动确认
```

---

## 3. 推荐方案：插件式集成

### 3.1 架构设计

```
┌─────────────────────────────────────────────┐
│ Hermes Ecosystem                             │
│                                              │
│  ┌──────────────────────────────┐           │
│  │ attend Skill (核心)           │           │
│  │ - facecall check             │           │
│  │ - 人脸识别                    │           │
│  │ - 结果审核                    │           │
│  │ - JSON 输出                   │           │
│  └────────────┬─────────────────┘           │
│               │                              │
│               │ 插件钩子 (plugin hook)       │
│               ▼                              │
│  ┌──────────────────────────────┐           │
│  │ rollcall Plugin               │           │
│  │ - 读取 JSON                   │           │
│  │ - 提交到教务系统              │           │
│  │ - 返回结果                    │           │
│  └──────────────────────────────┘           │
│                                              │
└─────────────────────────────────────────────┘
```

### 3.2 目录结构

```
facecall/
├── hermes_integration/
│   ├── skills/
│   │   └── attend/
│   │       ├── SKILL.md              # Skill 说明
│   │       ├── executor.py           # 执行器
│   │       └── config.yaml           # 配置
│   │
│   ├── plugins/
│   │   └── rollcall/
│   │       ├── __init__.py
│   │       ├── plugin.py             # 插件实现
│   │       └── config.yaml           # 插件配置
│   │
│   └── docs/
│       ├── HERMES_INTEGRATION.md     # 集成指南
│       └── PLUGIN_DEVELOPMENT.md     # 插件开发
│
├── src/facecall/
│   ├── face/                         # 人脸识别模块
│   ├── rollcall/                     # 教务系统模块
│   ├── core/
│   │   ├── workflow.py               # 工作流
│   │   └── plugin_manager.py         # 插件管理器 ⭐
│   └── ...
```

### 3.3 为什么选择插件式？

**1. 职责清晰**
```
Skill 层 (attend):
- 职责：人脸识别
- 输入：照片
- 输出：考勤JSON

Plugin 层 (rollcall):
- 职责：考勤提交
- 输入：考勤JSON
- 输出：提交结果
```

**2. 可配置化**
```yaml
# config.yaml
skills:
  attend:
    threshold: 0.70
    annotate: true
    
plugins:
  rollcall:
    enabled: true           # 启用插件
    auto_submit: false      # 需要确认
    system: "cucn"          # 教务系统类型
    
    # 确认策略
    confirm_when:
      - uncertain > 0       # 有不确定人脸
      - absent > 5          # 缺勤超过5人
      
    # 自动提交条件
    auto_when:
      - uncertain == 0      # 无不确定
      - absent <= 2         # 缺勤≤2人
```

**3. 可扩展性**
```
插件生态：

rollcall (教务系统提交)
├── cucn_plugin         # 中传南广
├── zfsoft_plugin       # 正方教务
└── custom_plugin       # 自定义系统

notification (通知插件)
├── telegram_plugin     # Telegram 通知
├── email_plugin        # 邮件通知
└── wechat_plugin       # 企业微信

analytics (分析插件)
├── attendance_report   # 考勤报表
├── trend_analysis      # 趋势分析
└── anomaly_detection   # 异常检测
```

---

## 4. 技术实现

### 4.1 核心：Plugin Manager

```python
# src/facecall/core/plugin_manager.py

from dataclasses import dataclass
from typing import Protocol, Any
import importlib


class Plugin(Protocol):
    """插件协议"""
    
    name: str
    version: str
    
    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        """执行插件
        
        Args:
            data: 插件输入数据
            
        Returns:
            dict: 插件执行结果
        """
        ...
    
    def validate(self, data: dict[str, Any]) -> bool:
        """验证输入数据
        
        Args:
            data: 待验证数据
            
        Returns:
            bool: 是否有效
        """
        ...


@dataclass(frozen=True)
class PluginConfig:
    """插件配置"""
    name: str
    enabled: bool
    module_path: str
    config: dict[str, Any]


class PluginManager:
    """插件管理器"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.plugins: dict[str, Plugin] = {}
        self._load_plugins()
    
    def _load_plugins(self) -> None:
        """加载所有启用的插件"""
        import yaml
        
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
        
        for plugin_name, plugin_config in config.get("plugins", {}).items():
            if not plugin_config.get("enabled", False):
                continue
            
            # 动态加载插件模块
            module_path = plugin_config["module_path"]
            module = importlib.import_module(module_path)
            
            # 实例化插件
            plugin_class = getattr(module, "Plugin")
            plugin = plugin_class(plugin_config)
            
            self.plugins[plugin_name] = plugin
    
    def execute_plugin(
        self,
        plugin_name: str,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """执行指定插件
        
        Args:
            plugin_name: 插件名称
            data: 输入数据
            
        Returns:
            dict: 执行结果
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return {
                "success": False,
                "message": f"插件不存在: {plugin_name}"
            }
        
        # 验证数据
        if not plugin.validate(data):
            return {
                "success": False,
                "message": "数据验证失败"
            }
        
        # 执行插件
        try:
            result = plugin.execute(data)
            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"插件执行失败: {str(e)}"
            }
    
    def list_plugins(self) -> list[str]:
        """列出所有已加载的插件"""
        return list(self.plugins.keys())
```

### 4.2 Rollcall Plugin

```python
# hermes_integration/plugins/rollcall/plugin.py

from typing import Any
import subprocess
import json
from pathlib import Path


class Plugin:
    """教务系统提交插件"""
    
    name = "rollcall"
    version = "1.0.0"
    
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.rollcall_cli_path = config.get(
            "rollcall_cli_path",
            "cucn-rollcall-cli/rollcall_auto.py"
        )
    
    def validate(self, data: dict[str, Any]) -> bool:
        """验证输入数据"""
        required_fields = ["students", "course", "date"]
        return all(field in data for field in required_fields)
    
    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        """执行提交
        
        Args:
            data: 考勤数据
                {
                    "students": [...],
                    "course": "体育3",
                    "date": "2026-10-20"
                }
        
        Returns:
            dict: 提交结果
        """
        # 1. 准备临时 JSON 文件
        temp_file = Path("/tmp/attendance.json")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump({"students": data["students"]}, f, ensure_ascii=False)
        
        # 2. 构建命令
        cmd = [
            "python3",
            self.rollcall_cli_path,
            "--date", data["date"],
            "--course", data["course"],
            "--mode", "manual",
            "--input", str(temp_file)
        ]
        
        # 3. 执行命令
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result = json.loads(proc.stdout)
            
            # 4. 清理临时文件
            temp_file.unlink(missing_ok=True)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "message": f"提交失败: {str(e)}"
            }
```

### 4.3 Hermes Skill: attend

```python
# hermes_integration/skills/attend/executor.py

import json
import subprocess
from pathlib import Path
from facecall.core.plugin_manager import PluginManager


def execute_skill(**kwargs):
    """Attend Skill 执行器
    
    Args:
        **kwargs: Hermes 传递的参数
            - photo: 照片路径 (@标记)
            - course: 课程名称
            - date: 日期 (默认today)
            - submit: 是否自动提交 (默认false)
            - threshold: 识别阈值 (默认0.70)
    
    Returns:
        dict: 执行结果
    """
    # 1. 参数提取
    photo = kwargs.get("photo", "")
    if photo.startswith("@"):
        photo = photo[1:]
    
    if not photo:
        return {
            "success": False,
            "message": "缺少必需参数: photo"
        }
    
    course = kwargs.get("course")
    if not course:
        return {
            "success": False,
            "message": "缺少必需参数: course"
        }
    
    date = kwargs.get("date", "today")
    threshold = float(kwargs.get("threshold", 0.70))
    auto_submit = kwargs.get("submit", "false").lower() == "true"
    
    # 2. 调用 FaceCall 识别
    result = run_facecall_check(
        photo=photo,
        course=course,
        date=date,
        threshold=threshold
    )
    
    if not result["success"]:
        return result
    
    # 3. 检查不确定人脸
    uncertain_count = result.get("summary", {}).get("uncertain", 0)
    
    if uncertain_count > 0:
        # 需要人工确认
        return {
            "success": True,
            "phase": "review_required",
            "message": f"识别完成，有 {uncertain_count} 位同学不确定，需要人工审核",
            "data": result,
            "next_action": "请审核后再提交"
        }
    
    # 4. 执行插件（如果启用）
    if auto_submit:
        plugin_result = submit_via_plugin(result, course, date)
        return {
            "success": True,
            "phase": "completed",
            "recognition": result,
            "submission": plugin_result
        }
    
    # 5. 仅识别，不提交
    return {
        "success": True,
        "phase": "recognition_only",
        "message": "识别完成，考勤数据已保存",
        "data": result,
        "next_action": "使用 /rollcall 提交考勤"
    }


def run_facecall_check(
    photo: str,
    course: str,
    date: str,
    threshold: float
) -> dict:
    """调用 FaceCall 识别"""
    cmd = [
        "facecall", "check",
        "--photo", photo,
        "--course", course,
        "--date", date,
        "--threshold", str(threshold),
        "--output", "/tmp/attendance.json",
        "--format", "json"
    ]
    
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120
    )
    
    return json.loads(proc.stdout)


def submit_via_plugin(
    recognition_result: dict,
    course: str,
    date: str
) -> dict:
    """通过插件提交考勤"""
    manager = PluginManager("config/plugins.yaml")
    
    plugin_data = {
        "students": recognition_result["students"],
        "course": course,
        "date": date
    }
    
    return manager.execute_plugin("rollcall", plugin_data)
```

### 4.4 Skill 说明文档

```markdown
# hermes_integration/skills/attend/SKILL.md

---
name: attend
description: Face recognition attendance for classroom
author: scfmac
version: 1.0.0
tags: [attendance, face-recognition, education]
platforms: [cli, telegram, cron]
requires_approval: false
---

# 🎓 点到 - 智能课堂考勤

基于人脸识别的智能考勤系统。

## 🎯 功能特性

- ✅ 人脸识别点名
- ✅ 自动标注图片
- ✅ 不确定人脸审核
- ✅ 可选自动提交
- ✅ JSON 格式导出

## 📖 使用方法

### 1. 基础识别（仅识别）

```
/attend @class.jpg course=体育3
```

### 2. 识别并提交（一键完成）

```
/attend @class.jpg course=体育3 submit=true
```

### 3. 自定义阈值

```
/attend @class.jpg course=体育3 threshold=0.65
```

### 4. 自然语言

```
"识别这张照片的考勤，体育3"
"拍了一张课堂照片，帮我点名"
```

## 📋 参数说明

| 参数 | 必需 | 默认 | 说明 |
|------|------|------|------|
| `photo` | ✅ | - | 照片路径（@标记） |
| `course` | ✅ | - | 课程名称 |
| `date` | ❌ | today | 日期 |
| `threshold` | ❌ | 0.70 | 识别阈值 |
| `submit` | ❌ | false | 是否自动提交 |

## 🔄 执行流程

1. **加载照片** - 读取课堂照片
2. **人脸检测** - RetinaFace 检测人脸
3. **特征提取** - Facenet512 提取特征
4. **匹配识别** - 与数据库比对
5. **生成标注** - 标注识别结果
6. **审核确认** - 不确定人脸需人工确认
7. **插件执行** - 可选自动提交
8. **结果报告** - 返回详细结果

## ✅ 输出示例

### 仅识别模式

```json
{
  "success": true,
  "phase": "recognition_only",
  "message": "识别完成，考勤数据已保存",
  "data": {
    "date": "2026-10-20",
    "course": "体育3",
    "summary": {
      "total": 37,
      "present": 35,
      "absent": 2,
      "uncertain": 0
    },
    "students": [...]
  },
  "next_action": "使用 /rollcall 提交考勤"
}
```

### 识别+提交模式

```json
{
  "success": true,
  "phase": "completed",
  "recognition": {
    "summary": {...},
    "students": [...]
  },
  "submission": {
    "success": true,
    "submitted": 37,
    "message": "提交成功"
  }
}
```

## 📊 使用场景

### 场景1: 快速点名
```
# 早上8点，上课前
/attend @class.jpg course=体育3

# 输出
✅ 识别完成: 35/37人到课
📊 详细结果已保存
➡️ 使用 /rollcall 提交
```

### 场景2: 一键完成
```
# 所有人都到课，直接提交
/attend @class.jpg course=体育3 submit=true

# 输出
✅ 识别完成: 37/37人到课
✅ 已自动提交到教务系统
```

### 场景3: 需要审核
```
# 有不确定人脸
/attend @class.jpg course=体育3 submit=true

# 输出
⚠️ 识别完成，有2位同学不确定
📸 请查看标注图片确认
➡️ 确认后使用 /rollcall 提交
```

## 🔧 配置

```yaml
# config.yaml
skills:
  attend:
    threshold: 0.70
    annotate: true
    database_path: "databases/default.pkl"
    
plugins:
  rollcall:
    enabled: true
    auto_submit: false
    confirm_when:
      - uncertain > 0
```

## 🎓 最佳实践

1. **先测试** - 第一次使用先不加 `submit=true`
2. **调整阈值** - 根据准确率调整 threshold
3. **定期更新** - 学期初更新人脸数据库
4. **审核标注图** - 不确定人脸要看标注图

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**Last Updated**: 2026-10-20
```

---

## 5. 使用体验

### 5.1 三种使用模式

**模式1: 独立使用（无 Hermes）**
```bash
# 命令行直接调用
facecall check photo.jpg --course "体育3"
```

**模式2: Hermes + Skill（仅识别）**
```bash
# Hermes 中调用
/attend @photo.jpg course=体育3

# 输出识别结果
# 手动调用 /rollcall 提交
```

**模式3: Hermes + Skill + Plugin（一键）**
```bash
# Hermes 中一键完成
/attend @photo.jpg course=体育3 submit=true

# 自动识别 + 自动提交
```

### 5.2 自然语言交互

```
用户: "拍了一张今天体育课的照片"
     [上传照片]

Hermes: 收到照片，正在识别...

[调用 attend skill]

Hermes: ✅ 识别完成！
        📊 统计结果:
        - 总人数: 37
        - 到课: 35
        - 缺勤: 2
        
        是否提交到教务系统？

用户: "提交"

Hermes: [调用 rollcall plugin]
        ✅ 已提交！37人考勤记录已更新
```

### 5.3 Telegram Bot 场景

```
[Telegram 对话]

老师: /attend @photo1.jpg course=体育3

Bot: 🔄 正在识别...
     ⏳ 预计15秒

     ✅ 识别完成！
     
     📊 考勤统计:
     • 到课: 35人
     • 缺勤: 2人
     • 不确定: 0人
     
     📸 标注图片: [查看]
     📄 详细数据: [下载JSON]
     
     💡 下一步:
     • 直接提交: /rollcall @attendance.json
     • 修改后提交: 编辑JSON再提交

老师: [点击"直接提交"]

Bot: ✅ 已提交！
     🎯 37/37人记录已更新
     📊 提交时间: 08:05
```

---

## 6. 完整工作流

### 6.1 数据流图

```
┌─────────────────────────────────────────┐
│ 用户 (Telegram/CLI/Discord)              │
└──────────────┬──────────────────────────┘
               │
               │ /attend @photo.jpg course=体育3
               ▼
┌──────────────────────────────────────────┐
│ Hermes Agent                              │
│ - 解析命令                                │
│ - 提取参数                                │
│ - 路由到 Skill                            │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ attend Skill Executor                     │
│ - 参数验证                                │
│ - 调用 FaceCall CLI                       │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ FaceCall Core                             │
│ - 人脸检测                                │
│ - 特征提取                                │
│ - 匹配识别                                │
│ - 生成标注图                              │
└──────────────┬───────────────────────────┘
               │
               │ attendance.json
               │ {"students": [...]}
               ▼
┌──────────────────────────────────────────┐
│ attend Skill (决策点)                     │
│ - uncertain > 0? → 需审核                 │
│ - submit=true? → 调用插件                 │
│ - 否则 → 仅返回结果                       │
└──────────────┬───────────────────────────┘
               │
               │ [submit=true]
               ▼
┌──────────────────────────────────────────┐
│ Plugin Manager                            │
│ - 加载 rollcall plugin                    │
│ - 传递数据                                │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ rollcall Plugin                           │
│ - 调用 CUCN Rollcall CLI                  │
│ - 提交到教务系统                          │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ 教务系统 (CUCN/正方)                      │
│ - 接收考勤数据                            │
│ - 写入数据库                              │
│ - 返回结果                                │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ Hermes Agent (汇总结果)                   │
│ - 格式化输出                              │
│ - 发送给用户                              │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ 用户 (收到结果通知)                       │
│ ✅ 识别完成: 35/37人到课                  │
│ ✅ 已提交到教务系统                       │
└──────────────────────────────────────────┘
```

### 6.2 错误处理流

```
任意阶段出错
    ↓
捕获异常
    ↓
回滚操作
    ↓
格式化错误信息
    ↓
返回给用户
    ↓
提供解决建议

示例：
┌────────────────────────────────┐
│ 识别阶段错误                    │
│ - 照片未找到                    │
│ - 人脸检测失败                  │
│ - 数据库不存在                  │
└──────────────┬─────────────────┘
               │
               ▼
        ❌ 识别失败
        💡 建议:
        • 检查照片路径
        • 确认数据库已创建
        • 尝试降低阈值

┌────────────────────────────────┐
│ 提交阶段错误                    │
│ - 登录失败                      │
│ - 课程未找到                    │
│ - 网络超时                      │
└──────────────┬─────────────────┘
               │
               ▼
        ✅ 识别成功
        ❌ 提交失败: 登录超时
        💡 建议:
        • 检查网络连接
        • 稍后重试
        • 或手动提交: /rollcall @attendance.json
```

---

## 7. 实施计划

### Phase 1: 基础集成（1-2天）

```bash
# 1. 创建目录结构
mkdir -p hermes_integration/{skills/attend,plugins/rollcall,docs}

# 2. 实现 attend skill
- executor.py
- SKILL.md
- config.yaml

# 3. 实现 rollcall plugin
- plugin.py
- config.yaml

# 4. 测试
./test_hermes_integration.sh
```

### Phase 2: 插件机制（2-3天）

```bash
# 1. 实现 PluginManager
src/facecall/core/plugin_manager.py

# 2. 定义 Plugin 协议
src/facecall/core/plugin.py

# 3. 配置系统
config/plugins.yaml

# 4. 测试插件加载
pytest tests/test_plugin_manager.py
```

### Phase 3: 完善体验（1-2天）

```bash
# 1. 错误处理
- 友好的错误提示
- 自动重试机制

# 2. 进度反馈
- 识别进度
- 提交进度

# 3. 结果格式化
- Markdown 输出
- 图表可视化
```

### Phase 4: 文档与测试（1天）

```bash
# 1. 完善文档
docs/HERMES_INTEGRATION.md
docs/PLUGIN_DEVELOPMENT.md

# 2. 集成测试
tests/integration/test_hermes_flow.py

# 3. 用户指南
examples/hermes_usage.md
```

---

## 8. 总结

### 推荐接入方式

**🏆 插件式集成（方案C）**

**核心理念**:
- Skill 专注人脸识别（核心功能）
- Plugin 扩展其他能力（提交、通知等）
- 用户可控（启用/禁用插件）

**技术栈**:
```
Hermes Agent
    ↓
attend Skill (Python)
    ↓
FaceCall Core (Python)
    ↓ [Plugin Hook]
rollcall Plugin (Python)
    ↓
CUCN Rollcall CLI (Python)
    ↓
教务系统 API (HTTP)
```

**优势**:
1. ✅ 解耦清晰，易于维护
2. ✅ 灵活可控，用户决策
3. ✅ 渐进增强，逐步完善
4. ✅ 可扩展性强，插件生态

**用户体验**:
```bash
# 最简单
/attend @photo.jpg course=体育3

# 一键完成
/attend @photo.jpg course=体育3 submit=true

# 自然语言
"识别今天体育课的考勤"
```

---

**文档撰写时间**: 2026-10-20  
**作者**: Claude Fable 5.1  
**版本**: 1.0
