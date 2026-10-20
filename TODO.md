# 📝 点到 FaceCall - 下一步实施计划

## ✅ 已完成（Phase 0: 项目框架）

- [x] 创建项目目录结构
- [x] 编写项目设计文档 (PROJECT_DESIGN.md)
- [x] 编写 README.md
- [x] 创建配置文件模板 (config.yaml, classes.yaml)
- [x] 创建核心工作流框架 (core/workflow.py)
- [x] 创建依赖文件 (requirements.txt)
- [x] 创建 .gitignore
- [x] 创建 .env.example

## 🚧 待实施（Phase 1: 核心功能）

### 1. 人脸识别模块 (src/facecall/face/)

```bash
# 需要从 classroom-face-attendance 迁移的代码
- detector.py       # 人脸检测
- recognizer.py     # 人脸识别
- database.py       # 数据库管理
- models.py         # 数据模型
```

**任务**:
- [ ] 复制 classroom-face-attendance/src/face_attendance/*.py
- [ ] 适配新项目的模块结构
- [ ] 统一数据模型（使用 workflow.py 中的 Student Attendance）
- [ ] 添加类型注解
- [ ] 编写单元测试

### 2. 教务系统模块 (src/facecall/rollcall/)

```bash
# 需要从 zfsoft-rollcall-cli 迁移的代码
- client.py         # HTTP 客户端
- crypto.py         # RSA 加密
- models.py         # 数据模型
```

**任务**:
- [ ] 复制 zfsoft-rollcall-cli/src/zfsoft_rollcall/*.py
- [ ] 适配新项目的模块结构
- [ ] 统一数据模型
- [ ] 添加类型注解
- [ ] 编写单元测试

### 3. 配置管理模块 (src/facecall/config/)

```python
# settings.py - 配置加载和验证
- 从 YAML 加载配置
- 从环境变量读取敏感信息
- 配置验证（Pydantic）
- 查找数据库和名单（根据课程名）
```

**任务**:
- [ ] 实现 settings.py
- [ ] 实现 validator.py
- [ ] 添加单元测试

### 4. 工具模块 (src/facecall/utils/)

```python
# logger.py - 统一日志
# image.py - 图像处理工具
```

**任务**:
- [ ] 实现 logger.py (Rich 格式化)
- [ ] 实现 image.py
- [ ] 添加单元测试

### 5. 命令行脚本 (scripts/)

```bash
# attend.py - 一键考勤（核心脚本）
# build_db.py - 建立人脸库
# list_courses.py - 查询课程列表
# review.py - 审核识别结果
```

**任务**:
- [ ] 实现 scripts/attend.py
- [ ] 实现 scripts/build_db.py
- [ ] 实现 scripts/list_courses.py
- [ ] 实现 scripts/review.py
- [ ] 添加集成测试

### 6. Claude Code Skill (.claude/skills/)

```markdown
# facecall.md - Skill 定义
```

**任务**:
- [ ] 编写 Skill 定义
- [ ] 测试参数提取
- [ ] 测试交互流程

---

## 🎯 Phase 2: 体验优化（预计1周）

- [ ] Rich 终端UI（进度条、彩色输出）
- [ ] 交互式审核（不确定项确认）
- [ ] 配置向导（首次使用引导）
- [ ] 完善错误提示
- [ ] 编写完整文档

---

## 📋 实施优先级

### 立即开始（今天）
1. 迁移人脸识别模块
2. 迁移教务系统模块
3. 实现配置管理
4. 实现 scripts/attend.py

### 本周完成
1. 所有核心功能
2. 基础测试
3. 文档完善
4. Claude Skill 集成

### 下周优化
1. 终端UI美化
2. 交互优化
3. 性能优化
4. 部署文档

---

## 🔧 技术难点预判

### 1. 依赖冲突
**问题**: TensorFlow 和 其他库可能版本冲突
**解决**: 
- 使用 requirements.txt 锁定版本
- 测试兼容性
- 必要时使用 Docker 隔离

### 2. 数据模型统一
**问题**: 两个项目的数据模型不一致
**解决**:
- 在 core/workflow.py 定义统一模型
- 各模块适配统一模型
- 保持不可变性（frozen dataclass）

### 3. 配置查找逻辑
**问题**: 根据课程名自动查找数据库和名单
**解决**:
- 从 classes.yaml 读取配置
- 模糊匹配课程名
- 多个匹配时提示用户选择

---

## 🧪 测试策略

### 单元测试
```bash
tests/
├── test_face/
│   ├── test_detector.py
│   ├── test_recognizer.py
│   └── test_database.py
├── test_rollcall/
│   ├── test_client.py
│   └── test_crypto.py
└── test_core/
    └── test_workflow.py
```

### 集成测试
```bash
tests/test_integration/
├── test_full_workflow.py
├── test_cli_scripts.py
└── test_skill_integration.py
```

### 测试覆盖率目标
- 核心模块：80%+
- 工具模块：70%+
- 脚本：60%+

---

## 📝 文档待完成

```bash
docs/
├── QUICKSTART.md       # 快速开始（5分钟上手）
├── USER_GUIDE.md       # 用户指南（完整功能）
├── ADMIN_GUIDE.md      # 管理员指南（部署配置）
├── API.md              # Python API文档
├── TROUBLESHOOTING.md  # 故障排查
└── MIGRATION.md        # 从原项目迁移
```

---

## 🚀 发布计划

### v1.0.0-alpha（本周）
- 核心功能可用
- 基础文档

### v1.0.0-beta（下周）
- 所有功能完成
- 完整测试
- 完整文档

### v1.0.0（两周后）
- 生产就绪
- 性能优化
- 部署指南

---

## 📞 协作建议

1. **每日同步**: 每天结束时同步进度
2. **代码审查**: 重要模块完成后互相审查
3. **问题追踪**: 使用 GitHub Issues 追踪问题
4. **文档先行**: 先写文档再写代码

---

**下一步**: 开始迁移人脸识别模块

时间: 2026-10-20
状态: 框架已就绪，等待实施
