---
name: attend
description: Face recognition attendance for classroom
author: scfmac
version: 1.0.0
tags: [attendance, face-recognition, education, facecall]
platforms: [cli, telegram, cron, discord, slack]
requires_approval: false
---

# 🎓 点到 - 智能课堂考勤

基于人脸识别的智能考勤系统，一拍即点，秒知到课。

## ✨ 功能特性

- ✅ 人脸识别点名
- ✅ 自动生成标注图片
- ✅ 不确定人脸审核提醒
- ✅ 可选自动提交到教务系统
- ✅ 支持自然语言交互
- ✅ JSON 格式数据导出

## 📖 使用方法

### 1. 基础识别（仅识别，不提交）

最常用的方式，先看看识别结果：

```
/attend @class.jpg course=体育3
```

或自然语言：
```
"识别这张照片的考勤，体育3"
"帮我点一下今天体育课的名"
```

### 2. 一键完成（识别+提交）

确定没问题，直接搞定：

```
/attend @class.jpg course=体育3 submit=true
```

### 3. 自定义识别阈值

如果识别不准，可以调整阈值：

```
/attend @class.jpg course=体育3 threshold=0.65
```

### 4. 指定数据库和名单

```
/attend @class.jpg course=体育3 database=@db.pkl roster=@students.xlsx
```

## 📋 参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `photo` | ✅ | - | 课堂照片路径（@标记） |
| `course` | ✅ | - | 课程名称（支持模糊匹配） |
| `date` | ❌ | today | 日期（today/tomorrow/2026-10-20） |
| `threshold` | ❌ | 0.70 | 人脸识别阈值（0.0-1.0） |
| `submit` | ❌ | false | 是否自动提交到教务系统 |
| `database` | ❌ | 自动 | 人脸数据库路径 |
| `roster` | ❌ | 自动 | 班级名单路径 |

## 🔄 执行流程

```
1️⃣ 参数验证
   ├─ 检查照片文件
   ├─ 检查必需参数
   └─ 验证参数格式

2️⃣ 人脸识别
   ├─ 加载照片
   ├─ 检测人脸 (RetinaFace)
   ├─ 提取特征 (Facenet512)
   ├─ 匹配识别 (Cosine相似度)
   └─ 生成标注图

3️⃣ 结果检查
   ├─ 有不确定人脸？→ 提示审核
   └─ 全部确定 → 继续

4️⃣ 决策点
   ├─ submit=true → 自动提交
   └─ submit=false → 仅返回结果

5️⃣ 插件执行（可选）
   └─ 调用 rollcall 插件提交到教务系统

6️⃣ 结果报告
   └─ 返回格式化结果给用户
```

## ✅ 输出示例

### 场景1: 仅识别模式

```json
{
  "success": true,
  "phase": "recognition_only",
  "message": "✅ 识别完成\n📊 到课: 35/37人\n📊 缺勤: 2人",
  "summary": {
    "total": 37,
    "present": 35,
    "absent": 2,
    "uncertain": 0
  },
  "next_action": "使用 /rollcall 提交考勤",
  "commands": {
    "submit": "/rollcall date=today course=体育3 input=@attendance.json"
  }
}
```

**用户看到**：
```
✅ 识别完成
📊 到课: 35/37人
📊 缺勤: 2人

➡️ 下一步: 使用 /rollcall 提交考勤
```

---

### 场景2: 需要审核

```json
{
  "success": true,
  "phase": "review_required",
  "message": "✅ 识别完成\n⚠️ 有 2 位同学不太确定，需要人工审核",
  "summary": {
    "total": 37,
    "present": 33,
    "absent": 2,
    "uncertain": 2
  },
  "next_action": "请查看标注图片确认后再提交"
}
```

**用户看到**：
```
✅ 识别完成
⚠️ 有 2 位同学不太确定，需要人工审核

📸 标注图片: [查看]

➡️ 请确认后再提交
```

---

### 场景3: 一键完成

```json
{
  "success": true,
  "phase": "completed",
  "message": "✅ 识别完成\n✅ 已自动提交到教务系统",
  "recognition": {
    "summary": {
      "total": 37,
      "present": 37,
      "absent": 0,
      "uncertain": 0
    }
  },
  "submission": {
    "success": true,
    "submitted": 37,
    "message": "提交成功: 37/37人"
  }
}
```

**用户看到**：
```
✅ 识别完成
✅ 已自动提交到教务系统

📊 37/37人记录已更新
⏰ 提交时间: 08:05
```

---

## 📱 使用场景

### 场景1: Telegram Bot 日常点名

```
[Telegram 对话]

老师: [上传照片]
老师: /attend 体育3

Bot: 🔄 正在识别...（预计15秒）

     ✅ 识别完成！
     
     📊 统计:
     • 到课: 35人
     • 缺勤: 2人
     
     📸 标注图片: [查看]
     
     💡 下一步:
     • 直接提交 → /rollcall
     • 修改数据 → 下载JSON编辑

老师: 直接提交

Bot: ✅ 已提交！37人考勤记录已更新
```

---

### 场景2: 一键搞定（特别忙）

```
老师: [上传照片]
老师: /attend 体育3 submit=true

Bot: 🔄 正在识别...
     ✅ 识别完成: 37/37人到课
     🚀 正在提交...
     ✅ 提交成功！
     
     全部搞定，去上课吧！😊
```

---

### 场景3: 有疑问，先看看

```
老师: /attend 体育3 submit=true

Bot: 🔄 正在识别...
     ✅ 识别完成
     
     ⚠️ 等一下！
     有2个同学我不太确定：
     
     📸 [标注照片] ← 点击查看
     
     确认没问题再提交

老师: [查看照片]
老师: 没问题

Bot: 🚀 正在提交...
     ✅ 提交成功！
```

---

### 场景4: 定时自动点名（Cron）

```bash
# 每周一/三/五 早上8:00 自动拍照点名
# （需要配合摄像头自动拍照）

/cron add "0 8 * * 1,3,5" "/attend @/camera/latest.jpg course=体育3 submit=true"
```

---

## 🛠️ 技术实现

### 底层依赖

- **FaceCall Core** - 人脸识别引擎
  - DeepFace 0.0.87
  - RetinaFace 人脸检测
  - Facenet512 特征提取
  
- **Plugin System** - 插件系统
  - PluginManager - 插件管理器
  - rollcall Plugin - 教务系统提交

### 数据流

```
用户输入
  ↓
Hermes Agent (解析)
  ↓
attend Skill (executor.py)
  ↓
FaceCall Core (识别)
  ↓
Plugin Manager (可选)
  ↓
rollcall Plugin (可选)
  ↓
教务系统 API
  ↓
返回结果
```

---

## ⚙️ 配置

### 插件配置

```yaml
# hermes_integration/skills/attend/config.yaml

plugins:
  rollcall:
    enabled: true
    module_path: "hermes_integration.plugins.rollcall"
    rollcall_cli_path: "../cucn-rollcall-cli/rollcall_auto.py"
    timeout: 60
    
    # 自动提交策略
    auto_submit:
      # 仅当这些条件都满足时才自动提交
      conditions:
        uncertain: 0    # 无不确定人脸
        absent: <= 2    # 缺勤不超过2人
      
      # 否则提示人工确认
      confirm_when:
        - uncertain > 0
        - absent > 5
```

---

## ❗ 错误处理

| 错误类型 | 原因 | 解决方案 |
|---------|------|---------|
| 照片不存在 | 文件路径错误 | 检查路径，使用 @ 标记 |
| 人脸检测失败 | 照片质量差/无人脸 | 重新拍摄清晰照片 |
| 识别准确率低 | 阈值过高/数据库陈旧 | 降低阈值或更新数据库 |
| 插件执行失败 | 配置错误/网络问题 | 检查配置，手动提交 |
| 提交失败 | 教务系统问题 | 稍后重试或联系管理员 |

---

## 🎓 最佳实践

1. **第一次使用先测试**
   ```
   /attend @photo.jpg course=体育3
   # 不加 submit=true，先看识别效果
   ```

2. **根据准确率调整阈值**
   ```
   # 误识别太多 → 提高阈值
   /attend @photo.jpg course=体育3 threshold=0.75
   
   # 漏识别太多 → 降低阈值
   /attend @photo.jpg course=体育3 threshold=0.65
   ```

3. **学期初更新数据库**
   ```
   # 有新生转入，及时补录人脸数据
   ```

4. **有疑问必看标注图**
   ```
   # uncertain > 0 时一定要查看标注图确认
   ```

5. **定期检查考勤异常**
   ```
   # 连续多次缺勤的学生要关注
   ```

---

## 📊 性能指标

### 处理时间

- **人脸检测**: ~3-5秒（37人）
- **特征提取**: ~2-3秒
- **匹配识别**: ~1秒
- **生成标注图**: ~0.5秒
- **插件提交**: ~5-7秒
- **总耗时**: **约15-20秒** 完成全流程

对比手工点名（3-5分钟），**效率提升约12倍**。

### 准确率

- **正常光照**: 95%+
- **较差光照**: 85%+
- **部分遮挡**: 70%+

---

## 🔗 相关资源

- 📚 [FaceCall 完整文档](../../README.md)
- 🔌 [插件开发指南](../../docs/PLUGIN_DEVELOPMENT.md)
- 🤖 [Hermes 集成说明](../../docs/HERMES_INTEGRATION.md)

---

## 📝 更新日志

### v1.0.0 (2026-10-20)
- ✅ 初始版本
- ✅ 基础人脸识别功能
- ✅ 插件式架构
- ✅ rollcall 插件集成
- ✅ Hermes Skill 封装

---

## 📄 License

MIT License

---

**Status**: ✅ Ready for Testing  
**Last Updated**: 2026-10-20  
**Maintainer**: scfmac
