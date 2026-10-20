"""
人脸数据库管理模块

支持单人照和合照建库
"""

from dataclasses import dataclass, replace
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from datetime import datetime
import pickle

import pandas as pd
import numpy as np

from .models import FaceRecord, DetectedFace
from .detector import FaceDetector


class FaceDatabaseBuilder:
    """人脸数据库构建器"""

    def __init__(
        self, detector: Optional[FaceDetector] = None, database_path: Optional[str] = None
    ) -> None:
        """
        初始化构建器

        Args:
            detector: 人脸检测器（None 时使用默认配置）
            database_path: 已有数据库路径（追加模式）
        """
        self.detector = detector if detector else FaceDetector()
        self.database: List[FaceRecord] = []

        # 加载已有数据库
        if database_path and Path(database_path).exists():
            self.database = self.load(database_path)
            print(f"✓ 加载已有数据库: {len(self.database)} 条记录")

    def build_from_group_photo(
        self, photo_path: str, output_preview: str = "annotated_preview.jpg"
    ) -> List[DetectedFace]:
        """
        从合照检测所有人脸

        Args:
            photo_path: 合照路径
            output_preview: 标注预览图输出路径

        Returns:
            检测到的人脸列表（已按位置排序并分配 face_id）
        """
        print(f"\n正在检测合照: {photo_path}")

        # 检测人脸
        faces = self.detector.detect_faces(photo_path, min_confidence=0.9)

        print(f"✓ 检测到 {len(faces)} 张人脸")

        # 生成标注预览图
        from .annotator import ImageAnnotator

        annotator = ImageAnnotator()
        annotator.annotate_faces(photo_path, faces, output_preview)
        print(f"✓ 标注预览已保存: {output_preview}")

        return faces

    def build_from_single_photos(
        self, photos_dir: str, roster_df: pd.DataFrame, mapping_csv: Optional[str] = None
    ) -> int:
        """
        从单人照片目录批量建库

        支持两种模式:
        1. 文件名模式: {学号}_{姓名}.jpg 或 {学号}.jpg
        2. CSV映射模式: 提供 photo_filename,xh,name 映射表

        Args:
            photos_dir: 照片目录
            roster_df: 班级名单 DataFrame (列: xh, name)
            mapping_csv: CSV映射文件路径（可选）

        Returns:
            成功添加的记录数
        """
        photos_path = Path(photos_dir)
        if not photos_path.exists():
            raise FileNotFoundError(f"照片目录不存在: {photos_dir}")

        # 构建学号→姓名映射
        roster_dict = roster_df.set_index("xh")["name"].to_dict()

        # 如果提供了 CSV 映射，使用 CSV 模式
        if mapping_csv:
            return self._build_from_csv_mapping(photos_path, roster_dict, mapping_csv)

        # 否则使用文件名模式
        return self._build_from_filename(photos_path, roster_dict)

    def _build_from_filename(
        self, photos_path: Path, roster_dict: Dict[str, str]
    ) -> int:
        """从文件名解析学号（原有逻辑）"""
        count = 0
        for img_file in photos_path.glob("*"):
            if img_file.suffix.lower() not in [".jpg", ".jpeg", ".png"]:
                continue

            # 解析文件名
            filename = img_file.stem  # 去掉扩展名
            parts = filename.split("_")
            xh = parts[0]

            if xh not in roster_dict:
                print(f"⚠️  跳过: {img_file.name} (学号 {xh} 不在名单中)")
                continue

            name = roster_dict[xh]

            # 检测人脸
            try:
                face = self.detector.detect_single_face(str(img_file), enforce=True)

                # 创建记录
                record = FaceRecord(
                    xh=xh,
                    name=name,
                    embedding=face.embedding,
                    source_photo=str(img_file),
                    face_bbox=None,  # 单人照无需bbox
                    created_at=datetime.now().isoformat(),
                    quality_score=face.confidence,
                )

                self.database.append(record)
                count += 1
                print(f"✓ 添加: {xh} {name} (confidence={face.confidence:.2f})")

            except Exception as e:
                print(f"✗ 失败: {img_file.name} - {e}")

        print(f"\n✓ 批量导入完成: {count} 条记录")
        return count

    def _build_from_csv_mapping(
        self, photos_path: Path, roster_dict: Dict[str, str], mapping_csv: str
    ) -> int:
        """从 CSV 映射表批量导入单人照"""
        print(f"\n正在加载单人照 CSV 映射: {mapping_csv}")

        # 读取 CSV
        try:
            mapping_df = pd.read_csv(mapping_csv)
        except Exception as e:
            raise ValueError(f"CSV 读取失败: {e}")

        # 验证列
        required_cols = ["photo_filename", "xh", "name"]
        for col in required_cols:
            if col not in mapping_df.columns:
                raise ValueError(f"CSV 缺少列: {col}，必须包含: {', '.join(required_cols)}")

        print(f"✓ CSV 验证通过: {len(mapping_df)} 条记录")

        # 批量处理
        count = 0
        for _, row in mapping_df.iterrows():
            photo_filename = str(row["photo_filename"])
            xh = str(row["xh"])
            name = str(row["name"])

            # 验证学号姓名
            if xh not in roster_dict:
                print(f"⚠️  跳过: {photo_filename} (学号 {xh} 不在名单中)")
                continue

            if roster_dict[xh] != name:
                print(f"⚠️  跳过: {photo_filename} (姓名不匹配: CSV={name}, 名单={roster_dict[xh]})")
                continue

            # 查找照片文件
            img_file = photos_path / photo_filename
            if not img_file.exists():
                print(f"✗ 跳过: {photo_filename} (文件不存在)")
                continue

            # 检测人脸
            try:
                face = self.detector.detect_single_face(str(img_file), enforce=True)

                # 创建记录
                record = FaceRecord(
                    xh=xh,
                    name=name,
                    embedding=face.embedding,
                    source_photo=str(img_file),
                    face_bbox=None,
                    created_at=datetime.now().isoformat(),
                    quality_score=face.confidence,
                )

                self.database.append(record)
                count += 1
                print(f"✓ 添加: {xh} {name} (confidence={face.confidence:.2f})")

            except Exception as e:
                print(f"✗ 失败: {photo_filename} - {e}")

        print(f"\n✓ CSV 批量导入完成: {count} 条记录")
        return count

    def add_face_records(
        self,
        faces: List[DetectedFace],
        mapping: List[Tuple[int, str, str]],  # (face_id, xh, name)
        photo_path: str,
    ) -> int:
        """
        添加人脸记录到数据库（合照模式）

        Args:
            faces: 检测到的人脸列表
            mapping: 人脸ID与学生的映射关系
            photo_path: 原始照片路径

        Returns:
            成功添加的记录数
        """
        face_dict = {f.face_id: f for f in faces}
        count = 0

        for face_id, xh, name in mapping:
            if face_id not in face_dict:
                print(f"⚠️  警告: face_id={face_id} 不存在，跳过")
                continue

            face = face_dict[face_id]

            # 检查是否已存在
            if any(r.xh == xh for r in self.database):
                print(f"⚠️  学号 {xh} 已存在，跳过")
                continue

            # 创建记录
            record = FaceRecord(
                xh=xh,
                name=name,
                embedding=face.embedding,
                source_photo=photo_path,
                face_bbox=face.bbox,
                created_at=datetime.now().isoformat(),
                quality_score=face.confidence,
            )

            self.database.append(record)
            count += 1

        print(f"✓ 添加 {count} 条人脸记录")
        return count

    def add_single_record(
        self, xh: str, name: str, photo_path: str
    ) -> None:
        """
        添加单条记录（单人照模式）

        Args:
            xh: 学号
            name: 姓名
            photo_path: 照片路径
        """
        # 检查是否已存在
        if any(r.xh == xh for r in self.database):
            print(f"⚠️  学号 {xh} 已存在，跳过")
            return

        # 检测人脸
        face = self.detector.detect_single_face(photo_path, enforce=True)

        # 创建记录
        record = FaceRecord(
            xh=xh,
            name=name,
            embedding=face.embedding,
            source_photo=photo_path,
            face_bbox=None,
            created_at=datetime.now().isoformat(),
            quality_score=face.confidence,
        )

        self.database.append(record)
        print(f"✓ 添加: {xh} {name} (confidence={face.confidence:.2f})")

    def save(self, output_path: str) -> None:
        """
        保存人脸数据库

        Args:
            output_path: 输出路径
        """
        with open(output_path, "wb") as f:
            pickle.dump(self.database, f)

        print(f"✓ 人脸库已保存: {output_path} ({len(self.database)} 条记录)")

    @staticmethod
    def load(database_path: str) -> List[FaceRecord]:
        """
        加载人脸数据库

        Args:
            database_path: 数据库路径

        Returns:
            人脸记录列表
        """
        with open(database_path, "rb") as f:
            database = pickle.load(f)

        if not isinstance(database, list):
            raise ValueError(f"数据库格式错误: 期望 List[FaceRecord]，实际 {type(database)}")

        return database

    def get_statistics(self) -> Dict[str, int | float]:
        """
        获取数据库统计信息

        Returns:
            统计字典
        """
        if not self.database:
            return {
                "total": 0,
                "avg_quality": 0.0,
                "min_quality": 0.0,
                "max_quality": 0.0,
            }

        qualities = [r.quality_score for r in self.database]

        return {
            "total": len(self.database),
            "avg_quality": float(np.mean(qualities)),
            "min_quality": float(np.min(qualities)),
            "max_quality": float(np.max(qualities)),
        }
