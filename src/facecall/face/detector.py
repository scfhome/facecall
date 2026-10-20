"""
人脸检测模块

使用 DeepFace + RetinaFace 检测器
"""

from typing import List
from pathlib import Path
import numpy as np
from numpy.typing import NDArray

from deepface import DeepFace

from .models import DetectedFace


class FaceDetector:
    """人脸检测器"""

    def __init__(
        self,
        detector_backend: str = "retinaface",
        model_name: str = "Facenet512",
    ) -> None:
        """
        初始化检测器

        Args:
            detector_backend: 检测器类型 (retinaface/opencv/ssd/mtcnn)
            model_name: 特征提取模型 (Facenet512/VGG-Face/ArcFace)
        """
        self.detector_backend = detector_backend
        self.model_name = model_name

    def detect_faces(
        self, img_path: str, min_confidence: float = 0.9
    ) -> List[DetectedFace]:
        """
        检测照片中的所有人脸

        Args:
            img_path: 图片路径
            min_confidence: 最小置信度阈值

        Returns:
            检测到的人脸列表（按位置排序）
        """
        if not Path(img_path).exists():
            raise FileNotFoundError(f"图片不存在: {img_path}")

        # DeepFace 不支持中文路径，先复制到临时位置
        import tempfile
        import shutil
        
        original_path = Path(img_path)
        temp_file = None
        
        # 检查路径是否包含非 ASCII 字符
        try:
            img_path.encode('ascii')
            working_path = img_path  # 路径安全，直接使用
        except UnicodeEncodeError:
            # 路径包含非 ASCII 字符，复制到临时文件
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=original_path.suffix
            )
            temp_file.close()
            shutil.copy2(original_path, temp_file.name)
            working_path = temp_file.name

        # 检测人脸
        try:
            faces_data = DeepFace.extract_faces(
                img_path=working_path,
                detector_backend=self.detector_backend,
                enforce_detection=False,  # 不强制检测（避免单张照片失败）
                align=True,  # 对齐人脸
            )
        except Exception as e:
            raise RuntimeError(f"人脸检测失败: {e}")
        finally:
            # 清理临时文件
            if temp_file:
                Path(temp_file.name).unlink(missing_ok=True)

        # 提取特征向量
        detected_faces: List[DetectedFace] = []

        for face_data in faces_data:
            # 置信度过滤
            confidence = face_data.get("confidence", 1.0)
            if confidence < min_confidence:
                continue

            # 边界框
            facial_area = face_data["facial_area"]
            x = facial_area["x"]
            y = facial_area["y"]
            w = facial_area["w"]
            h = facial_area["h"]
            bbox = (x, y, w, h)
            center_x = x + w // 2
            center_y = y + h // 2

            # 提取特征向量
            try:
                # 使用对齐后的人脸图像
                face_img = face_data["face"]
                representations = DeepFace.represent(
                    img_path=face_img,
                    model_name=self.model_name,
                    enforce_detection=False,
                )
                embedding = np.array(representations[0]["embedding"], dtype=np.float64)

            except Exception as e:
                print(f"⚠️  警告: 特征提取失败 (bbox={bbox}): {e}")
                continue

            # 创建检测对象（face_id 稍后分配）
            detected_faces.append(
                DetectedFace(
                    face_id=0,  # 临时值
                    bbox=bbox,
                    confidence=float(confidence),
                    embedding=embedding,
                    center_x=center_x,
                    center_y=center_y,
                )
            )

        # 按位置排序（从左到右、从上到下）
        sorted_faces = self._sort_by_position(detected_faces)

        # 分配 face_id
        result = []
        for i, face in enumerate(sorted_faces, start=1):
            # 创建新对象（frozen=True 不可变）
            result.append(
                DetectedFace(
                    face_id=i,
                    bbox=face.bbox,
                    confidence=face.confidence,
                    embedding=face.embedding,
                    center_x=face.center_x,
                    center_y=face.center_y,
                )
            )

        return result

    def _sort_by_position(self, faces: List[DetectedFace]) -> List[DetectedFace]:
        """
        按位置排序：从近到远（前排到后排）、从右到左

        算法：
        1. 按 y 坐标分组（容忍 ±50px 视为同一行）
        2. 每行内按 x 坐标倒序排序（从右到左）

        规则说明：
        - y 坐标小 = 近（前排）→ y 坐标大 = 远（后排）
        - x 坐标大 = 右侧 → x 坐标小 = 左侧
        """
        if not faces:
            return []

        # 按 y 坐标排序（从上到下，即从近到远）
        sorted_by_y = sorted(faces, key=lambda f: f.center_y)

        # 分组（同一行）
        rows: List[List[DetectedFace]] = []
        current_row = [sorted_by_y[0]]
        current_y = sorted_by_y[0].center_y
        ROW_TOLERANCE = 50  # 行容忍范围（像素）

        for face in sorted_by_y[1:]:
            if abs(face.center_y - current_y) <= ROW_TOLERANCE:
                # 同一行
                current_row.append(face)
            else:
                # 新行
                rows.append(current_row)
                current_row = [face]
                current_y = face.center_y

        rows.append(current_row)

        # 每行内按 x 坐标倒序排序（从右到左）
        result: List[DetectedFace] = []
        for row in rows:
            sorted_row = sorted(row, key=lambda f: f.center_x, reverse=True)
            result.extend(sorted_row)

        return result

    def detect_single_face(
        self, img_path: str, enforce: bool = True
    ) -> DetectedFace:
        """
        检测单人照中的人脸

        Args:
            img_path: 图片路径
            enforce: 是否强制检测到人脸（True 时未检测到会抛异常）

        Returns:
            检测到的人脸

        Raises:
            RuntimeError: 未检测到人脸或检测到多张人脸
        """
        faces = self.detect_faces(img_path, min_confidence=0.5)

        if len(faces) == 0:
            if enforce:
                raise RuntimeError(f"未检测到人脸: {img_path}")
            # 不强制时返回空特征
            return DetectedFace(
                face_id=1,
                bbox=(0, 0, 0, 0),
                confidence=0.0,
                embedding=np.zeros(512, dtype=np.float64),
                center_x=0,
                center_y=0,
            )

        if len(faces) > 1:
            raise RuntimeError(
                f"检测到多张人脸 ({len(faces)} 张)，请使用单人照: {img_path}"
            )

        return faces[0]
