# FaceCall Hermes Skill

> 人脸识别考勤 Skill，适配 Hermes Agent 系统

---

## 📦 这是什么？

这是 **FaceCall** 的 Hermes Agent Skill 预打包版本，开箱即用。

**核心功能**：
- 🎯 人脸识别考勤（DeepFace + TensorFlow）
- 🤖 智能决策（不确定时暂停）
- 📤 可选自动提交（教务系统）
- 🔌 插件式扩展

---

## 🚀 一键安装

### 前提条件
- Python >= 3.10
- pip 包管理器
- 2GB+ RAM

### 安装步骤
```bash
# 1. 克隆项目
git clone https://github.com/scfhome/facecall.git
cd facecall

# 2. 运行安装脚本
bash skills/hermes/attend/install.sh

# 3. 编辑配置
vim ~/.hermes/skills/attend/config.yaml

# 4. 准备数据
mkdir -p faces/
# 放入学生照片（学号.jpg）
```

**耗时**: 约 5 分钟

---

## 🎯 使用方式

### Telegram Bot（推荐）
```
# 基础识别
/attend @photo.jpg course=体育3

# 一键完成（识别+提交）
/attend @photo.jpg course=体育3 submit=true
```

### 命令行
```bash
cd ~/.hermes/skills/attend

# 仅识别
python executor.py --photo class.jpg --course "体育3"

# 识别+提交
python executor.py --photo class.jpg --course "体育3" --submit
```

### 定时任务（Hermes Cron）
```
# 每周一、三、五 8:00 自动执行
/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

---

## ⚙️ 配置说明

### 1. Skill 配置（`config.yaml`）

```yaml
# 人脸识别配置
face_recognition:
  model: "Facenet512"      # 识别模型
  detector: "retinaface"   # 检测器
  threshold: 0.70          # 匹配阈值

# 插件配置
plugins:
  rollcall:
    enabled: true
    config:
      username: "你的学号"
      password: "你的密码"
      base_url: "https://jwgl.cucn.edu.cn"
      timeout: 30
```

### 2. 班级配置（`classes.yaml`）

```yaml
体育3:
  students:
    - xh: "20210001"
      name: "张三"
      path: "faces/20210001.jpg"
    - xh: "20210002"
      name: "李四"
      path: "faces/20210002.jpg"
```

### 3. 人脸数据库（`faces/`）

```
faces/
├── 20210001.jpg
├── 20210002.jpg
└── ...
```

**要求**：
- 格式：JPG/PNG
- 命名：学号.jpg
- 内容：每人一张正面照

---

## 📊 执行流程

```
1. 接收照片 + 课程名
   ↓
2. 加载班级学生名单
   ↓
3. 人脸识别（DeepFace）
   ↓
4. 分类学生
   - 正常（置信度 >= 0.70）
   - 不确定（置信度 < 0.70）
   - 缺席（未识别）
   ↓
5. 智能决策
   - 有不确定 → 暂停，提示审核
   - 全部确定 → 继续
   ↓
6. 可选提交（submit=true）
   - 调用 rollcall 插件
   - 提交到教务系统
   ↓
7. 返回结果
```

**耗时**：15-20 秒（37 人班级）

---

## 🎨 输出示例

### 成功识别
```
✅ 人脸识别完成

📊 统计信息:
  - 应到: 37 人
  - 实到: 35 人
  - 缺席: 2 人

👥 正常 (35 人):
  1. 张三 (20210001) - 置信度: 0.85
  2. 李四 (20210002) - 置信度: 0.92
  ...

❌ 缺席 (2 人):
  1. 王五 (20210003)
  2. 赵六 (20210004)

📸 标注图片: /tmp/annotated_20261020_143022.jpg
```

### 不确定情况
```
⚠️  检测到 2 个不确定人脸

❓ 不确定 (2 人):
  1. 张三 (20210001) - 置信度: 0.65
  2. 李四 (20210002) - 置信度: 0.68

🔍 建议操作:
  1. 查看标注图片
  2. 手动确认身份
  3. 调整识别阈值（如需要）

⛔ 已暂停提交，请审核后重新执行
```

---

## 🔧 常见问题

### 1. 安装失败

**问题**: `pip install` 报错

**解决**:
```bash
# 升级 pip
pip3 install --upgrade pip

# 使用国内镜像
pip3 install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 识别准确率低

**问题**: 误识别率高

**解决**:
```yaml
# 调高阈值
face_recognition:
  threshold: 0.75  # 默认 0.70
```

### 3. 提交失败

**问题**: rollcall 插件报错

**解决**:
```bash
# 检查配置
cat ~/.hermes/skills/attend/config.yaml

# 测试登录
python hermes_integration/plugins/rollcall/plugin.py
```

### 4. 找不到 Skill

**问题**: Hermes 看不到 `/attend` 命令

**解决**:
```bash
# 检查链接
ls -la ~/.hermes/skills/attend

# 重新安装
bash skills/hermes/attend/install.sh
```

---

## 📚 完整文档

- [项目主页](../../../README.md)
- [快速开始](../../../hermes_integration/QUICKSTART.md)
- [Skill 手册](../../../hermes_integration/skills/attend/SKILL.md)
- [插件开发](../../../docs/PLUGIN_DEVELOPMENT.md)

---

## 🤝 贡献

欢迎贡献！请参考 [贡献指南](../../../CONTRIBUTING.md)

---

## 📜 许可证

MIT License - 详见 [LICENSE](../../../LICENSE)

---

**维护者**: scfmac  
**版本**: v1.0.0  
**更新**: 2026-10-20
