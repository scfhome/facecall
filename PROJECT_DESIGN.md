# 🎯 点到 FaceCall - 项目设计文档

## 📋 项目概述

**项目名称**: 点到 FaceCall (智能考勤系统)

**核心理念**: 
将 `classroom-face-attendance`（人脸识别）和 `zfsoft-rollcall-cli`（教务系统提交）**深度融合**为一个统一的智能考勤解决方案。

**与原有项目的区别**:

| 维度 | 原有方案 | 新项目方案 |
|------|---------|----------|
| **架构** | 两个独立项目，JSON文件中转 | 统一项目，内存数据流 |
| **用户体验** | 两条命令，手动传递文件 | 一条命令，全自动 |
| **依赖管理** | 两套venv，可能冲突 | 统一依赖，版本协调 |
| **代码复用** | 无共享 | 共享模型、工具类 |
| **配置** | 两份配置文件 | 统一配置管理 |
| **部署** | 分别部署 | 一键部署 |

---

## 🏗️ 架构设计

### 整体架构

```
facecall-system/
│
├─ src/facecall/
│  ├─ __init__.py
│  │
│  ├─ face/                    # 人脸识别模块（来自 classroom-face-attendance）
│  │  ├─ __init__.py
│  │  ├─ detector.py           # 人脸检测
│  │  ├─ recognizer.py         # 人脸识别
│  │  ├─ database.py           # 人脸数据库
│  │  └─ models.py             # 数据模型
│  │
│  ├─ rollcall/                # 教务系统模块（来自 zfsoft-rollcall-cli）
│  │  ├─ __init__.py
│  │  ├─ client.py             # 正方系统客户端
│  │  ├─ crypto.py             # RSA加密
│  │  └─ models.py             # 考勤数据模型
│  │
│  ├─ core/                    # 核心业务逻辑（新增）
│  │  ├─ __init__.py
│  │  ├─ workflow.py           # 统一工作流
│  │  ├─ pipeline.py           # 数据管道（识别→提交）
│  │  └─ exceptions.py         # 统一异常
│  │
│  ├─ config/                  # 配置管理（新增）
│  │  ├─ __init__.py
│  │  ├─ settings.py           # 统一配置
│  │  └─ validator.py          # 配置验证
│  │
│  └─ utils/                   # 工具模块（新增）
│     ├─ __init__.py
│     ├─ logger.py             # 统一日志
│     └─ image.py              # 图像处理
│
├─ scripts/                    # 命令行脚本
│  ├─ attend.py                # 一键考勤（核心）
│  ├─ build_db.py              # 建立人脸库
│  ├─ list_courses.py          # 查询课程
│  └─ review.py                # 审核识别结果
│
├─ config/                     # 配置文件
│  ├─ config.yaml              # 主配置
│  └─ classes.yaml             # 班级配置
│
├─ tests/                      # 测试
│  ├─ test_face/
│  ├─ test_rollcall/
│  └─ test_integration/
│
├─ docs/                       # 文档
│  ├─ QUICKSTART.md
│  ├─ ARCHITECTURE.md
│  └─ DEPLOYMENT.md
│
├─ .claude/skills/             # Claude Code Skill
│  └─ facecall.md
│
├─ requirements.txt            # 统一依赖
├─ pyproject.toml
├─ README.md
└─ .env.example

```

### 数据流设计

```
用户输入: 课堂照片
    ↓
┌─────────────────────────────────┐
│  Pipeline: AttendanceWorkflow   │
│                                 │
│  Stage 1: 人脸识别               │
│  ├─ 加载照片                    │
│  ├─ 检测人脸                    │
│  ├─ 提取特征                    │
│  └─ 匹配学生                    │
│      ↓                          │
│  AttendanceRecord (内存对象)     │
│  {students: [...], summary}     │
│      ↓                          │
│  Stage 2: 人工确认 (可选)        │
│  ├─ 生成标注图                  │
│  ├─ 检测不确定项                │
│  └─ 用户确认/修正               │
│      ↓                          │
│  Stage 3: 提交教务系统           │
│  ├─ RSA加密登录                 │
│  ├─ 查询课程                    │
│  ├─ 提交考勤                    │
│  └─ 返回结果                    │
│      ↓                          │
│  Result                         │
│  {success, submitted, duration}  │
└─────────────────────────────────┘
```

---

## 💻 核心代码设计

### 1. 统一工作流 (workflow.py)

```python
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

@dataclass(frozen=True)
class AttendanceConfig:
    """统一配置"""
    photo_path: Path
    database_path: Path
    roster_path: Path
    course_name: str
    date: str
    threshold: float = 0.70
    auto_submit: bool = True
    review_uncertain: bool = True
    
@dataclass(frozen=True)
class AttendanceResult:
    """考勤结果"""
    success: bool
    total: int
    submitted: int
    uncertain: int
    absent: int
    duration: float
    message: str
    annotated_image: Optional[Path] = None

class AttendanceWorkflow:
    """统一考勤工作流"""
    
    def __init__(self, config: AttendanceConfig):
        self.config = config
        self.face_recognizer = FaceRecognizer(...)
        self.rollcall_client = RollCallClient(...)
        
    def execute(self) -> AttendanceResult:
        """执行完整工作流"""
        # Stage 1: 人脸识别
        recognition_result = self._recognize_faces()
        
        # Stage 2: 人工确认（如果需要）
        if self.config.review_uncertain and recognition_result.has_uncertain():
            confirmed_result = self._review_uncertain(recognition_result)
        else:
            confirmed_result = recognition_result
            
        # Stage 3: 提交教务系统
        if self.config.auto_submit:
            submit_result = self._submit_to_system(confirmed_result)
        else:
            submit_result = None
            
        return self._build_result(
            recognition_result,
            confirmed_result,
            submit_result
        )
    
    def _recognize_faces(self) -> RecognitionResult:
        """人脸识别"""
        ...
    
    def _review_uncertain(self, result: RecognitionResult) -> RecognitionResult:
        """人工审核不确定项"""
        ...
    
    def _submit_to_system(self, result: RecognitionResult) -> SubmitResult:
        """提交到教务系统"""
        ...
```

### 2. 一键命令 (scripts/attend.py)

```python
#!/usr/bin/env python3
"""
一键考勤脚本

用法:
    python scripts/attend.py --photo class.jpg --course "体育3"
    python scripts/attend.py --photo class.jpg --course "体育3" --no-submit  # 仅识别
    python scripts/attend.py --photo class.jpg --course "体育3" --no-review  # 跳过审核
"""

import sys
from pathlib import Path
from facecall.core.workflow import AttendanceWorkflow, AttendanceConfig
from facecall.utils.logger import get_logger

logger = get_logger(__name__)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="一键智能考勤")
    
    # 必选参数
    parser.add_argument("--photo", required=True, help="课堂照片路径")
    parser.add_argument("--course", required=True, help="课程名称")
    
    # 可选参数
    parser.add_argument("--date", default="today", help="考勤日期 (today/2024-10-20)")
    parser.add_argument("--database", help="人脸数据库路径（自动从配置查找）")
    parser.add_argument("--roster", help="班级名单路径（自动从配置查找）")
    parser.add_argument("--threshold", type=float, default=0.70, help="识别阈值")
    
    # 流程控制
    parser.add_argument("--no-submit", action="store_true", help="仅识别，不提交")
    parser.add_argument("--no-review", action="store_true", help="跳过人工审核")
    parser.add_argument("--output", help="保存识别结果的JSON路径")
    
    args = parser.parse_args()
    
    # 构建配置
    config = AttendanceConfig(
        photo_path=Path(args.photo),
        database_path=Path(args.database) if args.database else _find_database(args.course),
        roster_path=Path(args.roster) if args.roster else _find_roster(args.course),
        course_name=args.course,
        date=args.date,
        threshold=args.threshold,
        auto_submit=not args.no_submit,
        review_uncertain=not args.no_review,
    )
    
    # 执行工作流
    logger.info(f"开始考勤: {args.course} ({args.date})")
    
    workflow = AttendanceWorkflow(config)
    result = workflow.execute()
    
    # 输出结果
    if result.success:
        logger.info(f"✅ 考勤完成: {result.submitted}/{result.total} 人")
        logger.info(f"⏱️  耗时: {result.duration:.1f}秒")
        if result.uncertain > 0:
            logger.warning(f"⚠️  不确定: {result.uncertain} 人")
    else:
        logger.error(f"❌ 考勤失败: {result.message}")
        sys.exit(1)
    
    # 保存JSON（如果指定）
    if args.output:
        _save_json(result, args.output)
        logger.info(f"📄 结果已保存: {args.output}")
    
    return 0 if result.success else 1

def _find_database(course: str) -> Path:
    """从配置文件自动查找数据库"""
    from facecall.config import load_config
    config = load_config()
    return config.get_database_for_course(course)

def _find_roster(course: str) -> Path:
    """从配置文件自动查找名单"""
    from facecall.config import load_config
    config = load_config()
    return config.get_roster_for_course(course)

def _save_json(result: AttendanceResult, output_path: str):
    """保存结果为JSON"""
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    sys.exit(main())
```

---

## 🎨 用户体验设计

### 命令对比

**原有方案（两条命令）**:
```bash
# 步骤1: 人脸识别
python face-attendance-cli/scripts/check_attendance.py \
  --photo class.jpg \
  --database face_db.pkl \
  --roster students.xlsx \
  --output temp.json

# 步骤2: 提交系统
python zfsoft-rollcall-cli/scripts/rollcall_auto.py \
  --date today \
  --course "体育3" \
  --input temp.json
```

**新方案（一条命令）**:
```bash
# 一键完成
python scripts/attend.py --photo class.jpg --course "体育3"
```

### Claude Code Skill 集成

```markdown
# .claude/skills/facecall.md

## 功能描述
智能考勤系统，人脸识别+自动提交。

## 触发词
- "考勤" / "点名" / "识别并提交"
- "attend" / "attendance"

## 参数提取
从用户输入中提取：
1. 照片路径（必需）
   - 文件引用: @photo.jpg
   - 智能识别: "识别 photo.jpg"
   
2. 课程名称（必需）
   - 直接提及: "体育3"
   - 模糊匹配: "体育" → 列出选项

3. 日期（可选，默认今天）
   - "今天" → today
   - "昨天" → yesterday
   - "2024-10-20" → 2024-10-20

## 执行流程
1. 检查参数完整性
2. 从配置查找数据库和名单
3. 执行 `python scripts/attend.py ...`
4. 解析输出，格式化展示
5. 如有不确定项，询问用户

## 示例

**用户**: 识别 @class_photo.jpg 体育3

**执行**:
```bash
python scripts/attend.py \
  --photo class_photo.jpg \
  --course "体育3" \
  --date today
```

**输出格式**:
```
✅ 考勤完成

📊 统计:
- 总人数: 37
- 已提交: 35
- 不确定: 2
  - 20230015 张三 (相似度: 0.72)
  - 20230028 李四 (相似度: 0.68)

⏱️ 耗时: 18.3秒

🎯 是否确认提交不确定项？
```
```

---

## 📦 依赖管理

### requirements.txt (统一依赖)

```txt
# 人脸识别核心
deepface==0.0.87
opencv-python==4.9.0.80
tensorflow==2.15.0
pillow==10.2.0

# 教务系统交互
requests==2.31.0
pycryptodome==3.20.0
beautifulsoup4==4.12.3

# 数据处理
pandas==2.2.0
openpyxl==3.1.2
numpy==1.26.3

# 配置管理
pyyaml==6.0.1
python-dotenv==1.0.1
pydantic==2.6.1

# 日志和工具
rich==13.7.0
click==8.1.7

# 开发依赖（requirements-dev.txt）
pytest==7.4.4
pytest-cov==4.1.0
black==24.1.1
ruff==0.1.15
mypy==1.8.0
```

---

## 🚀 实施计划

### Phase 1: 基础融合（1周）
- [ ] 创建项目结构
- [ ] 迁移人脸识别模块（from classroom-face-attendance）
- [ ] 迁移教务系统模块（from zfsoft-rollcall-cli）
- [ ] 实现 `AttendanceWorkflow` 核心类
- [ ] 实现 `scripts/attend.py` 一键脚本
- [ ] 统一配置管理
- [ ] 基础测试

### Phase 2: 体验优化（1周）
- [ ] Claude Code Skill 集成
- [ ] Rich终端UI（进度条、彩色输出）
- [ ] 交互式审核（不确定项确认）
- [ ] 配置向导（首次使用）
- [ ] 错误处理和友好提示
- [ ] 完善文档

### Phase 3: 高级特性（1-2周）
- [ ] 批量处理（多门课程）
- [ ] 数据库自动更新（增量学习）
- [ ] 考勤报表生成
- [ ] Web UI（可选）
- [ ] 性能优化（GPU加速）
- [ ] Docker部署

---

## 🎯 核心优势

### 与原有方案对比

| 维度 | 原方案 | 新方案 | 提升 |
|------|--------|--------|------|
| **命令数** | 2条 | 1条 | 简化50% |
| **配置文件** | 2份 | 1份 | 统一管理 |
| **中间文件** | JSON文件 | 内存传递 | 无文件残留 |
| **依赖冲突** | 可能 | 协调处理 | 更稳定 |
| **用户体验** | 需理解两个工具 | 一个工具 | 学习成本低 |
| **扩展性** | 独立演进 | 统一演进 | 一致性高 |
| **AI集成** | 需调用两个 | 一次调用 | Agent友好 |

---

## 📝 配置文件设计

### config/config.yaml

```yaml
# 智能考勤系统配置

# 教务系统配置
zfsoft:
  base_url: "https://jw.school.edu.cn"
  username: "${ZFSOFT_USERNAME}"  # 从环境变量读取
  password: "${ZFSOFT_PASSWORD}"

# 人脸识别配置
face_recognition:
  model: "Facenet512"
  detector: "retinaface"
  threshold: 0.70
  uncertain_range: [0.70, 0.85]

# 班级配置（引用独立文件）
classes_config: "config/classes.yaml"

# 日志配置
logging:
  level: "INFO"
  format: "rich"  # rich / simple / json
  file: "logs/attendance.log"

# 性能配置
performance:
  use_gpu: true
  batch_size: 16
```

### config/classes.yaml

```yaml
# 班级配置

classes:
  - class_id: "001"
    class_name: "234拓展女-1"
    courses:
      - name: "体育3"
        database: "databases/体育3_001班.pkl"
        roster: "rosters/001班.xlsx"
      - name: "高等数学"
        database: "databases/高数_001班.pkl"
        roster: "rosters/001班.xlsx"
        
  - class_id: "002"
    class_name: "计算机2班"
    courses:
      - name: "Python编程"
        database: "databases/Python_002班.pkl"
        roster: "rosters/002班.xlsx"
```

---

## 🔄 迁移指南

### 从原有项目迁移

```bash
# 1. 创建新项目
cd /path/to
git clone https://github.com/YOU/facecall-system.git
cd facecall-system

# 2. 迁移人脸数据库
cp /path/to/classroom-face-attendance/databases/*.pkl databases/

# 3. 迁移名单
cp /path/to/classroom-face-attendance/rosters/*.xlsx rosters/

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入教务系统账号密码

# 5. 配置班级
vim config/classes.yaml

# 6. 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 7. 测试
python scripts/attend.py --photo test.jpg --course "体育3" --no-submit
```

---

## 📚 文档结构

```
docs/
├── QUICKSTART.md          # 快速开始（5分钟上手）
├── ARCHITECTURE.md        # 架构文档（技术细节）
├── USER_GUIDE.md          # 用户指南（完整功能）
├── ADMIN_GUIDE.md         # 管理员指南（部署配置）
├── API.md                 # Python API文档
├── TROUBLESHOOTING.md     # 故障排查
└── MIGRATION.md           # 从原项目迁移
```

---

## 🎉 总结

**点到 FaceCall** 是原有两个项目的**深度融合**，不仅仅是简单的调用关系，而是：

1. **统一架构** - 单一代码仓库，模块化设计
2. **统一体验** - 一条命令完成所有操作
3. **统一配置** - 一份配置文件管理所有设置
4. **统一依赖** - 协调处理依赖冲突
5. **统一演进** - 功能同步迭代

**核心价值**:
- 🚀 更快：一条命令，15-20秒完成
- 🎯 更准：95%+准确率，可人工审核
- 🔒 更安全：本地识别，隐私保护
- 🤖 更智能：AI Agent深度集成
- 📦 更易用：统一管理，学习成本低

---

**下一步**: 开始实施 Phase 1 基础融合
