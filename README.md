# 🎯 Smart Attendance System

**智能考勤系统** - 人脸识别 + 教务系统自动提交的一体化解决方案

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## ✨ 核心特性

### 🎯 一键完成
```bash
# 原有方案：两条命令
python face-cli/check_attendance.py ...  # 步骤1
python zfsoft-cli/rollcall_auto.py ...   # 步骤2

# 新方案：一条命令
python scripts/attend.py --photo class.jpg --course "体育3"
```

### 🚀 极致效率
- ⚡ **15-20秒** - 从拍照到提交完成
- 🎯 **95%+准确率** - RetinaFace + Facenet512
- 🔄 **零中间文件** - 内存数据流，无残留

### 🤖 AI 深度集成
- 📸 自然语言：`识别 @photo.jpg 体育3`
- 🧠 智能推理：自动查找数据库和名单
- ✅ 交互确认：不确定项智能提示

### 🛡️ 隐私优先
- 🔒 **本地处理** - 人脸数据不离开本地
- 📊 **最小传输** - 仅提交学号和状态
- 🔐 **加密存储** - 数据库可选加密

---

## 📊 架构对比

### 原有方案
```
classroom-face-attendance  +  zfsoft-rollcall-cli
         ↓                          ↓
    JSON文件中转
         ↓
    需要两条命令
```

### 新方案
```
Smart Attendance System (统一项目)
    ↓
人脸识别模块 → 内存数据流 → 教务提交模块
    ↓
一条命令完成
```

---

## 🚀 快速开始

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/YOU/smart-attendance-system.git
cd smart-attendance-system

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置
cp .env.example .env
# 编辑 .env，填入教务系统账号密码
```

### 一次性准备（建立人脸库）

```bash
# 方案A: 单人照建库
python scripts/build_db.py \
  --mode single \
  --photos photos/001班/ \
  --roster rosters/001班.xlsx \
  --output databases/体育3_001班.pkl

# 方案B: 合照建库
python scripts/build_db.py \
  --mode group \
  --photo class_photo.jpg \
  --roster rosters/001班.xlsx \
  --output databases/体育3_001班.pkl
```

### 日常使用（一键考勤）

```bash
# 最简用法（自动从配置查找数据库和名单）
python scripts/attend.py --photo class.jpg --course "体育3"

# 完整用法
python scripts/attend.py \
  --photo class.jpg \
  --course "体育3" \
  --date today \
  --threshold 0.70

# 仅识别，不提交
python scripts/attend.py --photo class.jpg --course "体育3" --no-submit

# 跳过人工审核（全自动）
python scripts/attend.py --photo class.jpg --course "体育3" --no-review
```

**输出示例**:
```
✅ 考勤完成

📊 统计:
- 总人数: 37
- 已提交: 35
- 不确定: 2
  - 20230015 张三 (相似度: 0.72)
  - 20230028 李四 (相似度: 0.68)

⏱️ 耗时: 18.3秒
```

---

## 🤖 Claude Code Skill 集成

```bash
# 自然语言交互
"识别 @class_photo.jpg 体育3"
"考勤 @photo.jpg 高等数学"
"点名 @today_class.jpg 体育3 --no-review"
```

Claude 会自动：
1. 从文件名提取课程和日期
2. 从配置查找数据库和名单
3. 执行识别和提交
4. 格式化输出结果
5. 不确定项交互确认

---

## 📚 文档

- [快速开始](docs/QUICKSTART.md) - 5分钟上手
- [架构设计](PROJECT_DESIGN.md) - 技术细节
- [用户指南](docs/USER_GUIDE.md) - 完整功能
- [部署指南](docs/DEPLOYMENT.md) - 生产环境
- [故障排查](docs/TROUBLESHOOTING.md)

---

## 🔄 从原项目迁移

如果你之前使用 `classroom-face-attendance` + `zfsoft-rollcall-cli`：

```bash
# 1. 复制人脸数据库
cp /path/to/classroom-face-attendance/databases/*.pkl databases/

# 2. 复制名单
cp /path/to/classroom-face-attendance/rosters/*.xlsx rosters/

# 3. 配置 classes.yaml
vim config/classes.yaml

# 4. 完成！使用新命令
python scripts/attend.py --photo class.jpg --course "体育3"
```

---

## 🏗️ 项目结构

```
smart-attendance-system/
├── src/smart_attendance/
│   ├── face/          # 人脸识别模块
│   ├── rollcall/      # 教务系统模块
│   ├── core/          # 核心业务逻辑
│   ├── config/        # 配置管理
│   └── utils/         # 工具模块
├── scripts/           # 命令行脚本
│   ├── attend.py      # 一键考勤（核心）
│   ├── build_db.py    # 建立人脸库
│   └── list_courses.py # 查询课程
├── config/            # 配置文件
│   ├── config.yaml    # 主配置
│   └── classes.yaml   # 班级配置
└── .claude/skills/    # Claude Code Skill
```

---

## 🎯 优势对比

| 维度 | 原方案 | 新方案 | 提升 |
|------|--------|--------|------|
| **命令数** | 2条 | 1条 | 简化50% |
| **中间文件** | JSON文件 | 内存传递 | 无残留 |
| **配置文件** | 2份 | 1份 | 统一管理 |
| **依赖管理** | 独立venv | 统一依赖 | 无冲突 |
| **学习成本** | 两个工具 | 一个工具 | 降低50% |
| **AI集成** | 分别调用 | 一次调用 | 更友好 |

---

## 📦 技术栈

- **人脸识别**: DeepFace (Facenet512 + RetinaFace)
- **图像处理**: OpenCV + Pillow
- **深度学习**: TensorFlow 2.15
- **数据处理**: Pandas + NumPy
- **网络请求**: Requests + BeautifulSoup
- **配置管理**: PyYAML + Pydantic
- **终端UI**: Rich + Click

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

[MIT License](LICENSE)

---

## 🔗 相关项目

- [classroom-face-attendance](https://github.com/sucanfeng-coder/classroom-face-attendance) - 原人脸识别项目
- [zfsoft-rollcall-cli](https://github.com/YOU/zfsoft-rollcall-cli) - 原教务系统项目

---

## 📧 联系

有问题或建议？请提 [Issue](https://github.com/YOU/smart-attendance-system/issues)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
