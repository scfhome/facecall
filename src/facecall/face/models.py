"""
数据模型定义

所有数据类使用不可变模式（frozen=True）
"""

from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class DetectedFace:
    """检测到的人脸"""

    face_id: int  # 人脸编号（从1开始）
    bbox: Tuple[int, int, int, int]  # (x, y, w, h) 边界框
    confidence: float  # 检测置信度 [0.0, 1.0]
    embedding: NDArray[np.float64]  # 512维特征向量
    center_x: int  # 中心点 x 坐标（用于排序）
    center_y: int  # 中心点 y 坐标（用于排序）

    def __post_init__(self) -> None:
        """验证数据有效性"""
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError(f"confidence 必须在 [0.0, 1.0] 范围内: {self.confidence}")
        if len(self.embedding) != 512:
            raise ValueError(f"embedding 必须是 512 维: {len(self.embedding)}")


@dataclass(frozen=True)
class FaceRecord:
    """人脸库记录"""

    xh: str  # 学号
    name: str  # 姓名
    embedding: NDArray[np.float64]  # 512维特征向量
    source_photo: str  # 来源照片路径
    face_bbox: Optional[Tuple[int, int, int, int]]  # 原始边界框（单人照为None）
    created_at: str  # 创建时间（ISO格式）
    quality_score: float  # 质量评分 [0.0, 1.0]

    def __post_init__(self) -> None:
        """验证数据有效性"""
        if len(self.embedding) != 512:
            raise ValueError(f"embedding 必须是 512 维: {len(self.embedding)}")
        if self.quality_score < 0.0 or self.quality_score > 1.0:
            raise ValueError(f"quality_score 必须在 [0.0, 1.0] 范围内")


@dataclass(frozen=True)
class MatchResult:
    """人脸匹配结果"""

    face_id: int  # 检测到的人脸编号
    xh: Optional[str]  # 匹配到的学号（未匹配为None）
    name: Optional[str]  # 匹配到的姓名
    confidence: float  # 匹配置信度 [0.0, 1.0]
    distance: float  # 特征距离（越小越相似）
    bbox: Tuple[int, int, int, int]  # 边界框
    is_certain: bool  # 是否确定匹配（confidence >= threshold）

    def to_attendance_category(self) -> str:
        """转换为考勤类别"""
        if self.xh is None:
            return "未知"  # 检测到人脸但未匹配到学生
        if self.is_certain:
            return "正常"
        return "疑问"  # 置信度低，需人工确认


@dataclass(frozen=True)
class AttendanceRecord:
    """考勤记录（兼容 zfsoft-rollcall-cli 格式）"""

    xh: str  # 学号
    category: str  # 考勤类别: 正常/迟到/早退/旷课/请假/疑问/未知
    note: str = ""  # 备注
    confidence: Optional[float] = None  # 识别置信度（可选）

    def to_dict(self) -> dict[str, str | float]:
        """转换为字典格式"""
        result: dict[str, str | float] = {
            "xh": self.xh,
            "category": self.category,
        }
        if self.note:
            result["note"] = self.note
        if self.confidence is not None:
            result["confidence"] = self.confidence
        return result
