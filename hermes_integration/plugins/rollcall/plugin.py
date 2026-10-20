"""Rollcall 插件

将考勤数据提交到教务系统。
"""

from typing import Any
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class Plugin:
    """教务系统提交插件

    将人脸识别结果提交到 CUCN 教务系统。
    使用内部 rollcall 模块，不再依赖外部 CLI。
    """

    name = "rollcall"
    version = "1.0.0"
    description = "Submit attendance to educational system"

    def __init__(self, config: dict[str, Any]):
        """初始化插件

        Args:
            config: 插件配置
                {
                    "timeout": int,             # 超时时间（秒）
                    "username": str (可选),     # 用户名
                    "password": str (可选)      # 密码
                }
        """
        self.config = config
        self.timeout = config.get("timeout", 60)
        self.username = config.get("username")
        self.password = config.get("password")

        logger.info("Rollcall 插件初始化（使用内部模块）")

    def validate(self, data: dict[str, Any]) -> bool:
        """验证输入数据

        Args:
            data: 考勤数据
                {
                    "students": [{"xh": str, "category": str, "note": str?}],
                    "course": str,
                    "date": str
                }

        Returns:
            bool: 数据是否有效
        """
        required_fields = ["students", "course", "date"]

        # 检查必需字段
        if not all(field in data for field in required_fields):
            logger.error(f"缺少必需字段: {required_fields}")
            return False

        # 检查 students 是否为列表
        if not isinstance(data["students"], list):
            logger.error("students 必须是列表")
            return False

        # 检查每个学生记录
        for student in data["students"]:
            if not isinstance(student, dict):
                logger.error("每条学生记录必须是字典")
                return False

            if "xh" not in student or "category" not in student:
                logger.error("学生记录缺少 xh 或 category 字段")
                return False

        return True

    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        """执行提交

        Args:
            data: 考勤数据

        Returns:
            dict: 提交结果
                {
                    "success": bool,
                    "message": str,
                    "submitted": int,
                    "failed": int
                }
        """
        logger.info(f"开始提交考勤: course={data['course']}, date={data['date']}")

        try:
            # 使用内部 rollcall 模块
            from facecall.rollcall import RollcallClient

            # 创建客户端
            client = RollcallClient(
                username=self.username or self.config.get("username"),
                password=self.password or self.config.get("password")
            )

            # 提交考勤
            result = client.submit_attendance(
                students=data["students"],
                course=data["course"],
                date=data["date"]
            )

            logger.info(f"提交完成: success={result.get('success')}")
            return result

        except Exception as e:
            logger.error(f"提交失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"提交失败: {str(e)}",
                "submitted": 0,
                "failed": len(data.get("students", []))
            }

    def get_info(self) -> dict[str, Any]:
        """获取插件信息

        Returns:
            dict: 插件信息
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "config": {
                "timeout": self.timeout,
                "has_credentials": bool(self.username and self.password)
            }
        }
