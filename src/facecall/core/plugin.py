"""插件协议定义

定义了 FaceCall 插件系统的基础接口。
"""

from typing import Protocol, Any


class Plugin(Protocol):
    """插件协议

    所有插件必须实现此协议中的方法。
    """

    name: str
    """插件名称"""

    version: str
    """插件版本"""

    def execute(self, data: dict[str, Any]) -> dict[str, Any]:
        """执行插件

        Args:
            data: 插件输入数据

        Returns:
            dict: 插件执行结果，包含 success, message 等字段
        """
        ...

    def validate(self, data: dict[str, Any]) -> bool:
        """验证输入数据

        Args:
            data: 待验证数据

        Returns:
            bool: 数据是否有效
        """
        ...

    def get_info(self) -> dict[str, Any]:
        """获取插件信息

        Returns:
            dict: 插件信息（名称、版本、描述等）
        """
        ...
