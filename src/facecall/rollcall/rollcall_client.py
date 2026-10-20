"""教学点名客户端

处理点名相关的 API 请求
"""

from typing import Any

import requests

from .client import CUCNClient
from .models import (
    Course,
    PerformanceCategory,
    RollCallCategory,
    Student,
    StudentRollCall,
)


class RollCallClient:
    """教学点名专用客户端"""

    def __init__(self, base_client: CUCNClient):
        """
        初始化点名客户端

        Args:
            base_client: 已登录的基础客户端
        """
        self.client = base_client
        self.categories: list[RollCallCategory] = []
        self.performances: list[PerformanceCategory] = []

    def load_categories(self) -> tuple[bool, str]:
        """
        加载点名类别和表现类别

        Returns:
            (成功标志, 消息)
        """
        try:
            # 加载点名类别
            resp = self.client.session.post(
                f"{self.client.BASE_URL}/jxdmgl/jsjxdm_cxDmlbList.html",
                params={"gnmkdm": "N254350"},
                timeout=10,
            )
            resp.raise_for_status()
            dmlb_data = resp.json()

            self.categories = [
                RollCallCategory(code=item["dmlbm"], name=item["dmlbmc"])
                for item in dmlb_data
            ]

            # 加载表现类别
            resp = self.client.session.post(
                f"{self.client.BASE_URL}/jxdmgl/jsjxdm_cxBxlbList.html",
                params={"gnmkdm": "N254350"},
                timeout=10,
            )
            resp.raise_for_status()
            bxlb_data = resp.json()

            self.performances = [
                PerformanceCategory(code=item["bxlbm"], name=item["bxlbmc"])
                for item in bxlb_data
            ]

            return True, f"已加载 {len(self.categories)} 个点名类别，{len(self.performances)} 个表现类别"

        except requests.RequestException as e:
            return False, f"网络请求失败: {e}"
        except (ValueError, KeyError) as e:
            return False, f"数据解析失败: {e}"

    def get_lesson_periods(self, course: Course) -> dict[str, Any]:
        """
        查询课程的节次列表

        Args:
            course: 课程信息

        Returns:
            包含节次列表或错误信息的字典
        """
        try:
            resp = self.client.session.post(
                f"{self.client.BASE_URL}/jxdmgl/jsjxdm_cxJcListByRqJxbid.html",
                params={"gnmkdm": "N254350"},
                data={
                    "jxb_id": course.jxb_id,
                    "rq": course.rq,
                    "jgh_id": course.jgh_id,
                    "zcd": course.zcd,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
                timeout=10,
            )
            resp.raise_for_status()

            periods_data = resp.json()
            if periods_data and len(periods_data) > 0:
                # 返回第一个节次（通常一门课只有一个节次）
                period = periods_data[0]
                return {
                    "success": True,
                    "jc": str(period.get("jc", "")),
                    "qssj": period.get("qssj", ""),
                    "jssj": period.get("jssj", ""),
                    "jcm": period.get("jcm", ""),
                }
            else:
                return {"success": False, "error": "未找到节次信息"}

        except requests.RequestException as e:
            return {"success": False, "error": f"网络请求失败: {e}"}
        except (ValueError, KeyError) as e:
            return {"success": False, "error": f"数据解析失败: {e}"}

    def get_students(self, course: Course) -> dict[str, Any]:
        """
        获取课程的学生列表

        Args:
            course: 课程信息

        Returns:
            包含学生列表或错误信息的字典
        """
        try:
            # 如果课程没有节次信息，先查询节次
            jc = course.jc
            if not jc:
                periods_result = self.get_lesson_periods(course)
                if periods_result["success"]:
                    jc = periods_result["jc"]
                else:
                    return {
                        "success": False,
                        "error": f"无法获取节次信息: {periods_result.get('error')}",
                    }

            resp = self.client.session.post(
                f"{self.client.BASE_URL}/jxdmgl/jsjxdm_cxJxbxxByJxbid.html",
                params={"gnmkdm": "N254350"},
                data={
                    "jxb_id": course.jxb_id,
                    "rq": course.rq,
                    "jgh_id": course.jgh_id,
                    "zcd": course.zcd,
                    "jc": jc,
                    "xh": "",  # 不筛选学号
                    "qdfs": "",  # 签到方式
                },
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
                timeout=10,
            )
            resp.raise_for_status()

            students_data = resp.json()
            students = [
                Student(
                    xh_id=s["xh_id"],
                    xh=s["xh"],
                    xm=s["xm"],
                    jxdm_id=s.get("jxdm_id", ""),
                    dmlbm=s.get("dmlbm", ""),
                    bxlbm=s.get("bxlbm", ""),
                    bz=s.get("bz", ""),
                )
                for s in students_data
            ]

            return {"success": True, "students": students, "count": len(students)}

        except requests.RequestException as e:
            return {"success": False, "error": f"网络请求失败: {e}"}
        except (ValueError, KeyError) as e:
            return {"success": False, "error": f"数据解析失败: {e}"}

    def submit_rollcall(
        self, course: Course, records: list[StudentRollCall]
    ) -> dict[str, Any]:
        """
        提交点名记录

        Args:
            course: 课程信息
            records: 学生点名记录列表

        Returns:
            提交结果字典
        """
        if not records:
            return {"success": False, "error": "无学生信息可提交"}

        try:
            # 如果课程没有节次信息，先查询节次
            jc = course.jc
            qssj = course.qssj
            jssj = course.jssj

            if not jc:
                periods_result = self.get_lesson_periods(course)
                if periods_result["success"]:
                    jc = periods_result["jc"]
                    qssj = periods_result.get("qssj", "")
                    jssj = periods_result.get("jssj", "")
                else:
                    return {
                        "success": False,
                        "error": f"无法获取节次信息: {periods_result.get('error')}",
                    }

            # 构建请求数据
            data = {
                "jxb_id": course.jxb_id,
                "rq": course.rq,
                "zc": course.zcd,
                "jc": jc,
                "xqj": course.xqj,
                "jgh_id": course.jgh_id,
                "qssj": qssj,
                "jssj": jssj,
                "sftjjxrz": "false",  # 是否提交教学日志
            }

            # 添加学生点名记录
            for index, record in enumerate(records):
                prefix = f"modelList[{index}]"
                data[f"{prefix}.jxdm_id"] = record.student.jxdm_id
                data[f"{prefix}.jxb_id"] = course.jxb_id
                data[f"{prefix}.xh_id"] = record.student.xh_id
                data[f"{prefix}.dmlbm"] = record.category_code
                data[f"{prefix}.bxlbm"] = record.performance_code
                data[f"{prefix}.bz"] = record.note
                data[f"{prefix}.rq"] = course.rq
                data[f"{prefix}.zc"] = course.zcd
                data[f"{prefix}.jc"] = jc
                data[f"{prefix}.xqj"] = course.xqj

            # 提交
            resp = self.client.session.post(
                f"{self.client.BASE_URL}/jxdmgl/jsjxdm_tjDmxx.html",
                params={"gnmkdm": "N254350"},
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
                timeout=30,
            )
            resp.raise_for_status()

            result = resp.json()
            return {
                "success": result.get("status") == "success",
                "message": result.get("message", "提交完成"),
                "raw_response": result,
            }

        except requests.RequestException as e:
            return {"success": False, "error": f"网络请求失败: {e}"}
        except (ValueError, KeyError) as e:
            return {"success": False, "error": f"数据解析失败: {e}"}

    def get_category_by_name(self, name: str) -> RollCallCategory | None:
        """
        根据名称查找点名类别

        Args:
            name: 类别名称（如"到课"、"请假"）

        Returns:
            找到的类别，未找到返回 None
        """
        for cat in self.categories:
            if cat.name == name:
                return cat
        return None

    def get_category_by_code(self, code: str) -> RollCallCategory | None:
        """根据代码查找点名类别"""
        for cat in self.categories:
            if cat.code == code:
                return cat
        return None

    def get_default_category(self) -> RollCallCategory | None:
        """获取默认点名类别（到课）"""
        return self.get_category_by_name("到课")

    def parse_course_from_api(self, course_data: dict) -> Course:
        """
        从 API 响应解析课程对象

        Args:
            course_data: API 返回的课程数据

        Returns:
            Course 对象
        """
        return Course(
            jxb_id=course_data["jxb_id"],
            kcmc=course_data["kcmc"],
            jxbmc=course_data["jxbmc"],
            jxbrs=int(course_data["jxbrs"]),
            jgh_id=course_data["jgh_id"],
            rq=course_data["rq"],
            zcd=str(course_data["zcd"]),
            xqj=str(course_data.get("xqj", "")),
            jc=course_data.get("jc", ""),
            qssj=course_data.get("qssj", ""),
            jssj=course_data.get("jssj", ""),
            sksj=course_data.get("sksj", ""),
            jxdd=course_data.get("jxdd", ""),
        )
