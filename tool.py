#!/usr/bin/env python3
"""FaceCall WorkBuddy Tool

人脸识别考勤工具，适配 WorkBuddy Agent 系统
"""

from typing import Dict, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def register() -> Dict[str, Any]:
    """注册工具到 WorkBuddy

    Returns:
        dict: 工具元数据
    """
    return {
        "name": "facecall",
        "version": "1.0.0",
        "description": "人脸识别考勤工具 - 自动识别照片中的学生并提交到教务系统",
        "author": "scfmac",
        "parameters": {
            "photo": {
                "type": "string",
                "required": True,
                "description": "照片文件路径"
            },
            "course": {
                "type": "string",
                "required": True,
                "description": "课程名称"
            },
            "submit": {
                "type": "boolean",
                "required": False,
                "default": False,
                "description": "是否自动提交到教务系统"
            },
            "threshold": {
                "type": "number",
                "required": False,
                "default": 0.70,
                "description": "人脸识别阈值（0.0-1.0）"
            },
            "date": {
                "type": "string",
                "required": False,
                "default": "today",
                "description": "考勤日期（today 或 YYYY-MM-DD）"
            }
        },
        "returns": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "total": {"type": "integer", "description": "应到人数"},
                        "present": {"type": "integer", "description": "实到人数"},
                        "absent": {"type": "integer", "description": "缺席人数"},
                        "uncertain": {"type": "integer", "description": "不确定人数"},
                        "students": {"type": "array", "description": "学生列表"},
                        "submitted": {"type": "boolean", "description": "是否已提交"},
                        "annotated_image": {"type": "string", "description": "标注图片路径"}
                    }
                },
                "error": {"type": "string"}
            }
        },
        "tags": ["face-recognition", "attendance", "education", "automation"]
    }


def execute(
    photo: str,
    course: str,
    submit: bool = False,
    threshold: float = 0.70,
    date: str = "today",
    **kwargs
) -> Dict[str, Any]:
    """执行人脸识别考勤

    Args:
        photo: 照片路径
        course: 课程名称
        submit: 是否提交到教务系统
        threshold: 识别阈值
        date: 日期
        **kwargs: 其他参数

    Returns:
        dict: 执行结果
    """
    logger.info(f"=== FaceCall Tool 开始执行 ===")
    logger.info(f"照片: {photo}, 课程: {course}, 提交: {submit}")

    try:
        # 导入 facecall 内部模块
        from facecall.face.detector import FaceDetector
        from facecall.face.matcher import FaceMatcher
        from facecall.face.database import FaceDatabaseBuilder
        from facecall.face.annotator import ImageAnnotator

        # 验证参数
        photo_path = Path(photo)
        if not photo_path.exists():
            return {
                "success": False,
                "error": f"照片文件不存在: {photo}"
            }

        # 读取配置
        config_path = Path(__file__).parent / "config" / "config.yaml"
        if not config_path.exists():
            return {
                "success": False,
                "error": "配置文件不存在"
            }

        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # 初始化组件
        database_path = Path(config["facecall"]["default_database"])
        roster_path = Path(config["facecall"]["default_roster"])

        detector = FaceDetector()
        matcher = FaceMatcher(threshold=threshold)
        db_builder = FaceDatabaseBuilder(database_path)
        annotator = ImageAnnotator()

        # 1. 加载人脸数据库
        face_db = db_builder.load_database()

        # 2. 检测人脸
        detected_faces = detector.detect_faces(str(photo_path))
        logger.info(f"检测到 {len(detected_faces)} 张人脸")

        # 3. 匹配人脸
        matches = matcher.match_faces(detected_faces, face_db)

        # 4. 加载班级名单
        with open(roster_path) as f:
            roster_data = yaml.safe_load(f)

        # 5. 统计结果
        students = []
        present = []
        uncertain_list = []

        for match in matches:
            student_info = {
                "student_id": match.student_id,
                "name": match.name,
                "confidence": match.confidence,
                "status": "present" if match.confidence > threshold else "uncertain"
            }
            students.append(student_info)

            if match.confidence > threshold:
                present.append(match.student_id)
            else:
                uncertain_list.append(match.student_id)

        # 找出缺勤学生
        all_students = set(roster_data.get("students", []))
        present_set = set(present)
        absent = list(all_students - present_set - set(uncertain_list))

        # 6. 生成标注图片
        output_dir = Path("/tmp")
        annotated_img = output_dir / f"facecall_{course}_{date}.jpg"
        annotator.annotate_image(
            str(photo_path),
            matches,
            str(annotated_img)
        )

        # 7. 提交考勤（如果需要）
        submitted = False
        if submit and len(uncertain_list) == 0:
            from facecall.rollcall.client import CUCNClient
            from facecall.rollcall.rollcall_client import RollcallClient

            # 提交逻辑
            client = RollcallClient(
                username=config["rollcall"]["username"],
                password=config["rollcall"]["password"]
            )

            submit_result = client.submit_attendance(
                course=course,
                date=date,
                students=present
            )
            submitted = submit_result.get("success", False)

        return {
            "success": True,
            "data": {
                "total": len(all_students),
                "present": len(present),
                "absent": len(absent),
                "uncertain": len(uncertain_list),
                "students": students,
                "submitted": submitted,
                "annotated_image": str(annotated_img) if annotated_img.exists() else None
            }
        }

    except Exception as e:
        logger.exception("FaceCall Tool 执行失败")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """命令行测试入口"""
    import argparse

    parser = argparse.ArgumentParser(description="FaceCall WorkBuddy Tool")
    parser.add_argument("--photo", required=True, help="照片路径")
    parser.add_argument("--course", required=True, help="课程名称")
    parser.add_argument("--submit", action="store_true", help="自动提交")
    parser.add_argument("--threshold", type=float, default=0.70, help="识别阈值")
    parser.add_argument("--date", default="today", help="日期")

    args = parser.parse_args()

    result = execute(
        photo=args.photo,
        course=args.course,
        submit=args.submit,
        threshold=args.threshold,
        date=args.date
    )

    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
