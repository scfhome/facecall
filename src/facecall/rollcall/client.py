"""教务系统 API 客户端

处理登录、会话管理和 API 请求
"""

import time
from dataclasses import dataclass
from typing import Any

import requests

from .crypto import RSAEncryptor, RSAPublicKey


@dataclass(frozen=True)
class LoginCredentials:
    """登录凭据"""

    username: str
    password: str


@dataclass(frozen=True)
class LoginResult:
    """登录结果"""

    success: bool
    message: str
    session_id: str | None = None
    error: str | None = None


class CUCNClient:
    """正方教务系统客户端 (支持V-9.0通用版本)"""

    def __init__(self, base_url: str = "https://jw.cucn.edu.cn"):
        """
        初始化客户端

        Args:
            base_url: 教务系统基础URL（如 https://jw.xxx.edu.cn）
        """
        self.base_url = base_url.rstrip("/")
        self.BASE_URL = f"{self.base_url}/jwglxt"
        self.platform_info = {}

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

    def detect_platform(self) -> dict[str, Any]:
        """
        检测教务系统平台信息

        Returns:
            平台信息字典，包含:
            - is_zfsoft: 是否为正方软件系统
            - version: 版本号（如 V-9.0）
            - vendor: 厂商信息
            - detected: 是否成功检测
        """
        try:
            resp = self.session.get(f"{self.BASE_URL}/xtgl/login_slogin.html", timeout=10)
            resp.raise_for_status()

            html = resp.text

            # 检测正方软件特征
            is_zfsoft = "正方软件" in html or "zfsoft" in html.lower()

            # 提取版本信息
            version = None
            if "V-9.0" in html or "V9.0" in html:
                version = "V-9.0"
            elif "版本" in html:
                import re
                version_match = re.search(r'版本[：:]\s*([V\d\.\-]+)', html)
                if version_match:
                    version = version_match.group(1)

            # 提取厂商信息
            vendor = None
            if "正方软件股份有限公司" in html:
                vendor = "正方软件股份有限公司"
            elif "正方软件" in html:
                vendor = "正方软件"

            self.platform_info = {
                "is_zfsoft": is_zfsoft,
                "version": version,
                "vendor": vendor,
                "base_url": self.base_url,
                "detected": True
            }

            return self.platform_info

        except Exception as e:
            self.platform_info = {
                "is_zfsoft": None,
                "version": None,
                "vendor": None,
                "base_url": self.base_url,
                "detected": False,
                "error": str(e)
            }
            return self.platform_info

    def _get_timestamp(self) -> int:
        """获取当前时间戳（毫秒）"""
        return int(time.time() * 1000)

    def _get_public_key(self) -> RSAPublicKey:
        """获取 RSA 公钥"""
        timestamp = self._get_timestamp()
        params = {"time": timestamp, "_": timestamp - 1000}

        resp = self.session.get(
            f"{self.BASE_URL}/xtgl/login_getPublicKey.html", params=params, timeout=10
        )
        resp.raise_for_status()

        data = resp.json()
        return RSAPublicKey(modulus=data["modulus"], exponent=data["exponent"])

    def _get_csrf_token(self) -> str:
        """访问登录页获取 CSRF token"""
        resp = self.session.get(f"{self.BASE_URL}/xtgl/login_slogin.html", timeout=10)
        resp.raise_for_status()

        # 从页面提取 csrftoken（简化处理：生成固定格式）
        # 实际生产环境应从 HTML 解析
        import uuid

        token_uuid = str(uuid.uuid4())
        token_compact = token_uuid.replace("-", "")
        return f"{token_uuid},{token_compact}"

    def login(self, credentials: LoginCredentials) -> LoginResult:
        """
        登录教务系统

        Args:
            credentials: 登录凭据

        Returns:
            登录结果
        """
        try:
            # 步骤 1: 访问登录页获取初始会话
            csrf_token = self._get_csrf_token()

            # 步骤 2: 获取 RSA 公钥
            public_key = self._get_public_key()

            # 步骤 3: 加密密码
            encryptor = RSAEncryptor(public_key)
            encrypted_password = encryptor.encrypt(credentials.password)

            # 步骤 4: 提交登录（密码参数需重复提交两次）
            timestamp = self._get_timestamp()

            # 手动构建表单数据（确保 mm 参数重复）
            form_parts = [
                f"csrftoken={requests.utils.quote(csrf_token)}",
                f"yhm={credentials.username}",
                f"mm={requests.utils.quote(encrypted_password)}",
                f"mm={requests.utils.quote(encrypted_password)}",
                "language=zh_CN",
            ]
            form_body = "&".join(form_parts)

            resp = self.session.post(
                f"{self.BASE_URL}/xtgl/login_slogin.html",
                params={"time": timestamp},
                data=form_body,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
                allow_redirects=True,
            )

            # 检查登录是否成功（通过 Cookie 中的 JSESSIONID 判断）
            session_id = self.session.cookies.get("JSESSIONID")

            if resp.status_code == 200 and session_id:
                return LoginResult(success=True, message="登录成功", session_id=session_id)
            else:
                return LoginResult(
                    success=False,
                    message="登录失败",
                    error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                )

        except requests.RequestException as e:
            return LoginResult(success=False, message="网络请求失败", error=str(e))
        except (ValueError, KeyError) as e:
            return LoginResult(success=False, message="数据解析失败", error=str(e))

    def activate_module(self, module_code: str = "N254350") -> tuple[bool, str]:
        """
        激活功能模块（例如教师点名模块）

        Args:
            module_code: 模块代码，默认 N254350（教师点名）

        Returns:
            (成功标志, 消息)
        """
        try:
            resp = self.session.post(
                f"{self.BASE_URL}/xtgl/index_cxBczjsygnmk.html",
                params={"gnmkdm": "index"},
                data={"gndm": module_code},
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
                timeout=10,
            )
            resp.raise_for_status()

            return True, resp.text

        except requests.RequestException as e:
            return False, str(e)

    def get_user_info(self) -> dict[str, Any]:
        """获取当前用户信息（示例接口）"""
        try:
            resp = self.session.get(f"{self.BASE_URL}/xtgl/index_initMenu.html", timeout=10)
            resp.raise_for_status()
            return {"status": "logged_in", "content_length": len(resp.text)}
        except requests.RequestException as e:
            return {"status": "error", "error": str(e)}

    def get_courses_by_date(self, date: str) -> dict[str, Any]:
        """
        查询指定日期的课程列表

        Args:
            date: 日期字符串，格式 YYYY-MM-DD（如 2026-10-20）

        Returns:
            包含课程列表或错误信息的字典
        """
        try:
            resp = self.session.post(
                f"{self.BASE_URL}/jxdmgl/jsjxdm_cxKcListByRq.html",
                params={"gnmkdm": "N254350"},
                data={"rq": date},
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
                timeout=10,
            )
            resp.raise_for_status()

            courses = resp.json()
            return {"success": True, "courses": courses, "count": len(courses)}

        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
        except (ValueError, KeyError) as e:
            return {"success": False, "error": f"数据解析失败: {e}"}

    def get_class_periods(
        self, jxb_id: str, date: str, jgh_id: str, zcd: int
    ) -> dict[str, Any]:
        """
        查询指定教学班在某日期的节次列表（包含考勤录入状态）

        Args:
            jxb_id: 教学班ID
            date: 日期字符串，格式 YYYY-MM-DD
            jgh_id: 教工号ID
            zcd: 周次代码

        Returns:
            包含节次列表或错误信息的字典
        """
        try:
            resp = self.session.post(
                f"{self.BASE_URL}/jxdmgl/jsjxdm_cxJcListByRqJxbid.html",
                params={"gnmkdm": "N254350"},
                data={"jxb_id": jxb_id, "rq": date, "jgh_id": jgh_id, "zcd": zcd},
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
                timeout=10,
            )
            resp.raise_for_status()

            periods = resp.json()
            return {"success": True, "periods": periods, "count": len(periods)}

        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
        except (ValueError, KeyError) as e:
            return {"success": False, "error": f"数据解析失败: {e}"}

    def get_student_list(
        self, jxb_id: str, date: str, jgh_id: str, jc: int, xh: str = "", qdfs: str = ""
    ) -> dict[str, Any]:
        """
        查询教学班学生花名册

        Args:
            jxb_id: 教学班ID
            date: 日期字符串
            jgh_id: 教工号ID
            jc: 节次代码
            xh: 学号（可选，用于筛选）
            qdfs: 签到方式（可选）

        Returns:
            包含学生列表或错误信息的字典
        """
        try:
            resp = self.session.post(
                f"{self.BASE_URL}/jxdmgl/jsjxdm_cxJxbxxByJxbid.html",
                params={"gnmkdm": "N254350"},
                data={"jxb_id": jxb_id, "rq": date, "jgh_id": jgh_id, "jc": jc, "xh": xh, "qdfs": qdfs},
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
                timeout=10,
            )
            resp.raise_for_status()

            students = resp.json()
            return {"success": True, "students": students, "count": len(students)}

        except requests.RequestException as e:
            return {"success": False, "error": str(e)}
        except (ValueError, KeyError) as e:
            return {"success": False, "error": f"数据解析失败: {e}"}
