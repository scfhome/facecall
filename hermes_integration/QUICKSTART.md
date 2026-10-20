# 🚀 Hermes 集成快速开始

5分钟上手 Hermes + FaceCall 智能考勤。

---

## 📦 安装

### 1. 克隆项目

```bash
cd ~/projects
git clone https://github.com/scfhome/facecall.git
cd facecall
```

### 2. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyyaml  # 插件系统需要
```

### 3. 配置 Hermes

将 attend Skill 添加到 Hermes：

```bash
# 复制 Skill 到 Hermes 技能目录
cp -r hermes_integration/skills/attend ~/.hermes/skills/

# 或者符号链接（推荐）
ln -s $(pwd)/hermes_integration/skills/attend ~/.hermes/skills/attend
```

### 4. 配置插件

编辑配置文件：

```bash
vim hermes_integration/skills/attend/config.yaml
```

修改 rollcall CLI 路径：

```yaml
plugins:
  rollcall:
    rollcall_cli_path: "/path/to/your/cucn-rollcall-cli/rollcall_auto.py"
```

---

## ✅ 测试

### 1. 测试插件（可选）

```bash
pytest tests/test_rollcall_plugin.py -v
```

### 2. 测试 Skill 执行器

```bash
python hermes_integration/skills/attend/executor.py \
  --photo test.jpg \
  --course "体育3"
```

应该输出：

```json
{
  "success": true,
  "phase": "recognition_only",
  "message": "✅ 识别完成\n📊 到课: 35/37人\n📊 缺勤: 2人",
  "summary": {...}
}
```

---

## 📱 Hermes 中使用

### 方式1: Telegram Bot

```
[Telegram 对话]

你: [上传照片]
你: /attend course=体育3

Hermes Bot: 🔄 正在识别...
            ✅ 识别完成！
            📊 到课: 35/37人
```

### 方式2: 命令行

```bash
hermes skill attend photo=@class.jpg course=体育3
```

### 方式3: 自然语言

```
你: "识别这张照片的考勤，体育3"

Hermes: [自动调用 attend Skill]
```

---

## 🎯 常用命令

### 基础识别

```bash
# Telegram
/attend @photo.jpg course=体育3

# 命令行
hermes skill attend photo=@photo.jpg course=体育3
```

### 一键完成

```bash
/attend @photo.jpg course=体育3 submit=true
```

### 指定日期

```bash
/attend @photo.jpg course=体育3 date=2026-10-21
```

### 调整阈值

```bash
/attend @photo.jpg course=体育3 threshold=0.65
```

---

## 🔧 配置选项

### 插件配置

`hermes_integration/skills/attend/config.yaml`:

```yaml
plugins:
  rollcall:
    enabled: true                    # 启用插件
    rollcall_cli_path: "..."         # CLI 路径
    timeout: 60                      # 超时设置
    
    # 自动提交策略
    auto_submit:
      conditions:
        uncertain: 0                 # 无不确定人脸
        absent_max: 2                # 缺勤 <= 2人
```

### Hermes 配置

`~/.hermes/config.yaml`:

```yaml
skills:
  attend:
    enabled: true
    timeout: 120                     # Skill 执行超时
    require_confirmation: false      # 不需要确认
```

---

## 📊 工作流示例

### 场景1: 日常快速点名

```
1. 拍课堂照片
2. 发送到 Telegram
3. 输入: /attend 体育3
4. 查看结果
5. 输入: 提交
6. 完成！
```

**耗时**: 约20秒

---

### 场景2: 一键搞定

```
1. 拍课堂照片
2. 输入: /attend 体育3 submit=true
3. 完成！
```

**耗时**: 约20秒

---

### 场景3: 定时自动点名

```bash
# Hermes Cron
/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

每周一/三/五早上8点自动点名并提交。

---

## ❗ 故障排查

### 问题1: 插件未加载

```
错误: 插件不存在: rollcall
```

**解决**:
1. 检查配置文件路径
2. 确认 `config.yaml` 中 `enabled: true`
3. 检查 Python import 路径

---

### 问题2: rollcall CLI 执行失败

```
错误: 插件执行失败
```

**解决**:
1. 确认 rollcall_cli_path 正确
2. 测试手动执行:
   ```bash
   python /path/to/rollcall_auto.py --help
   ```
3. 检查权限和依赖

---

### 问题3: 照片识别失败

```
错误: 人脸检测失败
```

**解决**:
1. 检查照片质量
2. 降低阈值: `threshold=0.60`
3. 确认人脸数据库存在

---

## 📚 下一步

1. **配置数据库**: 建立你的人脸数据库
   ```bash
   facecall build --mode single --photos photos/ --roster roster.xlsx
   ```

2. **测试准确率**: 多拍几张测试识别效果

3. **调整阈值**: 根据准确率调整默认阈值

4. **配置自动化**: 设置定时任务或 Telegram Bot

5. **查看完整文档**: 
   - [SKILL.md](skills/attend/SKILL.md) - Skill 完整文档
   - [HERMES_INTEGRATION.md](../docs/HERMES_INTEGRATION.md) - 深度集成分析

---

## 🎉 完成！

现在你可以在 Hermes 中使用点到 FaceCall 进行智能考勤了！

有问题？查看 [FAQ](../docs/FAQ.md) 或提交 Issue。

---

**更新时间**: 2026-10-20  
**版本**: 1.0.0
