"""插件管理器

负责加载、管理和执行插件。
"""

from dataclasses import dataclass
from typing import Any
from pathlib import Path
import importlib
import logging

from .plugin import Plugin


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PluginConfig:
    """插件配置"""
    name: str
    enabled: bool
    module_path: str
    config: dict[str, Any]


class PluginManager:
    """插件管理器

    负责动态加载和执行插件。

    Example:
        >>> manager = PluginManager("config/plugins.yaml")
        >>> result = manager.execute_plugin("rollcall", data)
    """

    def __init__(self, config_path: str | Path | None = None):
        """初始化插件管理器

        Args:
            config_path: 插件配置文件路径（YAML格式）
        """
        self.config_path = Path(config_path) if config_path else None
        self.plugins: dict[str, Plugin] = {}

        if self.config_path and self.config_path.exists():
            self._load_plugins()

    def _load_plugins(self) -> None:
        """从配置文件加载所有启用的插件"""
        import yaml

        if not self.config_path:
            logger.warning("未指定配置文件，跳过插件加载")
            return

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return

        plugins_config = config.get("plugins", {})

        for plugin_name, plugin_config in plugins_config.items():
            if not plugin_config.get("enabled", False):
                logger.info(f"插件 {plugin_name} 未启用，跳过")
                continue

            try:
                self._load_plugin(plugin_name, plugin_config)
            except Exception as e:
                logger.error(f"加载插件 {plugin_name} 失败: {e}")

    def _load_plugin(self, name: str, config: dict[str, Any]) -> None:
        """加载单个插件

        Args:
            name: 插件名称
            config: 插件配置
        """
        module_path = config.get("module_path")
        if not module_path:
            raise ValueError(f"插件 {name} 缺少 module_path 配置")

        # 动态导入插件模块
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"无法导入插件模块 {module_path}: {e}")

        # 获取插件类
        plugin_class = getattr(module, "Plugin", None)
        if not plugin_class:
            raise AttributeError(f"插件模块 {module_path} 没有 Plugin 类")

        # 实例化插件
        plugin_instance = plugin_class(config)

        # 验证插件实现了必需的方法
        required_methods = ["execute", "validate", "get_info"]
        for method in required_methods:
            if not hasattr(plugin_instance, method):
                raise AttributeError(f"插件 {name} 缺少必需方法: {method}")

        self.plugins[name] = plugin_instance
        logger.info(f"插件 {name} 加载成功")

    def register_plugin(self, name: str, plugin: Plugin) -> None:
        """手动注册插件（用于测试或动态注册）

        Args:
            name: 插件名称
            plugin: 插件实例
        """
        self.plugins[name] = plugin
        logger.info(f"手动注册插件: {name}")

    def execute_plugin(
        self,
        plugin_name: str,
        data: dict[str, Any]
    ) -> dict[str, Any]:
        """执行指定插件

        Args:
            plugin_name: 插件名称
            data: 输入数据

        Returns:
            dict: 执行结果
                {
                    "success": bool,
                    "message": str,
                    "data": Any (可选)
                }
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return {
                "success": False,
                "message": f"插件不存在: {plugin_name}",
                "available_plugins": list(self.plugins.keys())
            }

        # 验证输入数据
        try:
            if not plugin.validate(data):
                return {
                    "success": False,
                    "message": f"插件 {plugin_name} 数据验证失败"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"数据验证异常: {str(e)}"
            }

        # 执行插件
        try:
            logger.info(f"执行插件: {plugin_name}")
            result = plugin.execute(data)
            logger.info(f"插件 {plugin_name} 执行完成")
            return result
        except Exception as e:
            logger.error(f"插件 {plugin_name} 执行失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"插件执行失败: {str(e)}"
            }

    def list_plugins(self) -> list[dict[str, Any]]:
        """列出所有已加载的插件

        Returns:
            list: 插件信息列表
        """
        return [
            plugin.get_info()
            for plugin in self.plugins.values()
        ]

    def has_plugin(self, name: str) -> bool:
        """检查插件是否已加载

        Args:
            name: 插件名称

        Returns:
            bool: 是否已加载
        """
        return name in self.plugins

    def get_plugin(self, name: str) -> Plugin | None:
        """获取插件实例

        Args:
            name: 插件名称

        Returns:
            Plugin: 插件实例，不存在则返回 None
        """
        return self.plugins.get(name)
