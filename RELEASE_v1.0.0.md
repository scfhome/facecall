# 🎉 FaceCall v1.0.0 发布

**发布日期**: 2026-10-20  
**项目地址**: https://github.com/scfhome/facecall  
**版本标签**: v1.0.0

---

## 📦 版本概述

FaceCall v1.0.0 是首个正式版本，集成了人脸识别考勤、插件架构和 Hermes Agent，为教育场景提供智能考勤解决方案。

---

## ✨ 核心特性

### 🎯 人脸识别考勤
- **DeepFace 集成**: 使用 DeepFace 0.0.87 + TensorFlow 2.15.0
- **高精度模型**: RetinaFace 检测器 + Facenet512 识别模型
- **智能阈值**: 可配置匹配阈值（默认 0.70）
- **不确定检测**: 自动标记不确定人脸，提示人工审核
- **可视化输出**: 生成标注图片，显示识别结果

### 🔌 插件架构
- **Protocol 定义**: 类型安全的插件接口
- **动态加载**: YAML 配置驱动，运行时加载
- **生命周期管理**: 注册、验证、执行、清理
- **错误处理**: 完善的异常捕获和恢复机制
- **可扩展性**: 轻松添加新插件，无需修改核心代码

### 🤖 Hermes Agent 集成
- **attend Skill**: 人脸识别执行器，支持 Telegram/CLI/Cron
- **rollcall Plugin**: 教务系统提交插件
- **智能决策**: 不确定时暂停，等待人工确认
- **一键完成**: 可选自动提交（`submit=true`）
- **多平台支持**: Telegram Bot、命令行、定时任务

### 📊 性能指标
- **识别速度**: ~8 秒（37 人班级）
- **提交耗时**: ~5 秒
- **总耗时**: 15-20 秒
- **准确率**: 95%+（正常光照条件）
- **并发支持**: 支持多班级并行处理

---

## 📚 文档体系

### 用户文档
- [README.md](README.md) - 项目概述和快速开始
- [QUICKSTART.md](hermes_integration/QUICKSTART.md) - 5 分钟快速上手
- [SKILL.md](hermes_integration/skills/attend/SKILL.md) - Skill 完整使用手册

### 开发文档
- [PROJECT_DESIGN.md](docs/PROJECT_DESIGN.md) - 完整架构设计
- [HERMES_INTEGRATION.md](docs/HERMES_INTEGRATION.md) - Hermes 深度集成分析
- [PLUGIN_DEVELOPMENT.md](docs/PLUGIN_DEVELOPMENT.md) - 插件开发指南
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南

### 导航文档
- [INDEX.md](docs/INDEX.md) - 文档导航中心
- [CHANGELOG.md](CHANGELOG.md) - 版本历史

---

## 🛠️ 技术栈

### 人脸识别
- **DeepFace**: 0.0.87 - 人脸识别框架
- **TensorFlow**: 2.15.0 - 深度学习引擎
- **OpenCV**: 4.9.0.80 - 图像处理
- **RetinaFace**: 0.0.13 - 人脸检测器

### 数据处理
- **Pandas**: 2.2.0 - 数据分析
- **NumPy**: 1.26.3 - 数值计算
- **Pillow**: 10.2.0 - 图像处理

### 配置与验证
- **PyYAML**: 6.0.1 - YAML 解析
- **Pydantic**: 2.6.1 - 数据验证
- **python-dotenv**: 1.0.1 - 环境变量

### 用户界面
- **Rich**: 13.7.0 - 终端 UI
- **Click**: 8.1.7 - CLI 框架

### 开发工具
- **pytest**: 8.0.0+ - 测试框架
- **black**: 24.0.0+ - 代码格式化
- **ruff**: 0.2.0+ - 代码检查
- **mypy**: 1.8.0+ - 类型检查

---

## 📦 安装指南

### 系统要求
- Python >= 3.10
- 2GB+ RAM（模型加载需要）
- 摄像头或照片文件
- 教务系统访问权限（可选，用于自动提交）

### 快速安装

```bash
# 克隆仓库
git clone https://github.com/scfhome/facecall.git
cd facecall

# 安装依赖
pip install -r requirements.txt

# 开发环境
pip install -r requirements-dev.txt
```

### 配置

1. **班级配置** (`config/classes.yaml`):
```yaml
班级名称:
  students:
    - xh: "学号"
      name: "姓名"
      path: "faces/学号.jpg"
```

2. **插件配置** (`config/config.yaml`):
```yaml
plugins:
  rollcall:
    enabled: true
    config:
      username: "你的用户名"
      password: "你的密码"
      base_url: "https://jwgl.cucn.edu.cn"
```

3. **环境变量** (`.env`):
```bash
ROLLCALL_USERNAME=your_username
ROLLCALL_PASSWORD=your_password
```

---

## 🚀 使用示例

### Telegram Bot (推荐)
```
# 基础识别
/attend @photo.jpg course=体育3

# 一键完成（识别+提交）
/attend @photo.jpg course=体育3 submit=true
```

### 命令行
```bash
# 基础识别
python hermes_integration/skills/attend/executor.py \
  --photo class.jpg \
  --course "体育3"

# 自动提交
python hermes_integration/skills/attend/executor.py \
  --photo class.jpg \
  --course "体育3" \
  --submit
```

### 定时任务 (Hermes Cron)
```
# 每周一、三、五早上 8 点自动执行
/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

---

## 🧪 测试

### 运行测试
```bash
# 所有测试
pytest tests/ -v

# 覆盖率报告
pytest --cov=src/facecall --cov-report=html tests/

# 特定测试
pytest tests/test_rollcall_plugin.py -v
```

### 测试覆盖率
- **目标**: 80%+
- **当前**: 基础测试已完成，持续添加中
- **类型**: 单元测试 + 集成测试

---

## 🔒 安全特性

### 隐私保护
- ✅ 人脸数据本地处理，不上传云端
- ✅ 仅学号通过网络传输
- ✅ 敏感文件已排除（.gitignore）
- ✅ 环境变量管理密码

### 数据验证
- ✅ 插件输入验证（Protocol）
- ✅ 类型检查（Pydantic）
- ✅ 错误详细日志

### 错误处理
- ✅ 完善的异常捕获
- ✅ 友好的错误提示
- ✅ 自动资源清理

---

## 📁 项目结构

```
facecall/
├── src/facecall/              # 核心代码
│   ├── core/                  # 核心模块
│   │   ├── plugin.py          # 插件协议
│   │   ├── plugin_manager.py  # 插件管理器
│   │   └── workflow.py        # 工作流
│   ├── face/                  # 人脸识别
│   ├── rollcall/              # 考勤提交
│   ├── config/                # 配置管理
│   └── utils/                 # 工具函数
│
├── hermes_integration/        # Hermes 集成
│   ├── skills/attend/         # attend Skill
│   │   ├── executor.py        # 执行器
│   │   ├── SKILL.md           # 使用手册
│   │   └── config.yaml        # 配置
│   └── plugins/rollcall/      # rollcall 插件
│       └── plugin.py          # 插件实现
│
├── tests/                     # 测试代码
├── docs/                      # 文档
├── config/                    # 配置模板
├── README.md                  # 主文档
├── LICENSE                    # MIT 许可证
├── CONTRIBUTING.md            # 贡献指南
├── CHANGELOG.md               # 更新日志
└── pyproject.toml             # 项目配置
```

---

## 🎯 使用场景

### 1. 日常考勤（最常见）
**场景**: 每节课拍照考勤  
**使用**: Telegram Bot 一键识别+提交

```
/attend @photo.jpg course=体育3 submit=true
```

**耗时**: 15-20 秒  
**优势**: 无需登录电脑，手机直接完成

### 2. 不确定审核
**场景**: 识别结果有不确定人脸  
**使用**: 系统自动暂停，提示审核

```
❗ 检测到 2 个不确定人脸：
   - 张三 (置信度: 0.65)
   - 李四 (置信度: 0.68)

请手动审核照片后重新提交。
```

**操作**: 检查标注图片 → 手动调整 → 重新提交

### 3. 定时任务
**场景**: 每周固定时间自动考勤  
**使用**: Hermes Cron 定时执行

```
/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

**优势**: 完全自动化，无需人工干预

### 4. 多班级并行
**场景**: 一次拍照，多班级考勤  
**使用**: 命令行批量处理

```bash
for class in "体育3" "体育4" "体育5"; do
  python executor.py --photo photo.jpg --course "$class" --submit &
done
wait
```

**耗时**: 20 秒（并行执行）

### 5. 离线测试
**场景**: 测试识别准确率，不提交  
**使用**: 仅识别模式

```
/attend @photo.jpg course=体育3
# 查看识别结果，不提交系统
```

---

## 🔮 未来规划

### 短期（1-2 周）
- [ ] 完善单元测试（目标覆盖率 80%+）
- [ ] GitHub Actions CI/CD
- [ ] Docker 镜像
- [ ] 公开示例数据

### 中期（1-2 月）
- [ ] Web UI 界面
- [ ] REST API 服务
- [ ] 性能优化（GPU 加速）
- [ ] 更多插件
  - notification - 发送通知
  - analytics - 生成报表
  - backup - 数据备份

### 长期（3-6 月）
- [ ] 多语言支持（i18n）
- [ ] 移动端 App
- [ ] 实时视频流识别
- [ ] 多校联盟部署
- [ ] 联邦学习（隐私计算）

---

## 🤝 贡献

我们欢迎任何形式的贡献！

### 贡献方式
- 🐛 报告 Bug（GitHub Issues）
- 💡 建议新功能（GitHub Issues）
- 📝 改进文档（Pull Request）
- 💻 提交代码（Pull Request）

### 开发流程
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交代码 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源。

```
MIT License

Copyright (c) 2026 scfmac

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 致谢

### 核心团队
- **scfmac** - 项目创建者和维护者
- **Claude Fable 5.1** - AI 协作伙伴

### 技术依赖
- [DeepFace](https://github.com/serengil/deepface) - 人脸识别框架
- [TensorFlow](https://www.tensorflow.org/) - 深度学习引擎
- [OpenCV](https://opencv.org/) - 计算机视觉库
- [Hermes Agent](https://github.com/hermes-agent) - AI Agent 系统

### 灵感来源
- 传统考勤系统的痛点
- 人脸识别技术的成熟
- AI Agent 的实际应用需求

---

## 📞 联系方式

- **GitHub**: [@scfhome](https://github.com/scfhome)
- **项目**: [facecall](https://github.com/scfhome/facecall)
- **Issues**: [提交问题](https://github.com/scfhome/facecall/issues)

---

## 📊 项目统计

- **代码行数**: ~3,000 行（核心代码）
- **文档字数**: ~50,000 字（中文文档）
- **测试覆盖**: 持续添加中
- **插件数量**: 1 个（rollcall）
- **Skill 数量**: 1 个（attend）
- **支持平台**: 3 个（Telegram/CLI/Cron）

---

## 🎯 快速链接

- [GitHub 仓库](https://github.com/scfhome/facecall)
- [快速开始](hermes_integration/QUICKSTART.md)
- [Skill 手册](hermes_integration/skills/attend/SKILL.md)
- [插件开发](docs/PLUGIN_DEVELOPMENT.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

---

**发布时间**: 2026-10-20 23:59:59  
**当前版本**: v1.0.0  
**维护者**: scfmac  
**协作**: Claude Fable 5.1
