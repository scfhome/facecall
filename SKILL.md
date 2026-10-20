---
name: attend
description: 人脸识别考勤 - 自动识别照片中的学生并提交到教务系统。使用 DeepFace + RetinaFace 进行人脸识别，支持批量处理和自动提交。适用于教育场景的考勤管理。
license: MIT
compatibility: Requires Python 3.10+, DeepFace, TensorFlow 2.15+
metadata:
  author: scfmac
  version: "1.0.0"
  category: education
  repository: https://github.com/scfhome/facecall
  hermes:
    tags: [face-recognition, attendance, deepface, education, automation]
    category: productivity
    requires_toolsets: [terminal]
    config:
      - key: facecall.database_path
        description: 人脸数据库路径
        default: "faces/"
        prompt: "人脸数据库目录（存放学生照片）"
      - key: facecall.roster_path
        description: 班级名单路径
        default: "rosters/class_2024_1.yaml"
        prompt: "班级名单文件路径"
      - key: rollcall.username
        description: 教务系统用户名
        prompt: "教务系统账号"
      - key: rollcall.password
        description: 教务系统密码
        prompt: "教务系统密码"
platforms: [macos, linux, windows]
---

# 人脸识别考勤 Skill

自动识别班级合照中的学生，生成考勤记录，并可选择性地提交到教务系统。

## 什么时候使用这个 Skill

在以下场景中使用这个 skill：

- 📸 需要识别班级合照中的学生
- ✅ 需要生成考勤名单
- 📊 需要统计到课率、缺勤率
- 🚀 需要自动提交考勤到教务系统
- 🎯 用户提到"人脸识别"、"考勤"、"点名"、"签到"等关键词

## 功能概述

1. **人脸识别**: 使用 DeepFace + RetinaFace + Facenet512 检测和识别人脸
2. **考勤统计**: 自动生成到课、缺勤、不确定名单
3. **图片标注**: 在原图上标注识别结果
4. **自动提交**: 可选地提交到教务系统（需要审核通过）

## 前置准备

### 1. 人脸数据库

在 `faces/` 目录下准备学生照片，以学号命名：

```
faces/
├── 20210001.jpg
├── 20210002.jpg
├── 20210003.jpg
└── ...
```

**要求**：
- 格式：JPG 或 PNG
- 命名：`{学号}.{jpg|png}`
- 质量：清晰的正面照，光线充足
- 大小：建议不超过 2MB

### 2. 班级名单

在 `rosters/` 目录下准备班级名单 YAML 文件：

```yaml
# rosters/class_2024_1.yaml
class_name: "2024级1班"
students:
  - 20210001
  - 20210002
  - 20210003
  # ...
```

### 3. 配置文件

编辑 `config/config.yaml` 填写教务系统信息：

```yaml
facecall:
  project_root: "/path/to/facecall"
  default_database: "faces/"
  default_roster: "rosters/class_2024_1.yaml"

rollcall:
  username: "你的学号"
  password: "你的密码"
  base_url: "https://jw.example.edu.cn"
```

## 使用步骤

### 基础用法：仅识别

```bash
/attend @class_photo.jpg course=体育3
```

执行流程：
1. ✅ 加载人脸数据库
2. ✅ 检测照片中的所有人脸
3. ✅ 匹配人脸到学生
4. ✅ 生成考勤统计
5. ✅ 生成标注图片
6. ✅ 返回结果

返回结果包括：
- 到课人数 / 总人数
- 缺勤人数
- 不确定人数（相似度低于阈值）
- 学生明细列表
- 标注后的图片路径

### 高级用法：自动提交

```bash
/attend @class_photo.jpg course=体育3 submit=true
```

额外步骤：
- ⚠️ 如果有"不确定"人脸，暂停提交，等待人工审核
- ✅ 如果所有识别确定，自动提交到教务系统

### 自定义参数

```bash
/attend @photo.jpg course=体育3 threshold=0.75 database=faces_2024/ roster=rosters/special_class.yaml
```

参数说明：
- `photo`: **必需**，班级照片路径
- `course`: **必需**，课程名称
- `submit`: 可选，是否自动提交（默认 false）
- `threshold`: 可选，识别阈值 0.0-1.0（默认 0.70）
- `database`: 可选，自定义人脸数据库路径
- `roster`: 可选，自定义班级名单路径
- `date`: 可选，考勤日期（默认 today）

## 执行流程详解

### 阶段 1: 人脸检测

```python
from facecall.face import FaceDetector

detector = FaceDetector(
    detector_backend="retinaface",
    model_name="Facenet512"
)

detected_faces = detector.detect_faces(photo_path)
```

- 使用 RetinaFace 检测器（高准确率）
- 提取 Facenet512 特征向量
- 过滤低置信度人脸

### 阶段 2: 人脸匹配

```python
from facecall.face import FaceMatcher

matcher = FaceMatcher(threshold=0.70)
matches = matcher.match_faces(detected_faces, face_database)
```

- 计算余弦相似度
- 应用阈值过滤
- 返回最佳匹配

### 阶段 3: 结果分类

根据相似度分为三类：

| 类别 | 相似度 | 说明 | 处理 |
|------|--------|------|------|
| **确定到课** | > threshold | 高置信度匹配 | ✅ 记为出勤 |
| **不确定** | 0.5 - threshold | 中等置信度 | ⚠️ 需要人工审核 |
| **未匹配** | < 0.5 | 未识别 | ❌ 不处理 |

### 阶段 4: 考勤提交（可选）

```python
from facecall.rollcall import AttendanceSubmitter

submitter = AttendanceSubmitter(config)
result = submitter.submit(students, course, date)
```

**自动提交条件**：
- ✅ `submit=true`
- ✅ 所有人脸识别确定（无"不确定"）

**需要人工审核条件**：
- ⚠️ 存在"不确定"人脸
- 返回不确定人脸的标注图片
- 用户审核后可手动提交

## 常见问题和解决方案

### 问题 1: 识别率低

**症状**：很多学生被标记为"不确定"或"未识别"

**原因**：
- 照片质量差（模糊、背光、侧脸）
- 人脸数据库质量差
- 阈值设置过高

**解决**：
1. 使用更清晰的班级照片
2. 更新人脸数据库（高质量正面照）
3. 降低阈值：`threshold=0.65`
4. 使用 `matcher_v2.py`（多角度匹配）

### 问题 2: 照片中检测不到人脸

**症状**：返回"检测到 0 张人脸"

**原因**：
- 照片分辨率太低
- 人脸太小（远距离拍摄）
- 遮挡严重（口罩、帽子）

**解决**：
1. 使用高分辨率照片（推荐 1920x1080+）
2. 近距离拍摄
3. 要求学生摘下口罩/帽子

### 问题 3: TensorFlow 内存不足

**症状**：`ResourceExhaustedError: OOM when allocating tensor`

**原因**：
- 照片太大
- 人脸太多
- 系统内存不足

**解决**：
1. 压缩照片到合适大小（2-3MB）
2. 分批处理（拍多张小组照）
3. 增加系统内存或使用 GPU

### 问题 4: 提交教务系统失败

**症状**：`{"success": false, "error": "登录失败"}`

**原因**：
- 用户名/密码错误
- 教务系统升级/更换
- 网络不通

**解决**：
1. 检查 `config/config.yaml` 中的账号密码
2. 手动登录教务系统确认可用
3. 检查网络连接
4. 查看 `src/facecall/rollcall/client.py` 是否需要更新

## 输出格式

### 成功输出（仅识别）

```json
{
  "success": true,
  "phase": "recognition_only",
  "message": "✅ 识别完成\n📊 到课: 35/37人\n📊 缺勤: 2人",
  "data": {
    "date": "2024-10-20",
    "course": "体育3",
    "summary": {
      "total": 37,
      "present": 35,
      "uncertain": 0,
      "absent": 2
    },
    "students": [
      {
        "student_id": "20210001",
        "name": "张三",
        "confidence": 0.89,
        "status": "present"
      },
      // ...
    ],
    "annotated_image": "/tmp/annotated_体育3_2024-10-20.jpg"
  }
}
```

### 成功输出（已提交）

```json
{
  "success": true,
  "phase": "completed",
  "message": "✅ 识别完成\n✅ 已自动提交到教务系统",
  "recognition": {
    "summary": {
      "total": 37,
      "present": 35,
      "uncertain": 0,
      "absent": 2
    }
  },
  "submission": {
    "success": true,
    "message": "提交成功"
  }
}
```

### 需要审核输出

```json
{
  "success": true,
  "phase": "review_required",
  "message": "✅ 识别完成\n⚠️ 有 3 位同学不太确定，需要人工审核",
  "data": {
    // ... 识别结果
  },
  "next_action": "请查看标注图片确认后再提交"
}
```

## 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| **识别速度** | ~8 秒 | 37 人班级，CPU |
| **准确率** | 95%+ | 正常光照条件 |
| **内存占用** | ~2GB | 模型加载后 |
| **最大人数** | 100+ | 理论上限 |

## 隐私和安全

### 数据处理

✅ **本地处理**：所有人脸识别在本地完成  
✅ **仅传输学号**：提交教务系统时不传输照片  
✅ **临时文件**：标注图片保存在 `/tmp/`，定期清理

### 敏感信息

⚠️ **密码存储**：`config/config.yaml` 包含明文密码  
🔒 **建议**：使用环境变量存储密码

```bash
export ROLLCALL_PASSWORD="your_password"
```

然后在代码中读取：
```python
import os
password = os.environ.get("ROLLCALL_PASSWORD")
```

## 相关文件

- [安装指南](../README.md) - 如何安装和配置
- [架构文档](docs/ARCHITECTURE.md) - 系统架构设计
- [API 参考](references/API.md) - Python API 文档
- [配置示例](config/config.yaml) - 配置文件模板

## 验证成功

执行完成后，检查：

- ✅ 返回 `"success": true`
- ✅ `summary.total` 等于班级人数
- ✅ `summary.present + summary.uncertain + summary.absent == total`
- ✅ 标注图片已生成
- ✅ 如果 `submit=true`，检查教务系统是否有记录

## 故障排除快速参考

| 错误信息 | 可能原因 | 解决方案 |
|----------|----------|----------|
| `照片文件不存在` | 路径错误 | 检查照片路径 |
| `人脸数据库不存在` | 未准备数据库 | 准备 `faces/` 目录 |
| `班级名单不存在` | 未准备名单 | 准备 `rosters/*.yaml` |
| `检测到 0 张人脸` | 照片质量差 | 使用高质量照片 |
| `识别超时` | 照片太大/人太多 | 压缩照片或分批 |
| `登录失败` | 账号密码错误 | 检查配置文件 |
| `OOM` | 内存不足 | 减小照片尺寸 |

## 技术栈

- **DeepFace**: 人脸识别框架
- **RetinaFace**: 人脸检测器
- **Facenet512**: 特征提取模型
- **TensorFlow**: 深度学习框架
- **OpenCV**: 图像处理
- **Requests**: HTTP 客户端

## 许可证

本 Skill 采用 MIT License 开源。

---

**维护者**: scfmac  
**版本**: 1.0.0  
**最后更新**: 2024-10-20
