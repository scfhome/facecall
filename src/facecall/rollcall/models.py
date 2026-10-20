"""教务点名数据模型

从 cucn-rollcall-cli 迁移并简化
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RollCallCategory:
    """点名类别（正常/迟到/旷课/请假等）"""
    code: str  # 点名类别码
    name: str  # 点名类别名称


@dataclass(frozen=True)
class Student:
    """学生考勤记录"""
    xh_id: str  # 学号ID（系统内部ID）
    xh: str  # 学号
    name: str  # 姓名
    category: str  # 考勤类别（正常/迟到/旷课等）
    note: str = ""  # 备注


@dataclass(frozen=True)
class Course:
    """课程信息"""
    jxb_id: str  # 教学班ID
    kcmc: str  # 课程名称
    jxbmc: str  # 教学班名称
    jxbrs: int  # 教学班人数
    rq: str  # 日期 (YYYY-MM-DD)
    sksj: str  # 上课时间描述

    def __str__(self) -> str:
        return f"{self.kcmc}({self.jxbmc}) - {self.sksj}"
