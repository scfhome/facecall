"""测试 rollcall 模块的数据模型"""

import pytest
from facecall.rollcall.models import Student, Course, RollCallCategory


def test_student_creation():
    """测试学生对象创建"""
    student = Student(
        xh_id="202301010001",
        xh="20230101",
        name="张三",
        category="正常",
        note=""
    )
    assert student.xh == "20230101"
    assert student.name == "张三"
    assert student.category == "正常"


def test_student_immutable():
    """测试学生对象不可变性"""
    student = Student(
        xh_id="202301010001",
        xh="20230101",
        name="张三",
        category="正常",
        note=""
    )
    with pytest.raises(AttributeError):
        student.xh = "99999999"  # frozen dataclass 不允许修改


def test_rollcall_category():
    """测试点名类别"""
    normal = RollCallCategory(code="01", name="正常")
    assert normal.code == "01"
    assert normal.name == "正常"
    
    absent = RollCallCategory(code="04", name="旷课")
    assert absent.code == "04"
    assert absent.name == "旷课"


def test_course_str_representation():
    """测试课程的字符串表示"""
    course = Course(
        jxb_id="5520774D89B36278E065000000000001",
        kcmc="体育3",
        jxbmc="234拓展女-1",
        jxbrs=37,
        rq="2026-10-20",
        sksj="星期二第3-4节{1-4周,7-17周}",
    )
    assert "体育3" in str(course)
    assert "234拓展女-1" in str(course)
