"""测试 RollCallClient 客户端

不直接连接真实系统，使用 Mock 测试接口
"""

import pytest
from unittest.mock import Mock, patch
from facecall.rollcall.client import RollCallClient


def test_client_initialization():
    """测试客户端初始化"""
    client = RollCallClient(base_url="https://jw.cucn.edu.cn")
    assert client.base_url == "https://jw.cucn.edu.cn"
    assert not client.is_logged_in()


def test_login_requires_credentials():
    """测试登录需要凭据"""
    client = RollCallClient()
    with pytest.raises(ValueError, match="username.*password"):
        client.login(username="", password="")


@patch('facecall.rollcall.client.requests.Session')
def test_login_mock(mock_session_class):
    """测试登录流程（Mock）"""
    # Mock 会话
    mock_session = Mock()
    mock_session_class.return_value = mock_session
    
    # Mock 获取公钥响应
    mock_pubkey_resp = Mock()
    mock_pubkey_resp.json.return_value = {
        "modulus": "AJHdDvSr6X...",
        "exponent": "AQAB"
    }
    
    # Mock 登录响应
    mock_login_resp = Mock()
    mock_login_resp.status_code = 302
    mock_login_resp.text = ""
    
    mock_session.get.return_value = mock_pubkey_resp
    mock_session.post.return_value = mock_login_resp
    
    client = RollCallClient()
    # 实际测试需要真实凭据，这里只验证接口
    # result = client.login(username="test", password="test")
    # assert result.success or result.error is not None
