"""
优化的人脸匹配器 - 使用匈牙利算法实现一对一最优匹配
"""
from dataclasses import dataclass, replace
from typing import List, Optional, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment

from .models import FaceRecord, DetectedFace


@dataclass(frozen=True)
class MatchResult:
    """匹配结果（优化版）"""
    
    face_id: int  # 检测到的人脸编号
    xh: Optional[str]  # 匹配到的学号（未匹配为None）
    name: Optional[str]  # 匹配到的姓名
    confidence: float  # 匹配置信度 [0.0, 1.0]
    distance: float  # 特征距离（越小越相似）
    bbox: Tuple[int, int, int, int]  # 边界框
    match_quality: str  # "high", "medium", "low", "unknown"
    needs_review: bool  # 是否需要人工审核
    alternative_matches: Tuple[Tuple[str, str, float], ...]  # 备选匹配 ((xh, name, conf),...)
    
    def to_attendance_category(self) -> str:
        """转换为考勤类别"""
        if self.xh is None:
            return "未知"
        if self.match_quality == "high":
            return "正常"
        elif self.match_quality == "medium":
            return "正常"
        elif self.match_quality == "low":
            return "待确认"
        else:
            return "未知"


@dataclass(frozen=True)
class AbsentStudent:
    """缺席学生"""
    
    xh: str
    name: str
    reason: str = "未检测到"  # "未检测到" or "低置信度"


class HungarianMatcher:
    """
    基于匈牙利算法的一对一人脸匹配器
    
    特性:
    - 全局最优匹配（最小化总距离）
    - 一对一约束（每个人脸最多匹配一个学生）
    - 自适应阈值（根据数据质量动态调整）
    - 匹配质量分级（high/medium/low/unknown）
    - 备选匹配（用于人工审核）
    """
    
    def __init__(
        self,
        database: List[FaceRecord],
        threshold: float = 0.60,
        use_adaptive_threshold: bool = True
    ):
        """
        Args:
            database: 人脸数据库
            threshold: 基础阈值（余弦距离，越小越相似）
            use_adaptive_threshold: 是否使用自适应阈值
        """
        if not database:
            raise ValueError("数据库不能为空")
        
        self.database = tuple(database)  # 不可变
        self.base_threshold = threshold
        self.use_adaptive = use_adaptive_threshold
    
    def match_faces(
        self,
        detected_faces: List[DetectedFace]
    ) -> Tuple[List[MatchResult], List[AbsentStudent]]:
        """
        使用匈牙利算法进行最优一对一匹配
        
        Args:
            detected_faces: 检测到的人脸列表
        
        Returns:
            (匹配结果列表, 缺席学生列表)
        """
        if not detected_faces:
            # 所有学生缺席
            absent = [
                AbsentStudent(xh=s.xh, name=s.name, reason="未检测到人脸")
                for s in self.database
            ]
            return [], absent
        
        # 1. 构建代价矩阵
        cost_matrix = self._build_cost_matrix(detected_faces)
        
        # 2. 应用匈牙利算法（找最优分配）
        # face_indices 和 student_indices 是对应的索引
        face_indices, student_indices = linear_sum_assignment(cost_matrix)
        
        # 3. 计算自适应阈值
        threshold = self._compute_threshold(cost_matrix, face_indices, student_indices)
        
        # 4. 构建匹配结果
        results = []
        matched_students = set()
        
        # 处理匈牙利算法分配的匹配
        for face_idx, student_idx in zip(face_indices, student_indices):
            face = detected_faces[face_idx]
            student = self.database[student_idx]
            distance = cost_matrix[face_idx, student_idx]
            confidence = 1.0 - distance
            
            if distance <= threshold:
                # 有效匹配
                quality = self._classify_quality(confidence)
                needs_review = (quality == "low")
                
                # 找备选匹配（排除当前学生）
                alternatives = self._find_alternatives(
                    face,
                    cost_matrix,
                    face_idx,
                    exclude_idx=student_idx,
                    top_k=3
                )
                
                result = MatchResult(
                    face_id=face.face_id,
                    xh=student.xh,
                    name=student.name,
                    confidence=confidence,
                    distance=distance,
                    bbox=face.bbox,
                    match_quality=quality,
                    needs_review=needs_review,
                    alternative_matches=alternatives
                )
                matched_students.add(student.xh)
            else:
                # 距离太大，标记为未知
                # 仍然提供最接近的学生作为参考
                alternatives = self._find_alternatives(
                    face,
                    cost_matrix,
                    face_idx,
                    exclude_idx=None,
                    top_k=3
                )
                
                result = MatchResult(
                    face_id=face.face_id,
                    xh=None,
                    name=None,
                    confidence=confidence,
                    distance=distance,
                    bbox=face.bbox,
                    match_quality="unknown",
                    needs_review=True,
                    alternative_matches=alternatives
                )
            
            results.append(result)
        
        # 5. 处理未分配的人脸（当人脸数 > 学生数）
        assigned_face_ids = set(face_indices)
        for i, face in enumerate(detected_faces):
            if i not in assigned_face_ids:
                # 这张人脸未被匈牙利算法分配（多余的人脸）
                alternatives = self._find_alternatives(
                    face,
                    cost_matrix,
                    i,
                    exclude_idx=None,
                    top_k=3
                )
                
                result = MatchResult(
                    face_id=face.face_id,
                    xh=None,
                    name=None,
                    confidence=0.0,
                    distance=1.0,
                    bbox=face.bbox,
                    match_quality="unknown",
                    needs_review=True,
                    alternative_matches=alternatives
                )
                results.append(result)
        
        # 6. 标记缺席学生
        absent_students = [
            AbsentStudent(xh=s.xh, name=s.name, reason="未检测到")
            for s in self.database
            if s.xh not in matched_students
        ]
        
        # 按face_id排序结果
        results.sort(key=lambda r: r.face_id)
        
        return results, absent_students
    
    def _build_cost_matrix(
        self,
        detected_faces: List[DetectedFace]
    ) -> np.ndarray:
        """
        构建代价矩阵 (n_faces × n_students)
        cost[i, j] = 人脸i 与 学生j 的余弦距离
        """
        n_faces = len(detected_faces)
        n_students = len(self.database)
        
        cost_matrix = np.zeros((n_faces, n_students), dtype=np.float32)
        
        for i, face in enumerate(detected_faces):
            for j, student in enumerate(self.database):
                distance = self._cosine_distance(
                    face.embedding,
                    student.embedding
                )
                cost_matrix[i, j] = distance
        
        return cost_matrix
    
    def _compute_threshold(
        self,
        cost_matrix: np.ndarray,
        face_indices: np.ndarray,
        student_indices: np.ndarray
    ) -> float:
        """计算自适应阈值"""
        if not self.use_adaptive:
            return self.base_threshold
        
        # 获取匈牙利算法分配的距离
        assigned_distances = [
            cost_matrix[f_idx, s_idx]
            for f_idx, s_idx in zip(face_indices, student_indices)
        ]
        
        if not assigned_distances:
            return self.base_threshold
        
        # 转换为置信度
        confidences = [1.0 - d for d in assigned_distances]
        
        # 统计分析
        median = float(np.median(confidences))
        std = float(np.std(confidences))
        
        # 自适应阈值: median - 1.0 * std
        # 对应的距离阈值
        adaptive_conf = median - 1.0 * std
        adaptive_dist = 1.0 - adaptive_conf
        
        # 限制范围
        # 置信度范围 [0.50, 0.85] -> 距离范围 [0.15, 0.50]
        adaptive_dist = max(0.15, min(0.50, adaptive_dist))
        
        return adaptive_dist
    
    @staticmethod
    def _classify_quality(confidence: float) -> str:
        """分类匹配质量"""
        if confidence >= 0.80:
            return "high"
        elif confidence >= 0.65:
            return "medium"
        elif confidence >= 0.50:
            return "low"
        else:
            return "unknown"
    
    def _find_alternatives(
        self,
        face: DetectedFace,
        cost_matrix: np.ndarray,
        face_idx: int,
        exclude_idx: Optional[int],
        top_k: int
    ) -> Tuple[Tuple[str, str, float], ...]:
        """
        找到备选匹配（用于人工审核）
        
        Returns:
            ((xh, name, confidence), ...)
        """
        alternatives = []
        
        for j, student in enumerate(self.database):
            if exclude_idx is not None and j == exclude_idx:
                continue
            
            distance = cost_matrix[face_idx, j]
            confidence = 1.0 - distance
            alternatives.append((student.xh, student.name, confidence))
        
        # 按置信度排序，返回前k个
        alternatives.sort(key=lambda x: x[2], reverse=True)
        return tuple(alternatives[:top_k])
    
    @staticmethod
    def _cosine_distance(emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        计算余弦距离
        
        distance = 1 - similarity
        similarity = cos(θ) = (a · b) / (||a|| ||b||)
        """
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 1.0  # 最大距离
        
        similarity = np.dot(emb1, emb2) / (norm1 * norm2)
        distance = 1.0 - similarity
        
        return float(distance)


# 兼容性：保留旧的接口名
FaceMatcher = HungarianMatcher
