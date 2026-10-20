"""
考勤导出模块

将匹配结果导出为 JSON 格式（兼容 zfsoft-rollcall-cli）
"""

from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import json

import pandas as pd

from .models import MatchResult, AttendanceRecord


class AttendanceExporter:
    """考勤导出器"""

    def __init__(self, roster_df: pd.DataFrame) -> None:
        """
        初始化导出器

        Args:
            roster_df: 班级名单 DataFrame (列: xh, name)
        """
        self.roster_df = roster_df
        self.roster_xh_set = set(roster_df["xh"].astype(str))

    def export_attendance(
        self,
        match_results: List[MatchResult],
        output_path: str,
        date: str | None = None,
        course: str = "",
    ) -> Dict[str, Any]:
        """
        导出考勤数据

        Args:
            match_results: 匹配结果列表
            output_path: 输出JSON文件路径
            date: 日期（YYYY-MM-DD，None 为今天）
            course: 课程名称

        Returns:
            导出的考勤字典
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # 构建考勤记录
        attendance_records: List[AttendanceRecord] = []
        present_xh_set = set()

        # 处理检测到的学生
        for result in match_results:
            if result.xh:
                category = result.to_attendance_category()
                note = ""

                if not result.is_certain:
                    note = f"置信度低 ({result.confidence:.2f})，请人工确认"

                record = AttendanceRecord(
                    xh=result.xh,
                    category=category,
                    note=note,
                    confidence=result.confidence,
                )
                attendance_records.append(record)
                present_xh_set.add(result.xh)

        # 处理未检测到的学生（标记为旷课）
        absent_xh = self.roster_xh_set - present_xh_set
        for xh in sorted(absent_xh):
            record = AttendanceRecord(
                xh=xh,
                category="旷课",
                note="未检测到人脸",
            )
            attendance_records.append(record)

        # 生成输出格式
        students_data = [record.to_dict() for record in attendance_records]

        # 统计信息
        total = len(self.roster_xh_set)
        present = len(present_xh_set)
        absent = total - present
        uncertain = sum(1 for r in match_results if not r.is_certain and r.xh)
        unknown = sum(1 for r in match_results if r.xh is None)

        # 疑问列表
        uncertain_list = []
        for result in match_results:
            if not result.is_certain:
                uncertain_list.append({
                    "face_id": result.face_id,
                    "xh": result.xh,
                    "name": result.name,
                    "confidence": result.confidence,
                    "bbox": list(result.bbox),
                    "note": "置信度低，请人工确认" if result.xh else "未知人脸",
                })

        output_data = {
            "date": date,
            "course": course,
            "students": students_data,
            "uncertain": uncertain_list,
            "summary": {
                "total": total,
                "present": present,
                "absent": absent,
                "uncertain": uncertain,
                "unknown": unknown,
            },
        }

        # 保存到文件
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(f"✓ 考勤数据已导出: {output_path}")
        print(f"  总人数: {total}, 到课: {present}, 缺勤: {absent}")
        print(f"  疑问: {uncertain}, 未知: {unknown}")

        return output_data
