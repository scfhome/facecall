# 🤖 Hermes Agent 快速开始

> 5 分钟完成 FaceCall Hermes Skill 安装和配置

---

## 📋 目录

- [前提条件](#前提条件)
- [一键安装](#一键安装)
- [配置数据](#配置数据)
- [测试运行](#测试运行)
- [Telegram 使用](#telegram-使用)
- [常见问题](#常见问题)

---

## 前提条件

### 系统要求
- **操作系统**: macOS / Linux / Windows (WSL)
- **Python**: >= 3.10
- **内存**: >= 2GB
- **磁盘**: >= 5GB（模型文件需要）

### 软件要求
```bash
# 检查 Python 版本
python3 --version  # 应显示 Python 3.10.x 或更高

# 检查 pip
pip3 --version
```

### Hermes Agent 安装
```bash
# 如果还没安装 Hermes Agent
pip3 install hermes-agent

# 验证安装
hermes --version
```

---

## 一键安装

### Step 1: 克隆项目
```bash
cd ~/Documents  # 或你的工作目录
git clone https://github.com/scfhome/facecall.git
cd facecall
```

### Step 2: 运行安装脚本
```bash
bash skills/hermes/attend/install.sh
```

**脚本会自动完成**：
1. ✅ 检查 Python 版本
2. ✅ 安装核心库（`pip install -e .`）
3. ✅ 链接 Skill 到 Hermes（`~/.hermes/skills/attend`）
4. ✅ 复制配置模板

**安装成功输出**：
```
✅ 安装完成！

📖 下一步操作：
   1. 编辑配置文件: ~/.hermes/skills/attend/config.yaml
   2. 准备人脸数据: /path/to/facecall/faces
   3. 配置班级信息: /path/to/facecall/config/classes.yaml
```

---

## 配置数据

### Step 3: 准备人脸数据库

```bash
# 创建目录
mkdir -p faces/

# 放入学生照片（学号命名）
faces/
├── 20210001.jpg
├── 20210002.jpg
├── 20210003.jpg
└── ...
```

**照片要求**：
- 格式：JPG 或 PNG
- 内容：清晰的正面照
- 命名：学号.jpg
- 大小：建议 < 5MB

### Step 4: 配置班级信息

编辑 `config/classes.yaml`：

```yaml
体育3:
  students:
    - xh: "20210001"
      name: "张三"
      path: "faces/20210001.jpg"
    
    - xh: "20210002"
      name: "李四"
      path: "faces/20210002.jpg"
    
    # ... 更多学生

# 可以配置多个班级
体育4:
  students:
    - xh: "20210101"
      name: "王五"
      path: "faces/20210101.jpg"
```

### Step 5: 配置 Skill

编辑 `~/.hermes/skills/attend/config.yaml`：

```yaml
# 人脸识别配置
face_recognition:
  model: "Facenet512"      # 识别模型
  detector: "retinaface"   # 人脸检测器
  threshold: 0.70          # 匹配阈值（0-1）

# 插件配置
plugins:
  rollcall:
    enabled: true
    config:
      username: "你的学号"        # 教务系统账号
      password: "你的密码"        # 教务系统密码
      base_url: "https://jwgl.cucn.edu.cn"
      timeout: 30
```

**配置说明**：
- `threshold`: 越高越严格（0.70 = 70% 置信度）
- `username/password`: 用于自动提交考勤
- 如果不需要自动提交，可以禁用 rollcall 插件

---

## 测试运行

### Step 6: 命令行测试

```bash
cd ~/.hermes/skills/attend

# 测试识别（不提交）
python executor.py \
  --photo ~/facecall/test_photos/class.jpg \
  --course "体育3"
```

**预期输出**：
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

📸 标注图片: /tmp/annotated_xxx.jpg
```

### Step 7: 测试自动提交

```bash
python executor.py \
  --photo ~/facecall/test_photos/class.jpg \
  --course "体育3" \
  --submit
```

**预期输出**：
```
✅ 人脸识别完成
... (识别结果)

📤 正在提交考勤...
✅ 提交成功！

📊 提交结果:
  - 提交人数: 35 人
  - 状态码: 200
  - 耗时: 3.2 秒
```

---

## Telegram 使用

### Step 8: 配置 Telegram Bot

1. **启动 Hermes Agent**
```bash
hermes start --telegram
```

2. **在 Telegram 中找到你的 Bot**
   - 搜索你的 Bot 用户名
   - 发送 `/start` 开始对话

### Step 9: 使用 Skill

#### 基础识别
```
/attend @photo.jpg course=体育3
```

1. 在 Telegram 发送照片
2. 发送上述命令（替换照片文件名）
3. 等待识别结果（约 15 秒）

#### 一键完成（识别+提交）
```
/attend @photo.jpg course=体育3 submit=true
```

#### 示例对话
```
你: [发送班级合照]
你: /attend @photo_001.jpg course=体育3

Bot: 🔍 开始识别...
Bot: ✅ 识别完成！
     应到: 37 人
     实到: 35 人
     缺席: 2 人
     
     [标注图片]
     
     详细名单: ...
```

---

## 常见问题

### Q1: 安装脚本失败

**问题**: `bash install.sh` 报错

**解决**:
```bash
# 检查权限
chmod +x skills/hermes/attend/install.sh

# 手动安装
cd facecall
pip3 install -e .
ln -sf $(pwd)/hermes_integration/skills/attend ~/.hermes/skills/attend
```

### Q2: 找不到 Skill

**问题**: Hermes 看不到 `/attend` 命令

**解决**:
```bash
# 检查链接
ls -la ~/.hermes/skills/attend

# 重启 Hermes
hermes restart
```

### Q3: 识别准确率低

**问题**: 误识别或漏识别

**解决**:
```yaml
# 调整阈值（config.yaml）
face_recognition:
  threshold: 0.75  # 提高到 0.75
```

### Q4: 提交失败

**问题**: rollcall 插件报错

**解决**:
```bash
# 1. 检查配置
cat ~/.hermes/skills/attend/config.yaml

# 2. 测试登录
python hermes_integration/plugins/rollcall/plugin.py

# 3. 检查网络
ping jwgl.cucn.edu.cn
```

### Q5: 照片太大

**问题**: Telegram 照片上传慢

**解决**:
```bash
# 压缩照片（保持识别质量）
convert input.jpg -resize 1920x1080 -quality 85 output.jpg
```

---

## 🎯 下一步

### 进阶使用
- 📚 [Skill 完整手册](../hermes_integration/skills/attend/SKILL.md)
- 🔌 [插件开发指南](../docs/PLUGIN_DEVELOPMENT.md)
- 🏗️ [架构设计文档](../docs/PROJECT_DESIGN.md)

### 定时任务
```bash
# 每周一、三、五 8:00 自动考勤
/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

### 性能优化
```yaml
# 使用 GPU 加速（需要 CUDA）
face_recognition:
  use_gpu: true
```

---

## 📞 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/scfhome/facecall/issues)
- **文档中心**: [docs/INDEX.md](../docs/INDEX.md)
- **贡献指南**: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**预计总耗时**: 5-10 分钟  
**难度**: ⭐⭐ (中等)  
**维护者**: scfmac  
**更新**: 2026-10-20
