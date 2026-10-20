# 贡献指南

感谢你对 FaceCall 项目的关注！我们欢迎任何形式的贡献。

---

## 🎯 贡献方式

### 1. 报告 Bug
- 使用 GitHub Issues 提交 Bug
- 提供详细的复现步骤
- 包含错误信息和环境信息

### 2. 建议新功能
- 使用 GitHub Issues 标记为 `enhancement`
- 说明功能的使用场景和价值
- 提供伪代码或设计草图（可选）

### 3. 提交代码
- Fork 项目到你的账户
- 创建特性分支
- 提交代码并推送
- 创建 Pull Request

### 4. 改进文档
- 修正错误
- 补充示例
- 翻译文档

---

## 📋 开发规范

### 代码规范

#### Python 代码
- 遵循 PEP 8 编码规范
- 使用类型注解
- 保持函数简洁（< 50 行）
- 使用不可变数据结构（`@dataclass(frozen=True)`）

```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class Student:
    """学生信息（不可变）"""
    xh: str  # 学号
    name: str  # 姓名
    
    def __post_init__(self):
        """验证数据"""
        if not self.xh:
            raise ValueError("学号不能为空")
```

#### 文件组织
- 多个小文件优于少数大文件
- 按功能组织，不按类型
- 每个文件单一职责

#### 错误处理
- 每层显式处理错误
- 不要静默吞错
- 提供友好的错误消息

```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"数据验证失败: {e}")
    raise ProcessError(f"无法处理数据: {e}") from e
```

### 命名规范

- **变量**: `snake_case`
- **常量**: `UPPER_SNAKE_CASE`
- **类**: `PascalCase`
- **函数**: `snake_case`
- **私有成员**: `_leading_underscore`

### 文档规范

#### Docstring
所有公开函数和类必须有文档字符串：

```python
def recognize_faces(photo_path: str, threshold: float = 0.70) -> List[Student]:
    """识别照片中的人脸
    
    Args:
        photo_path: 照片文件路径
        threshold: 匹配阈值，默认 0.70
        
    Returns:
        识别到的学生列表
        
    Raises:
        FileNotFoundError: 照片文件不存在
        ValueError: 阈值超出范围 [0, 1]
        
    Example:
        >>> students = recognize_faces("class.jpg", threshold=0.75)
        >>> print(f"识别到 {len(students)} 人")
    """
    ...
```

#### Markdown 文档
- 使用清晰的标题层次
- 提供代码示例
- 包含实际使用场景
- 保持简洁

---

## 🧪 测试规范

### 单元测试
- 使用 `pytest`
- 测试覆盖率 > 80%
- 测试文件命名: `test_*.py`

```python
import pytest
from facecall.core.plugin_manager import PluginManager

def test_plugin_manager_load():
    """测试插件管理器加载"""
    manager = PluginManager("config.yaml")
    plugins = manager.list_plugins()
    assert "rollcall" in plugins
    
def test_plugin_validation():
    """测试插件数据验证"""
    plugin = manager.get_plugin("rollcall")
    
    # 有效数据
    assert plugin.validate({"students": [], "course": "体育3"})
    
    # 无效数据
    assert not plugin.validate({"course": "体育3"})  # 缺少 students
```

### 集成测试
```python
def test_full_workflow():
    """测试完整工作流"""
    # 1. 识别人脸
    result = recognize_faces("test.jpg")
    assert len(result) > 0
    
    # 2. 调用插件提交
    plugin_result = manager.execute_plugin("rollcall", {
        "students": result,
        "course": "体育3"
    })
    assert plugin_result["success"]
```

### 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_rollcall_plugin.py -v

# 测试覆盖率
pytest --cov=src/facecall tests/

# 生成 HTML 报告
pytest --cov=src/facecall --cov-report=html tests/
```

---

## 🔄 提交流程

### 1. Fork 项目
```bash
# 在 GitHub 上点击 Fork 按钮
# 克隆你的 Fork
git clone https://github.com/YOUR_USERNAME/facecall.git
cd facecall
```

### 2. 创建分支
```bash
# 创建特性分支
git checkout -b feature/your-feature-name

# 或修复分支
git checkout -b fix/issue-123
```

### 3. 开发
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 编写代码
# 编写测试
# 运行测试
pytest tests/ -v

# 格式化代码
black src/ tests/
isort src/ tests/
ruff check src/ tests/
```

### 4. 提交
```bash
# 添加文件
git add .

# 提交（使用规范的提交信息）
git commit -m "feat: add new feature"
```

### 5. 推送
```bash
git push origin feature/your-feature-name
```

### 6. 创建 Pull Request
- 访问你的 Fork 页面
- 点击 "New Pull Request"
- 填写 PR 描述
- 等待审核

---

## 📝 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>: <description>

[optional body]

[optional footer]
```

### Type 类型
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具链更新
- `perf`: 性能优化
- `ci`: CI/CD 配置

### 示例
```bash
# 新功能
git commit -m "feat: add rollcall plugin for auto-submission"

# Bug 修复
git commit -m "fix: handle timeout error in plugin execution"

# 文档
git commit -m "docs: update QUICKSTART with installation steps"

# 重构
git commit -m "refactor: extract plugin validation logic"
```

---

## 🔍 Code Review 标准

### PR 审核重点
- [ ] 代码符合规范
- [ ] 有充分的测试
- [ ] 文档已更新
- [ ] 无安全问题
- [ ] 性能无明显下降
- [ ] 提交信息规范

### 审核流程
1. 自动化检查（CI）
2. 代码审核（Reviewer）
3. 测试验证
4. 合并

---

## 🎨 插件开发

### 插件协议
```python
from typing import Protocol

class Plugin(Protocol):
    """插件协议"""
    name: str
    version: str
    
    def execute(self, data: dict) -> dict:
        """执行插件"""
        ...
    
    def validate(self, data: dict) -> bool:
        """验证输入数据"""
        ...
    
    def get_info(self) -> dict:
        """获取插件信息"""
        ...
```

### 开发步骤
1. 创建插件目录 `plugins/your_plugin/`
2. 实现 `plugin.py`
3. 编写测试 `tests/test_your_plugin.py`
4. 更新配置 `config/config.yaml`
5. 编写文档 `plugins/your_plugin/README.md`

### 示例插件
参考 `hermes_integration/plugins/rollcall/` 的实现。

---

## 🐛 调试技巧

### 日志
```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

### 断点调试
```python
# 使用 pdb
import pdb; pdb.set_trace()

# 或使用 breakpoint() (Python 3.7+)
breakpoint()
```

---

## 📚 资源

### 项目文档
- [README](README.md) - 项目概述
- [PROJECT_DESIGN](PROJECT_DESIGN.md) - 架构设计
- [HERMES_INTEGRATION](docs/HERMES_INTEGRATION.md) - Hermes 集成

### 外部资源
- [PEP 8](https://pep8.org/) - Python 编码规范
- [pytest](https://docs.pytest.org/) - 测试框架
- [DeepFace](https://github.com/serengil/deepface) - 人脸识别库

---

## ❓ 获取帮助

### 问题讨论
- GitHub Issues: 报告 Bug 和功能建议
- GitHub Discussions: 一般性讨论

### 联系方式
- 项目维护者: scfmac
- GitHub: [@scfhome](https://github.com/scfhome)

---

## 📜 行为准则

### 基本原则
- 尊重他人
- 保持友好
- 开放包容
- 专注技术

### 不可接受的行为
- 骚扰或侮辱
- 恶意攻击
- 泄露隐私
- 其他不专业行为

---

再次感谢你的贡献！🎉

---

**更新时间**: 2026-10-20  
**维护者**: scfmac
