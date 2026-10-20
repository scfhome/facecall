"""
FaceCall WorkBuddy Tool Adapter

为 WorkBuddy Agent 系统提供人脸识别考勤能力
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from facecall.face.recognizer import FaceRecognizer
from facecall.core.plugin_manager import PluginManager


class FaceCallTool:
    """人脸识别考勤工具（WorkBuddy 适配器）"""

    name = "facecall"
    version = "1.0.0"
    description = "人脸识别考勤工具，支持自动识别和提交"

    def __init__(self, config_path: Optional[str] = None):
        """初始化工具

        Args:
            config_path: 配置文件路径（可选）
        """
        if config_path is None:
            config_path = str(Path(__file__).parent / "config.yaml")

        self.recognizer = FaceRecognizer()
        self.plugin_manager = PluginManager(config_path)

    def execute(
        self, photo: str, course: str, submit: bool = False, threshold: float = 0.70
    ) -> Dict[str, Any]:
        """执行人脸识别考勤

        Args:
            photo: 照片路径
            course: 课程名称
            submit: 是否自动提交到教务系统
            threshold: 识别阈值（默认 0.70）

        Returns:
            结果字典:
            {
                "success": True/False,
                "data": {
                    "total": 37,
                    "present": 35,
                    "absent": 2,
                    "uncertain": 0,
                    "students": [...],
                    "submitted": True/False
                },
                "error": "错误信息（如果失败）"
            }
        """
        try:
            # 1. 人脸识别
            result = self.recognizer.recognize(photo, course, threshold)

            # 2. 检查不确定人脸
            uncertain = [
                s for s in result["students"] if s.get("category") == "不确定"
            ]

            if uncertain and submit:
                return {
                    "success": False,
                    "error": f"检测到 {len(uncertain)} 个不确定人脸，无法自动提交",
                    "data": {
                        "total": result["total"],
                        "present": result["present"],
                        "absent": result["absent"],
                        "uncertain": len(uncertain),
                        "students": result["students"],
                        "submitted": False,
                    },
                }

            # 3. 可选提交
            submitted = False
            if submit and not uncertain:
                submit_result = self.plugin_manager.execute_plugin(
                    "rollcall",
                    {"students": result["students"], "course": course},
                )
                submitted = submit_result.get("success", False)

            # 4. 返回结果
            return {
                "success": True,
                "data": {
                    "total": result["total"],
                    "present": result["present"],
                    "absent": result["absent"],
                    "uncertain": len(uncertain),
                    "students": result["students"],
                    "submitted": submitted,
                    "annotated_image": result.get("annotated_image"),
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_schema(self) -> Dict[str, Any]:
        """获取工具的输入输出 Schema（供 WorkBuddy 注册使用）

        Returns:
            Schema 定义
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": {
                    "photo": {
                        "type": "string",
                        "description": "班级照片路径",
                    },
                    "course": {
                        "type": "string",
                        "description": "课程名称（如：体育3）",
                    },
                    "submit": {
                        "type": "boolean",
                        "description": "是否自动提交到教务系统",
                        "default": False,
                    },
                    "threshold": {
                        "type": "number",
                        "description": "人脸识别阈值（0-1）",
                        "default": 0.70,
                    },
                },
                "required": ["photo", "course"],
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "total": {"type": "integer"},
                            "present": {"type": "integer"},
                            "absent": {"type": "integer"},
                            "uncertain": {"type": "integer"},
                            "students": {"type": "array"},
                            "submitted": {"type": "boolean"},
                        },
                    },
                    "error": {"type": "string"},
                },
            },
        }


# WorkBuddy 自动注册入口
def register():
    """WorkBuddy 自动发现和注册工具"""
    tool = FaceCallTool()
    return tool.get_schema()


# 命令行测试入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="FaceCall WorkBuddy Tool")
    parser.add_argument("--photo", required=True, help="照片路径")
    parser.add_argument("--course", required=True, help="课程名称")
    parser.add_argument("--submit", action="store_true", help="自动提交")
    parser.add_argument("--threshold", type=float, default=0.70, help="识别阈值")

    args = parser.parse_args()

    tool = FaceCallTool()
    result = tool.execute(
        photo=args.photo,
        course=args.course,
        submit=args.submit,
        threshold=args.threshold,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
