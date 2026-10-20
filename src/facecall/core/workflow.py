"""
点到 FaceCall - 核心工作流

职责：
1. 协调人脸识别模块和教务系统模块
2. 管理数据在各模块间的流转
3. 处理人工审核流程
4. 统一错误处理
"""

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path
import time


@dataclass(frozen=True)
class AttendanceConfig:
    """考勤配置"""
    photo_path: Path
    database_path: Path
    roster_path: Path
    course_name: str
    date: str
    threshold: float = 0.70
    auto_submit: bool = True
    review_uncertain: bool = True


@dataclass(frozen=True)
class StudentAttendance:
    """单个学生的考勤记录"""
    xh: str  # 学号
    name: str  # 姓名
    category: str  # 考勤类别
    confidence: float = 1.0  # 识别置信度
    note: str = ""  # 备注


@dataclass(frozen=True)
class AttendanceResult:
    """考勤结果"""
    success: bool
    total: int
    submitted: int
    uncertain: int
    absent: int
    duration: float
    message: str
    students: List[StudentAttendance]
    annotated_image: Optional[Path] = None

    def to_dict(self) -> dict:
        """转换为字典（用于JSON序列化）"""
        return {
            "success": self.success,
            "total": self.total,
            "submitted": self.submitted,
            "uncertain": self.uncertain,
            "absent": self.absent,
            "duration": self.duration,
            "message": self.message,
            "students": [
                {
                    "xh": s.xh,
                    "name": s.name,
                    "category": s.category,
                    "confidence": s.confidence,
                    "note": s.note,
                }
                for s in self.students
            ],
            "annotated_image": str(self.annotated_image) if self.annotated_image else None,
        }


class AttendanceWorkflow:
    """考勤工作流编排器"""

    def __init__(self, config: AttendanceConfig):
        self.config = config
        self._start_time = None

        # 延迟导入，避免循环依赖
        from facecall.face import FaceRecognizer
        from facecall.rollcall import RollCallClient

        # 初始化人脸识别器
        self.face_recognizer = FaceRecognizer(
            database_path=config.database_path,
            roster_path=config.roster_path,
            threshold=config.threshold,
        )

        # 初始化教务系统客户端
        self.rollcall_client = RollCallClient() if config.auto_submit else None

    def execute(self) -> AttendanceResult:
        """
        执行完整的考勤工作流

        流程:
        1. 人脸识别
        2. 人工审核（可选）
        3. 提交教务系统（可选）
        4. 返回结果
        """
        self._start_time = time.time()

        try:
            # Stage 1: 人脸识别
            print("🔍 正在识别人脸...")
            recognition_result = self._recognize_faces()
            print(f"✅ 识别完成: {len(recognition_result.students)} 人")

            # Stage 2: 人工审核（如果需要）
            if self.config.review_uncertain and recognition_result.has_uncertain():
                print(f"⚠️  检测到 {recognition_result.uncertain_count()} 个不确定项")
                confirmed_result = self._review_uncertain(recognition_result)
            else:
                confirmed_result = recognition_result

            # Stage 3: 提交教务系统（如果启用）
            if self.config.auto_submit:
                print("📤 正在提交到教务系统...")
                submit_result = self._submit_to_system(confirmed_result)
                print(f"✅ 提交成功: {submit_result.submitted}/{submit_result.total} 人")
            else:
                submit_result = confirmed_result
                print("⏸️  已跳过提交（--no-submit）")

            duration = time.time() - self._start_time

            return AttendanceResult(
                success=True,
                total=len(submit_result.students),
                submitted=len([s for s in submit_result.students if s.category != "旷课"]),
                uncertain=submit_result.uncertain_count(),
                absent=len([s for s in submit_result.students if s.category == "旷课"]),
                duration=duration,
                message="考勤完成",
                students=submit_result.students,
                annotated_image=submit_result.annotated_image,
            )

        except Exception as e:
            duration = time.time() - self._start_time
            return AttendanceResult(
                success=False,
                total=0,
                submitted=0,
                uncertain=0,
                absent=0,
                duration=duration,
                message=f"考勤失败: {str(e)}",
                students=[],
            )

    def _recognize_faces(self) -> 'RecognitionResult':
        """执行人脸识别"""
        result = self.face_recognizer.recognize(
            photo_path=self.config.photo_path,
            output_annotated=True,
        )
        return result

    def _review_uncertain(self, result: 'RecognitionResult') -> 'RecognitionResult':
        """
        人工审核不确定项

        TODO: 实现交互式审核
        - 显示标注图片
        - 列出不确定学生
        - 询问用户确认/修正
        """
        print("\n⚠️  不确定项:")
        for student in result.uncertain_students():
            print(f"  - {student.xh} {student.name} (相似度: {student.confidence:.2f})")

        # 简单处理：询问用户是否继续
        confirm = input("\n是否继续提交？(y/n): ").lower()
        if confirm != 'y':
            raise ValueError("用户取消提交")

        return result

    def _submit_to_system(self, result: 'RecognitionResult') -> 'RecognitionResult':
        """提交到教务系统"""
        if not self.rollcall_client:
            raise ValueError("RollCallClient 未初始化")

        # 构建提交数据
        students_data = [
            {
                "xh": s.xh,
                "category": s.category,
                "note": s.note,
            }
            for s in result.students
        ]

        # 提交
        self.rollcall_client.submit_attendance(
            date=self.config.date,
            course=self.config.course_name,
            students=students_data,
        )

        return result


# 辅助数据类（人脸识别结果）
@dataclass(frozen=True)
class RecognitionResult:
    """人脸识别结果"""
    students: List[StudentAttendance]
    annotated_image: Optional[Path] = None

    def has_uncertain(self) -> bool:
        """是否有不确定项"""
        return any(0.70 <= s.confidence < 0.85 for s in self.students)

    def uncertain_count(self) -> int:
        """不确定项数量"""
        return sum(1 for s in self.students if 0.70 <= s.confidence < 0.85)

    def uncertain_students(self) -> List[StudentAttendance]:
        """不确定的学生列表"""
        return [s for s in self.students if 0.70 <= s.confidence < 0.85]
