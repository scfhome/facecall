"""
Face Attendance CLI - 人脸识别考勤系统

基于 DeepFace 的智能考勤工具，支持单人照和合照建库，
可与 zfsoft-rollcall-cli 无缝集成。
"""

__version__ = "1.0.0"
__author__ = "scfmac"
__license__ = "MIT"

from .models import FaceRecord, DetectedFace
from .database import FaceDatabaseBuilder
from .detector import FaceDetector
from .matcher import FaceMatcher
from .annotator import ImageAnnotator
from .exporter import AttendanceExporter

__all__ = [
    "FaceDatabaseBuilder",
    "FaceRecord",
    "DetectedFace",
    "FaceDetector",
    "FaceMatcher",
    "ImageAnnotator",
    "AttendanceExporter",
]
