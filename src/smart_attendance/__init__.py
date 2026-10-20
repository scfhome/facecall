"""
Smart Attendance System - 智能考勤系统

将人脸识别和教务系统提交深度融合的一体化解决方案
"""

__version__ = "1.0.0"
__author__ = "Smart Attendance Team"

from smart_attendance.core.workflow import AttendanceWorkflow, AttendanceConfig, AttendanceResult

__all__ = ["AttendanceWorkflow", "AttendanceConfig", "AttendanceResult"]
