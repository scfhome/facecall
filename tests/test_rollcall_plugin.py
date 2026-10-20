"""rollcall 插件单元测试"""

import pytest
from pathlib import Path
import json
import tempfile


# 测试数据
SAMPLE_DATA = {
    "students": [
        {"xh": "20230001", "category": "正常"},
        {"xh": "20230002", "category": "正常"},
        {"xh": "20230003", "category": "旷课", "note": "未检测到"}
    ],
    "course": "体育3",
    "date": "2026-10-20"
}


@pytest.fixture
def plugin_config():
    """测试配置"""
    return {
        "rollcall_cli_path": "../cucn-rollcall-cli/rollcall_auto.py",
        "timeout": 30
    }


@pytest.fixture
def rollcall_plugin(plugin_config):
    """创建插件实例"""
    from hermes_integration.plugins.rollcall.plugin import Plugin
    return Plugin(plugin_config)


class TestRollcallPlugin:
    """Rollcall 插件测试"""

    def test_plugin_info(self, rollcall_plugin):
        """测试插件信息"""
        info = rollcall_plugin.get_info()

        assert info["name"] == "rollcall"
        assert info["version"] == "1.0.0"
        assert "description" in info

    def test_validate_valid_data(self, rollcall_plugin):
        """测试有效数据验证"""
        assert rollcall_plugin.validate(SAMPLE_DATA) is True

    def test_validate_missing_students(self, rollcall_plugin):
        """测试缺少 students 字段"""
        data = SAMPLE_DATA.copy()
        del data["students"]

        assert rollcall_plugin.validate(data) is False

    def test_validate_missing_course(self, rollcall_plugin):
        """测试缺少 course 字段"""
        data = SAMPLE_DATA.copy()
        del data["course"]

        assert rollcall_plugin.validate(data) is False

    def test_validate_invalid_student_format(self, rollcall_plugin):
        """测试学生数据格式错误"""
        data = SAMPLE_DATA.copy()
        data["students"] = [
            {"xh": "20230001"}  # 缺少 category
        ]

        assert rollcall_plugin.validate(data) is False

    def test_create_temp_file(self, rollcall_plugin):
        """测试创建临时文件"""
        students = SAMPLE_DATA["students"]

        temp_file = rollcall_plugin._create_temp_file(students)

        try:
            # 检查文件存在
            assert temp_file.exists()

            # 检查文件内容
            with open(temp_file, encoding="utf-8") as f:
                content = json.load(f)

            assert "students" in content
            assert len(content["students"]) == 3
            assert content["students"][0]["xh"] == "20230001"

        finally:
            # 清理
            temp_file.unlink(missing_ok=True)

    def test_build_command(self, rollcall_plugin):
        """测试命令构建"""
        temp_file = Path("/tmp/test.json")

        cmd = rollcall_plugin._build_command(SAMPLE_DATA, temp_file)

        assert "python3" in cmd
        assert SAMPLE_DATA["date"] in cmd
        assert SAMPLE_DATA["course"] in cmd
        assert str(temp_file) in cmd

    def test_cleanup_temp_file(self, rollcall_plugin):
        """测试临时文件清理"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

        assert temp_path.exists()

        # 清理
        rollcall_plugin._cleanup_temp_file(temp_path)

        # 验证已删除
        assert not temp_path.exists()

    @pytest.mark.integration
    def test_execute_integration(self, rollcall_plugin):
        """集成测试（需要真实的 rollcall CLI）

        此测试需要:
        1. cucn-rollcall-cli 已安装
        2. 配置正确的凭证
        3. 网络连接正常
        """
        pytest.skip("集成测试需要真实环境")

        result = rollcall_plugin.execute(SAMPLE_DATA)

        assert result["success"] is True
        assert "submitted" in result


class TestPluginManager:
    """插件管理器测试"""

    def test_manual_register(self):
        """测试手动注册插件"""
        from facecall.core.plugin_manager import PluginManager
        from hermes_integration.plugins.rollcall.plugin import Plugin

        manager = PluginManager()

        # 手动注册
        plugin = Plugin({"rollcall_cli_path": "test.py", "timeout": 30})
        manager.register_plugin("rollcall", plugin)

        # 验证
        assert manager.has_plugin("rollcall")
        assert manager.get_plugin("rollcall") is not None

    def test_list_plugins(self):
        """测试列出插件"""
        from facecall.core.plugin_manager import PluginManager
        from hermes_integration.plugins.rollcall.plugin import Plugin

        manager = PluginManager()
        plugin = Plugin({"rollcall_cli_path": "test.py", "timeout": 30})
        manager.register_plugin("rollcall", plugin)

        plugins = manager.list_plugins()

        assert len(plugins) == 1
        assert plugins[0]["name"] == "rollcall"

    def test_execute_nonexistent_plugin(self):
        """测试执行不存在的插件"""
        from facecall.core.plugin_manager import PluginManager

        manager = PluginManager()

        result = manager.execute_plugin("nonexistent", {})

        assert result["success"] is False
        assert "不存在" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
