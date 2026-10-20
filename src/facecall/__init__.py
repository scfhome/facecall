"""
点到 FaceCall - 智能课堂考勤系统

一拍即点，秒知到课
深度融合人脸识别与教务系统提交的一体化解决方案
"""

__version__ = "1.0.0"
__author__ = "FaceCall Team"

from facecall.core.workflow import AttendanceWorkflow, AttendanceConfig, AttendanceResult

__all__ = ["AttendanceWorkflow", "AttendanceConfig", "AttendanceResult"]
