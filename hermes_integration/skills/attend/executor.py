#!/usr/bin/env python3
"""Hermes Skill Executor - attend

人脸识别考勤 Skill，可选择性地自动提交到教务系统。
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def execute_skill(**kwargs) -> dict[str, Any]:
    """Attend Skill 执行器

    Args:
        **kwargs: Hermes 传递的参数
            - photo: 照片路径 (@标记)
            - course: 课程名称
            - date: 日期 (默认today)
            - submit: 是否自动提交 (默认false)
            - threshold: 识别阈值 (默认0.70)
            - database: 人脸数据库路径 (可选)
            - roster: 名单文件路径 (可选)

    Returns:
        dict: 执行结果
    """
    logger.info("=== Attend Skill 开始执行 ===")
    logger.info(f"参数: {kwargs}")

    # 1. 参数提取和验证
    validation_result = validate_params(kwargs)
    if not validation_result["valid"]:
        return validation_result["error"]

    params = validation_result["params"]

    # 2. 调用 FaceCall 识别
    logger.info("步骤1: 人脸识别")
    recognition_result = run_facecall_check(params)

    if not recognition_result["success"]:
        return recognition_result

    # 3. 检查不确定人脸
    summary = recognition_result.get("summary", {})
    uncertain_count = summary.get("uncertain", 0)
    absent_count = summary.get("absent", 0)

    logger.info(f"识别结果: uncertain={uncertain_count}, absent={absent_count}")

    # 4. 决策：是否需要审核
    if uncertain_count > 0:
        logger.info("检测到不确定人脸，需要人工审核")
        return {
            "success": True,
            "phase": "review_required",
            "message": f"✅ 识别完成\n⚠️ 有 {uncertain_count} 位同学不太确定，需要人工审核",
            "data": recognition_result,
            "summary": summary,
            "next_action": "请查看标注图片确认后再提交",
            "commands": {
                "submit": "/rollcall date={} course={} input=@attendance.json".format(
                    params["date"],
                    params["course"]
                )
            }
        }

    # 5. 执行插件（如果启用）
    if params.get("submit", False):
        logger.info("步骤2: 自动提交到教务系统")
        submission_result = submit_via_plugin(
            recognition_result,
            params["course"],
            params["date"]
        )

        return {
            "success": True,
            "phase": "completed",
            "message": "✅ 识别完成\n✅ 已自动提交到教务系统",
            "recognition": {
                "summary": summary,
                "students_count": len(recognition_result.get("students", []))
            },
            "submission": submission_result
        }

    # 6. 仅识别，不提交
    logger.info("仅识别模式，不自动提交")
    return {
        "success": True,
        "phase": "recognition_only",
        "message": f"✅ 识别完成\n📊 到课: {summary.get('present', 0)}/{summary.get('total', 0)}人\n📊 缺勤: {absent_count}人",
        "data": recognition_result,
        "summary": summary,
        "next_action": "使用 /rollcall 提交考勤",
        "commands": {
            "submit": "/rollcall date={} course={} input=@attendance.json".format(
                params["date"],
                params["course"]
            )
        }
    }


def validate_params(kwargs: dict[str, Any]) -> dict[str, Any]:
    """验证和提取参数

    Args:
        kwargs: 原始参数

    Returns:
        dict: 验证结果
            {
                "valid": bool,
                "params": dict (如果有效),
                "error": dict (如果无效)
            }
    """
    # 提取照片路径
    photo = kwargs.get("photo", "")
    if photo.startswith("@"):
        photo = photo[1:]

    if not photo:
        return {
            "valid": False,
            "error": {
                "success": False,
                "message": "❌ 缺少必需参数: photo",
                "usage": "/attend @photo.jpg course=体育3"
            }
        }

    # 检查照片文件是否存在
    photo_path = Path(photo)
    if not photo_path.exists():
        return {
            "valid": False,
            "error": {
                "success": False,
                "message": f"❌ 照片文件不存在: {photo}"
            }
        }

    # 提取课程
    course = kwargs.get("course")
    if not course:
        return {
            "valid": False,
            "error": {
                "success": False,
                "message": "❌ 缺少必需参数: course",
                "usage": "/attend @photo.jpg course=体育3"
            }
        }

    # 提取其他参数
    params = {
        "photo": str(photo_path.absolute()),
        "course": course,
        "date": kwargs.get("date", "today"),
        "threshold": float(kwargs.get("threshold", 0.70)),
        "submit": kwargs.get("submit", "false").lower() in ["true", "yes", "1"],
        "database": kwargs.get("database"),
        "roster": kwargs.get("roster")
    }

    return {
        "valid": True,
        "params": params
    }


def run_facecall_check(params: dict[str, Any]) -> dict[str, Any]:
    """调用 FaceCall 进行人脸识别

    Args:
        params: 识别参数

    Returns:
        dict: 识别结果
    """
    import subprocess
    import json
    from pathlib import Path

    # 读取配置获取项目根目录
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        return {
            "success": False,
            "error": "配置文件不存在"
        }

    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    project_root = Path(config["facecall"]["project_root"])
    check_script = project_root / "classroom-face-attendance/scripts/check_attendance.py"

    if not check_script.exists():
        return {
            "success": False,
            "error": f"人脸识别脚本不存在: {check_script}"
        }

    # 解析 database 和 roster 路径
    database = params.get("database")
    if not database:
        database = project_root / config["facecall"]["default_database"]
    else:
        database = Path(database)

    roster = params.get("roster")
    if not roster:
        roster = project_root / config["facecall"]["default_roster"]
    else:
        roster = Path(roster)

    # 检查文件存在性
    if not database.exists():
        return {
            "success": False,
            "error": f"人脸数据库不存在: {database}"
        }

    if not roster.exists():
        return {
            "success": False,
            "error": f"班级名单不存在: {roster}"
        }

    # 准备输出路径
    output_json = Path("/tmp") / f"attendance_{params['course']}_{params['date']}.json"
    annotated_img = Path("/tmp") / f"annotated_{params['course']}_{params['date']}.jpg"

    # 构建命令
    cmd = [
        "python3",
        str(check_script),
        "--photo", params["photo"],
        "--database", str(database),
        "--roster", str(roster),
        "--threshold", str(params["threshold"]),
        "--output", str(output_json),
        "--annotated", str(annotated_img)
    ]

    logger.info(f"执行人脸识别: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            logger.error(f"识别失败: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr
            }

        # 读取结果
        if not output_json.exists():
            return {
                "success": False,
                "error": "识别脚本未生成输出文件"
            }

        with open(output_json) as f:
            attendance_data = json.load(f)

        return {
            "success": True,
            "date": params["date"],
            "course": params["course"],
            "summary": attendance_data.get("summary", {}),
            "students": attendance_data.get("students", []),
            "annotated_image": str(annotated_img) if annotated_img.exists() else None
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "识别超时（120秒）"
        }
    except Exception as e:
        logger.exception("识别过程出错")
        return {
            "success": False,
            "error": str(e)
        }


def submit_via_plugin(
    recognition_result: dict[str, Any],
    course: str,
    date: str
) -> dict[str, Any]:
    """通过插件提交考勤

    Args:
        recognition_result: 识别结果
        course: 课程名称
        date: 日期

    Returns:
        dict: 提交结果
    """
    try:
        # 导入插件管理器
        from facecall.core.plugin_manager import PluginManager

        # 获取配置文件路径
        config_path = Path(__file__).parent / "config.yaml"

        if not config_path.exists():
            logger.warning(f"插件配置文件不存在: {config_path}")
            return {
                "success": False,
                "message": "插件配置文件不存在"
            }

        # 创建插件管理器
        manager = PluginManager(str(config_path))

        # 准备插件数据
        plugin_data = {
            "students": recognition_result.get("students", []),
            "course": course,
            "date": date
        }

        # 执行插件
        result = manager.execute_plugin("rollcall", plugin_data)
        return result

    except Exception as e:
        logger.error(f"插件执行失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"插件执行失败: {str(e)}"
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Attend Skill Executor")
    parser.add_argument("--photo", required=True, help="照片路径")
    parser.add_argument("--course", required=True, help="课程名称")
    parser.add_argument("--date", default="today", help="日期")
    parser.add_argument("--threshold", type=float, default=0.70, help="识别阈值")
    parser.add_argument("--submit", action="store_true", help="自动提交")
    parser.add_argument("--database", help="人脸数据库路径")
    parser.add_argument("--roster", help="名单文件路径")

    args = parser.parse_args()

    # 构建 kwargs
    kwargs = {
        "photo": args.photo,
        "course": args.course,
        "date": args.date,
        "threshold": args.threshold,
        "submit": "true" if args.submit else "false"
    }

    if args.database:
        kwargs["database"] = args.database
    if args.roster:
        kwargs["roster"] = args.roster

    # 执行
    result = execute_skill(**kwargs)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 返回退出码
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
