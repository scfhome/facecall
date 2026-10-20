"""Rollcall 插件

将考勤数据提交到教务系统。
"""

from typing import Any
import subprocess
import json
import tempfile
from pathlib import Path
import logging


logger = logging.getLogger(__name__)


class Plugin:
    """教务系统提交插件

    将人脸识别结果提交到 CUCN 教务系统。
    """

    name = "rollcall"
    version = "1.0.0"
    description = "Submit attendance to educational system"

    def __init__(self, config: dict[str, Any]):
        """初始化插件

        Args:
            config: 插件配置
                {
                    "rollcall_cli_path": str,  # rollcall CLI 脚本路径
                    "timeout": int,             # 超时时间（秒）
                    "username": str (可选),     # 用户名
                    "password": str (可选)      # 密码
                }
        """
        self.config = config
        self.rollcall_cli_path = config.get(
            "rollcall_cli_path",
            "../cucn-rollcall-cli/rollcall_auto.py"
        )
        self.timeout = config.get("timeout", 60)
        self.username = config.get("username")
        self.password = config.get("password")

        logger.info(f"Rollcall 插件初始化: {self.rollcall_cli_path}")

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

        # 1. 准备临时 JSON 文件
        try:
            temp_file = self._create_temp_file(data["students"])
        except Exception as e:
            logger.error(f"创建临时文件失败: {e}")
            return {
                "success": False,
                "message": f"创建临时文件失败: {str(e)}",
                "submitted": 0,
                "failed": 0
            }

        # 2. 构建命令
        cmd = self._build_command(data, temp_file)

        # 3. 执行命令
        try:
            result = self._run_command(cmd)

            # 4. 清理临时文件
            self._cleanup_temp_file(temp_file)

            logger.info(f"提交完成: success={result.get('success')}")
            return result

        except Exception as e:
            logger.error(f"执行命令失败: {e}", exc_info=True)
            self._cleanup_temp_file(temp_file)

            return {
                "success": False,
                "message": f"提交失败: {str(e)}",
                "submitted": 0,
                "failed": len(data["students"])
            }

    def _create_temp_file(self, students: list[dict[str, Any]]) -> Path:
        """创建临时 JSON 文件

        Args:
            students: 学生考勤数据

        Returns:
            Path: 临时文件路径
        """
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            delete=False
        ) as f:
            json.dump({"students": students}, f, ensure_ascii=False, indent=2)
            temp_path = Path(f.name)

        logger.debug(f"创建临时文件: {temp_path}")
        return temp_path

    def _build_command(self, data: dict[str, Any], temp_file: Path) -> list[str]:
        """构建执行命令

        Args:
            data: 考勤数据
            temp_file: 临时文件路径

        Returns:
            list: 命令列表
        """
        cmd = [
            "python3",
            self.rollcall_cli_path,
            "--date", data["date"],
            "--course", data["course"],
            "--mode", "manual",
            "--input", str(temp_file)
        ]

        # 添加可选的用户名和密码
        if self.username:
            cmd.extend(["--username", self.username])
        if self.password:
            cmd.extend(["--password", self.password])

        logger.debug(f"命令: {' '.join(cmd)}")
        return cmd

    def _run_command(self, cmd: list[str]) -> dict[str, Any]:
        """执行命令

        Args:
            cmd: 命令列表

        Returns:
            dict: 执行结果
        """
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=self.timeout
        )

        # 尝试解析 JSON 输出
        try:
            result = json.loads(proc.stdout)
            return result
        except json.JSONDecodeError:
            # 如果不是 JSON，返回原始输出
            logger.warning(f"输出不是 JSON 格式: {proc.stdout[:200]}")
            return {
                "success": proc.returncode == 0,
                "message": proc.stdout or proc.stderr,
                "returncode": proc.returncode
            }

    def _cleanup_temp_file(self, temp_file: Path) -> None:
        """清理临时文件

        Args:
            temp_file: 临时文件路径
        """
        try:
            temp_file.unlink(missing_ok=True)
            logger.debug(f"删除临时文件: {temp_file}")
        except Exception as e:
            logger.warning(f"删除临时文件失败: {e}")

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
                "rollcall_cli_path": self.rollcall_cli_path,
                "timeout": self.timeout,
                "has_credentials": bool(self.username and self.password)
            }
        }
