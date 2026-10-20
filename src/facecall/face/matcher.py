"""
人脸匹配模块

将检测到的人脸与数据库中的特征进行匹配
"""

from typing import List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray
from scipy.spatial.distance import cosine

from .models import FaceRecord, DetectedFace, MatchResult


class FaceMatcher:
    """人脸匹配器"""

    def __init__(
        self,
        database: List[FaceRecord],
        distance_metric: str = "cosine",
        threshold: float = 0.70,
    ) -> None:
        """
        初始化匹配器

        Args:
            database: 人脸数据库
            distance_metric: 距离度量方式 (cosine/euclidean)
            threshold: 匹配阈值（distance <= threshold 视为匹配）
        """
        self.database = database
        self.distance_metric = distance_metric
        self.threshold = threshold

        # 预先提取所有特征向量
        self.database_embeddings = np.array([r.embedding for r in database])
        self.database_xh = [r.xh for r in database]
        self.database_name = [r.name for r in database]

    def match_faces(self, faces: List[DetectedFace]) -> List[MatchResult]:
        """
        批量匹配人脸

        Args:
            faces: 检测到的人脸列表

        Returns:
            匹配结果列表
        """
        results: List[MatchResult] = []

        for face in faces:
            result = self._match_single_face(face)
            results.append(result)

        return results

    def _match_single_face(self, face: DetectedFace) -> MatchResult:
        """
        匹配单张人脸

        Args:
            face: 检测到的人脸

        Returns:
            匹配结果
        """
        if len(self.database) == 0:
            # 空数据库
            return MatchResult(
                face_id=face.face_id,
                xh=None,
                name=None,
                confidence=0.0,
                distance=float("inf"),
                bbox=face.bbox,
                is_certain=False,
            )

        # 计算与所有数据库记录的距离
        distances = self._calculate_distances(face.embedding)

        # 找到最近的匹配
        min_idx = int(np.argmin(distances))
        min_distance = float(distances[min_idx])

        # 判断是否在阈值内
        is_certain = min_distance <= self.threshold

        if is_certain:
            # 匹配成功
            xh = self.database_xh[min_idx]
            name = self.database_name[min_idx]
            # confidence = 1.0 - distance (距离越小置信度越高)
            confidence = max(0.0, 1.0 - min_distance)
        else:
            # 未匹配到
            xh = None
            name = None
            confidence = 0.0

        return MatchResult(
            face_id=face.face_id,
            xh=xh,
            name=name,
            confidence=confidence,
            distance=min_distance,
            bbox=face.bbox,
            is_certain=is_certain,
        )

    def _calculate_distances(self, embedding: NDArray[np.float64]) -> NDArray[np.float64]:
        """
        计算查询向量与数据库所有向量的距离

        Args:
            embedding: 查询特征向量

        Returns:
            距离数组
        """
        if self.distance_metric == "cosine":
            # 余弦距离
            distances = np.array(
                [cosine(embedding, db_emb) for db_emb in self.database_embeddings]
            )
        elif self.distance_metric == "euclidean":
            # 欧氏距离
            distances = np.linalg.norm(self.database_embeddings - embedding, axis=1)
        else:
            raise ValueError(f"不支持的距离度量: {self.distance_metric}")

        return distances

    def get_match_statistics(
        self, match_results: List[MatchResult]
    ) -> dict[str, int]:
        """
        获取匹配统计信息

        Args:
            match_results: 匹配结果列表

        Returns:
            统计字典
        """
        total = len(match_results)
        matched = sum(1 for r in match_results if r.is_certain)
        uncertain = sum(1 for r in match_results if not r.is_certain and r.xh is not None)
        unknown = sum(1 for r in match_results if r.xh is None)

        return {
            "total_faces": total,
            "matched": matched,
            "uncertain": uncertain,
            "unknown": unknown,
        }
