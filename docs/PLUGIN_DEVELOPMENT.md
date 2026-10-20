# 🔌 插件开发指南

本指南帮助你开发 FaceCall 插件，扩展系统功能。

---

## 📖 目录

- [插件架构](#插件架构)
- [快速开始](#快速开始)
- [插件协议](#插件协议)
- [开发步骤](#开发步骤)
- [最佳实践](#最佳实践)
- [测试](#测试)
- [发布](#发布)

---

## 插件架构

### 核心概念

```
PluginManager (插件管理器)
    ↓
Plugin Protocol (插件协议)
    ↓
具体插件实现
    ├─ rollcall (考勤提交)
    ├─ notification (通知推送)
    └─ analytics (数据分析)
```

### 插件生命周期

```
1. 注册 → PluginManager 加载配置
2. 验证 → 检查插件实现是否符合协议
3. 执行 → 调用插件的 execute() 方法
4. 清理 → 插件自行管理资源
```

---

## 快速开始

### 1. 创建插件目录

```bash
mkdir -p hermes_integration/plugins/your_plugin
cd hermes_integration/plugins/your_plugin
touch __init__.py plugin.py README.md
```

### 2. 实现插件

```python
# plugin.py
from typing import Dict, Any

class Plugin:
    """你的插件实现"""
    
    name: str = "your_plugin"
    version: str = "1.0.0"
    
    def __init__(self, config: Dict[str, Any]):
        """初始化插件
        
        Args:
            config: 插件配置字典
        """
        self.config = config
        # 初始化资源
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行插件功能
        
        Args:
            data: 输入数据
            
        Returns:
            执行结果
        """
        # 1. 验证数据
        if not self.validate(data):
            return {"success": False, "error": "数据验证失败"}
        
        # 2. 执行逻辑
        try:
            result = self._process(data)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """验证输入数据
        
        Args:
            data: 待验证数据
            
        Returns:
            是否有效
        """
        required_fields = ["field1", "field2"]
        return all(field in data for field in required_fields)
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息
        
        Returns:
            插件元数据
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": "插件描述",
            "author": "作者名",
            "required_fields": ["field1", "field2"],
            "optional_fields": ["field3"]
        }
    
    def _process(self, data: Dict[str, Any]) -> Any:
        """实际处理逻辑（内部方法）"""
        # 实现你的逻辑
        pass
```

### 3. 注册插件

```yaml
# config/config.yaml
plugins:
  your_plugin:
    enabled: true
    module_path: "hermes_integration.plugins.your_plugin.plugin"
    config:
      # 插件特定配置
      key1: value1
      key2: value2
```

### 4. 测试插件

```python
# tests/test_your_plugin.py
import pytest
from hermes_integration.plugins.your_plugin.plugin import Plugin

def test_plugin_info():
    """测试插件信息"""
    plugin = Plugin({})
    info = plugin.get_info()
    assert info["name"] == "your_plugin"
    assert info["version"] == "1.0.0"

def test_plugin_validation():
    """测试数据验证"""
    plugin = Plugin({})
    
    # 有效数据
    valid_data = {"field1": "value1", "field2": "value2"}
    assert plugin.validate(valid_data)
    
    # 无效数据
    invalid_data = {"field1": "value1"}
    assert not plugin.validate(invalid_data)

def test_plugin_execute():
    """测试执行"""
    plugin = Plugin({"key1": "value1"})
    
    data = {"field1": "value1", "field2": "value2"}
    result = plugin.execute(data)
    
    assert result["success"]
    assert "data" in result
```

---

## 插件协议

### Protocol 定义

```python
# src/facecall/core/plugin.py
from typing import Protocol, Dict, Any

class Plugin(Protocol):
    """插件协议
    
    所有插件必须实现这个协议的所有方法。
    """
    
    name: str
    """插件名称（必须唯一）"""
    
    version: str
    """插件版本（语义化版本）"""
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行插件功能
        
        Args:
            data: 输入数据字典
            
        Returns:
            结果字典，至少包含 'success' 字段
            成功: {"success": True, "data": ...}
            失败: {"success": False, "error": "..."}
        """
        ...
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """验证输入数据
        
        Args:
            data: 待验证的数据
            
        Returns:
            True 如果数据有效，False 否则
        """
        ...
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息
        
        Returns:
            插件元数据，包含:
            - name: 插件名
            - version: 版本
            - description: 描述
            - author: 作者
            - required_fields: 必需字段列表
            - optional_fields: 可选字段列表（可选）
        """
        ...
```

### 标准返回格式

#### 成功

```python
{
    "success": True,
    "data": {
        # 插件返回的数据
    },
    "message": "执行成功"  # 可选
}
```

#### 失败

```python
{
    "success": False,
    "error": "错误描述",
    "details": {  # 可选
        # 详细错误信息
    }
}
```

---

## 开发步骤

### Step 1: 设计插件

**明确目标**：
- 插件要解决什么问题？
- 输入是什么？
- 输出是什么？
- 依赖什么外部资源？

**示例：notification 插件**
```
目标: 发送考勤通知给学生
输入: {"students": [...], "course": "..."}
输出: {"success": True, "sent": 35}
依赖: 邮件服务器/短信API/Telegram Bot
```

### Step 2: 创建文件结构

```bash
hermes_integration/plugins/notification/
├── __init__.py          # 包初始化
├── plugin.py            # 插件实现
├── README.md            # 插件文档
└── config_example.yaml  # 配置示例
```

### Step 3: 实现核心逻辑

```python
# plugin.py
import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any, List

class Plugin:
    name = "notification"
    version = "1.0.0"
    
    def __init__(self, config: Dict[str, Any]):
        self.smtp_server = config.get("smtp_server")
        self.smtp_port = config.get("smtp_port", 587)
        self.username = config.get("username")
        self.password = config.get("password")
        self.from_email = config.get("from_email")
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate(data):
            return {"success": False, "error": "无效数据"}
        
        students = data["students"]
        course = data["course"]
        
        sent_count = 0
        failed = []
        
        for student in students:
            try:
                self._send_email(student, course)
                sent_count += 1
            except Exception as e:
                failed.append({
                    "student": student["xh"],
                    "error": str(e)
                })
        
        return {
            "success": len(failed) == 0,
            "sent": sent_count,
            "failed": failed
        }
    
    def validate(self, data: Dict[str, Any]) -> bool:
        return (
            "students" in data and
            isinstance(data["students"], list) and
            "course" in data
        )
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": "发送考勤通知给学生",
            "author": "你的名字",
            "required_fields": ["students", "course"],
            "optional_fields": ["template"]
        }
    
    def _send_email(self, student: Dict[str, Any], course: str):
        """发送单个邮件"""
        email = student.get("email")
        if not email:
            raise ValueError("学生无邮箱")
        
        status = student["category"]
        body = f"你在{course}课程的考勤状态: {status}"
        
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = f"考勤通知 - {course}"
        msg["From"] = self.from_email
        msg["To"] = email
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
```

### Step 4: 编写测试

```python
# tests/test_notification_plugin.py
import pytest
from unittest.mock import Mock, patch
from hermes_integration.plugins.notification.plugin import Plugin

@pytest.fixture
def plugin():
    config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "username": "user@example.com",
        "password": "password",
        "from_email": "noreply@example.com"
    }
    return Plugin(config)

def test_plugin_info(plugin):
    info = plugin.get_info()
    assert info["name"] == "notification"
    assert "students" in info["required_fields"]

def test_validate(plugin):
    # 有效
    valid = {
        "students": [{"xh": "001", "email": "s@ex.com"}],
        "course": "体育3"
    }
    assert plugin.validate(valid)
    
    # 无效 - 缺少 students
    invalid = {"course": "体育3"}
    assert not plugin.validate(invalid)

@patch("smtplib.SMTP")
def test_execute_success(mock_smtp, plugin):
    """测试成功发送"""
    data = {
        "students": [
            {"xh": "001", "email": "s1@ex.com", "category": "正常"},
            {"xh": "002", "email": "s2@ex.com", "category": "正常"}
        ],
        "course": "体育3"
    }
    
    result = plugin.execute(data)
    
    assert result["success"]
    assert result["sent"] == 2
    assert len(result["failed"]) == 0

def test_execute_partial_failure(plugin):
    """测试部分失败"""
    data = {
        "students": [
            {"xh": "001", "category": "正常"},  # 无邮箱
            {"xh": "002", "email": "s2@ex.com", "category": "正常"}
        ],
        "course": "体育3"
    }
    
    result = plugin.execute(data)
    
    assert not result["success"]
    assert len(result["failed"]) == 1
```

### Step 5: 编写文档

```markdown
# Notification 插件

## 功能

发送考勤通知给学生。

## 配置

```yaml
plugins:
  notification:
    enabled: true
    module_path: "hermes_integration.plugins.notification.plugin"
    config:
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "your@gmail.com"
      password: "your_password"
      from_email: "noreply@example.com"
```

## 使用

```python
manager = PluginManager("config.yaml")
result = manager.execute_plugin("notification", {
    "students": [...],
    "course": "体育3"
})
```

## 依赖

- smtplib (标准库)
- email (标准库)
```

---

## 最佳实践

### 1. 单一职责

每个插件只做一件事，做好这一件事。

```python
# ✅ 好 - 职责单一
class NotificationPlugin:
    """发送通知"""
    def execute(self, data):
        return self._send_notifications(data)

# ❌ 差 - 职责混乱
class MegaPlugin:
    """发送通知 + 生成报表 + 备份数据"""
    def execute(self, data):
        self._send_notifications(data)
        self._generate_report(data)
        self._backup_data(data)
```

### 2. 错误处理

```python
def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # 1. 验证
        if not self.validate(data):
            return {
                "success": False,
                "error": "数据验证失败",
                "details": {"missing": self._find_missing(data)}
            }
        
        # 2. 执行
        result = self._process(data)
        
        # 3. 返回
        return {"success": True, "data": result}
        
    except ValueError as e:
        # 数据错误
        return {"success": False, "error": f"数据错误: {e}"}
    except ConnectionError as e:
        # 网络错误
        return {"success": False, "error": f"连接失败: {e}"}
    except Exception as e:
        # 未知错误
        return {"success": False, "error": f"未知错误: {e}"}
```

### 3. 配置验证

```python
def __init__(self, config: Dict[str, Any]):
    # 验证必需配置
    required = ["api_key", "endpoint"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"缺少配置: {', '.join(missing)}")
    
    self.api_key = config["api_key"]
    self.endpoint = config["endpoint"]
    self.timeout = config.get("timeout", 30)  # 默认值
```

### 4. 资源清理

```python
class Plugin:
    def __init__(self, config):
        self.connection = self._create_connection(config)
    
    def execute(self, data):
        try:
            return self._process(data)
        finally:
            # 确保资源释放
            self._cleanup()
    
    def _cleanup(self):
        if hasattr(self, "connection") and self.connection:
            self.connection.close()
```

### 5. 日志记录

```python
import logging

logger = logging.getLogger(__name__)

class Plugin:
    def execute(self, data):
        logger.info(f"开始执行插件: {self.name}")
        
        try:
            result = self._process(data)
            logger.info(f"插件执行成功: {result}")
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"插件执行失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
```

---

## 测试

### 单元测试

```bash
# 测试单个插件
pytest tests/test_your_plugin.py -v

# 测试覆盖率
pytest tests/test_your_plugin.py --cov=hermes_integration/plugins/your_plugin
```

### 集成测试

```python
def test_plugin_integration():
    """测试插件与系统集成"""
    # 1. 加载插件管理器
    manager = PluginManager("config.yaml")
    
    # 2. 验证插件已加载
    plugins = manager.list_plugins()
    assert "your_plugin" in plugins
    
    # 3. 执行插件
    result = manager.execute_plugin("your_plugin", test_data)
    
    # 4. 验证结果
    assert result["success"]
```

---

## 发布

### 1. 准备发布

```bash
# 运行测试
pytest tests/test_your_plugin.py -v

# 检查代码风格
black hermes_integration/plugins/your_plugin/
ruff check hermes_integration/plugins/your_plugin/

# 更新文档
vim hermes_integration/plugins/your_plugin/README.md
```

### 2. 提交代码

```bash
git add hermes_integration/plugins/your_plugin/
git commit -m "feat: add your_plugin for XYZ functionality"
git push
```

### 3. 创建 Pull Request

- 标题: `feat: add your_plugin`
- 描述: 插件功能、使用场景、测试情况
- 标签: `plugin`, `enhancement`

---

## 示例插件

参考现有插件实现：

- [rollcall](../hermes_integration/plugins/rollcall/) - 考勤提交
- 更多插件陆续添加...

---

## 获取帮助

- GitHub Issues: 提问和讨论
- 项目文档: [docs/INDEX.md](INDEX.md)
- 贡献指南: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**更新时间**: 2026-10-20  
**维护者**: scfmac
