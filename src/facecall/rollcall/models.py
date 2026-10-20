"""教学点名数据模型

定义点名系统中的核心数据结构
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RollCallCategory:
    """点名类别

    Examples:
        到课、请假、旷课、迟到、早退等
    """

    code: str  # 点名类别码 (dmlbm)
    name: str  # 点名类别名称 (dmlbmc)


@dataclass(frozen=True)
class PerformanceCategory:
    """表现类别

    Examples:
        优秀、良好、一般、较差等
    """

    code: str  # 表现类别码 (bxlbm)
    name: str  # 表现类别名称 (bxlbmc)


@dataclass(frozen=True)
class Student:
    """学生信息"""

    xh_id: str  # 学号ID（系统内部ID）
    xh: str  # 学号
    xm: str  # 姓名
    jxdm_id: str  # 教学点名ID（空字符串表示未点名）
    dmlbm: str  # 当前点名类别码
    bxlbm: str  # 当前表现类别码
    bz: str  # 备注

    @property
    def is_rolled(self) -> bool:
        """是否已点名"""
        return bool(self.jxdm_id)


@dataclass(frozen=True)
class Course:
    """课程信息"""

    jxb_id: str  # 教学班ID
    kcmc: str  # 课程名称
    jxbmc: str  # 教学班名称
    jxbrs: int  # 教学班人数
    jgh_id: str  # 教工号ID
    rq: str  # 日期 (YYYY-MM-DD)
    zcd: str  # 周次代码
    xqj: str  # 星期几
    jc: str  # 节次
    qssj: str  # 开始时间 (HH:MM)
    jssj: str  # 结束时间 (HH:MM)
    sksj: str  # 上课时间描述
    jxdd: str  # 教学地点

    def __str__(self) -> str:
        return f"{self.kcmc}({self.jxbmc}) - {self.sksj} @ {self.jxdd}"


@dataclass
class StudentRollCall:
    """学生点名记录（可变）

    用于构建点名提交数据
    """

    student: Student
    category_code: str  # 点名类别码
    performance_code: str = ""  # 表现类别码（可选）
    note: str = ""  # 备注（可选）
