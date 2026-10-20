"""
图片标注模块

在照片上标注人脸框、编号、姓名等信息
"""

from typing import List
from pathlib import Path
import cv2
import numpy as np

from .models import DetectedFace, MatchResult


class ImageAnnotator:
    """图片标注器"""

    def __init__(
        self,
        box_color: tuple[int, int, int] = (0, 255, 0),  # BGR: 绿色
        text_color: tuple[int, int, int] = (255, 255, 255),  # BGR: 白色
        font_scale: float = 0.6,
        thickness: int = 2,
    ) -> None:
        """
        初始化标注器

        Args:
            box_color: 边框颜色 (BGR)
            text_color: 文字颜色 (BGR)
            font_scale: 字体大小
            thickness: 线条粗细
        """
        self.box_color = box_color
        self.text_color = text_color
        self.font_scale = font_scale
        self.thickness = thickness
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def annotate_faces(
        self,
        img_path: str,
        faces: List[DetectedFace],
        output_path: str,
    ) -> None:
        """
        标注检测到的人脸（建库模式）

        Args:
            img_path: 原始图片路径
            faces: 检测到的人脸列表
            output_path: 输出路径
        """
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {img_path}")

        for face in faces:
            x, y, w, h = face.bbox

            # 绘制边框
            cv2.rectangle(img, (x, y), (x + w, y + h), self.box_color, self.thickness)

            # 绘制编号标签
            label = f"[{face.face_id}]"
            self._draw_text_with_background(
                img, label, (x, y - 10), self.box_color
            )

            # 绘制置信度
            conf_text = f"{face.confidence:.2f}"
            self._draw_text_with_background(
                img,
                conf_text,
                (x, y + h + 20),
                (255, 255, 255),
                font_scale=0.5,
            )

        cv2.imwrite(output_path, img)

    def annotate_matches(
        self,
        img_path: str,
        match_results: List[MatchResult],
        output_path: str,
    ) -> None:
        """
        标注匹配结果（考勤模式）

        Args:
            img_path: 原始图片路径
            match_results: 匹配结果列表
            output_path: 输出路径
        """
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {img_path}")

        for result in match_results:
            x, y, w, h = result.bbox

            # 根据匹配状态选择颜色
            if result.is_certain:
                color = (0, 255, 0)  # 绿色：确定匹配
            elif result.xh is not None:
                color = (0, 165, 255)  # 橙色：不确定
            else:
                color = (0, 0, 255)  # 红色：未知

            # 绘制边框
            cv2.rectangle(img, (x, y), (x + w, y + h), color, self.thickness)

            # 绘制姓名标签
            if result.name:
                label = f"{result.name}"
                self._draw_text_with_background(img, label, (x, y - 10), color)

                # 绘制置信度
                conf_text = f"{result.confidence:.2f}"
                self._draw_text_with_background(
                    img, conf_text, (x, y + h + 20), (255, 255, 255), font_scale=0.5
                )
            else:
                # 未知人脸
                label = "未知"
                self._draw_text_with_background(
                    img, label, (x, y - 10), color
                )

        cv2.imwrite(output_path, img)

    def _draw_text_with_background(
        self,
        img: np.ndarray,
        text: str,
        position: tuple[int, int],
        color: tuple[int, int, int],
        font_scale: float | None = None,
    ) -> None:
        """
        绘制带背景的文字

        Args:
            img: 图像数组
            text: 文字内容
            position: 文字位置 (x, y)
            color: 文字和背景颜色
            font_scale: 字体大小（None 使用默认）
        """
        scale = font_scale if font_scale is not None else self.font_scale
        x, y = position

        # 计算文字大小
        (text_w, text_h), baseline = cv2.getTextSize(
            text, self.font, scale, self.thickness
        )

        # 绘制背景矩形
        cv2.rectangle(
            img,
            (x, y - text_h - baseline),
            (x + text_w, y + baseline),
            color,
            -1,  # 填充
        )

        # 绘制文字
        cv2.putText(
            img,
            text,
            (x, y),
            self.font,
            scale,
            self.text_color,
            self.thickness,
        )
