#!/Users/scfmac/.hermes/hermes-agent/venv/bin/python
"""
人脸考勤识别工具

从课堂合照识别学生考勤
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from facecall.face.database import FaceDatabaseBuilder
from facecall.face.detector import FaceDetector
from facecall.face.matcher import FaceMatcher
from facecall.face.annotator import ImageAnnotator
from facecall.face.exporter import AttendanceExporter


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="人脸考勤识别工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 基本用法
  python scripts/check_attendance.py \\
    --photo class_photo.jpg \\
    --database face_database.pkl \\
    --roster students.xlsx \\
    --output attendance.json

  # 指定日期和课程
  python scripts/check_attendance.py \\
    --photo class_photo.jpg \\
    --database face_database.pkl \\
    --roster students.xlsx \\
    --date 2026-10-20 \\
    --course "体育3" \\
    --output attendance.json \\
    --annotated result_annotated.jpg

  # 调整匹配阈值
  python scripts/check_attendance.py \\
    --photo class_photo.jpg \\
    --database face_database.pkl \\
    --roster students.xlsx \\
    --threshold 0.60 \\
    --output attendance.json
        """,
    )

    parser.add_argument("--photo", required=True, help="课堂合照路径")

    parser.add_argument("--database", required=True, help="人脸数据库文件 (.pkl)")

    parser.add_argument("--roster", required=True, help="班级名单文件 (.xlsx)")

    parser.add_argument("--output", required=True, help="输出考勤JSON文件")

    parser.add_argument(
        "--annotated", help="输出标注图片路径（可选）"
    )

    parser.add_argument(
        "--date",
        help="日期 (YYYY-MM-DD，默认今天)",
    )

    parser.add_argument("--course", default="", help="课程名称")

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.70,
        help="匹配阈值 (0.0-1.0，默认0.70)",
    )

    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.9,
        help="最小检测置信度 (默认0.9)",
    )

    return parser.parse_args()


def main() -> None:
    """主函数"""
    args = parse_args()

    # 验证输入文件
    if not Path(args.photo).exists():
        print(f"✗ 错误: 照片不存在: {args.photo}")
        sys.exit(1)

    if not Path(args.database).exists():
        print(f"✗ 错误: 数据库不存在: {args.database}")
        sys.exit(1)

    if not Path(args.roster).exists():
        print(f"✗ 错误: 名单不存在: {args.roster}")
        sys.exit(1)

    # 加载数据库
    print(f"\n正在加载人脸数据库: {args.database}")
    database = FaceDatabaseBuilder.load(args.database)
    print(f"✓ 数据库加载完成: {len(database)} 条记录")

    # 加载班级名单
    print(f"\n正在加载班级名单: {args.roster}")
    roster_df = pd.read_excel(args.roster)
    print(f"✓ 名单加载完成: {len(roster_df)} 人")

    # 检测人脸
    print(f"\n正在检测人脸: {args.photo}")
    detector = FaceDetector()
    faces = detector.detect_faces(args.photo, min_confidence=args.min_confidence)
    print(f"✓ 检测到 {len(faces)} 张人脸")

    if len(faces) == 0:
        print("⚠️  警告: 未检测到人脸")

    # 匹配人脸
    print(f"\n正在匹配人脸（阈值={args.threshold}）...")
    matcher = FaceMatcher(database, distance_metric="cosine", threshold=args.threshold)
    match_results = matcher.match_faces(faces)

    # 统计信息
    stats = matcher.get_match_statistics(match_results)
    print(f"✓ 匹配完成:")
    print(f"  总人脸数: {stats['total_faces']}")
    print(f"  确定匹配: {stats['matched']}")
    print(f"  不确定: {stats['uncertain']}")
    print(f"  未知人脸: {stats['unknown']}")

    # 导出考勤数据
    print(f"\n正在导出考勤数据...")
    exporter = AttendanceExporter(roster_df)
    date_str = args.date if args.date else datetime.now().strftime("%Y-%m-%d")
    attendance_data = exporter.export_attendance(
        match_results, args.output, date=date_str, course=args.course
    )

    # 生成标注图片
    if args.annotated:
        print(f"\n正在生成标注图片: {args.annotated}")
        annotator = ImageAnnotator()
        annotator.annotate_matches(args.photo, match_results, args.annotated)
        print(f"✓ 标注图片已保存")

    # 输出疑问列表
    if attendance_data["uncertain"]:
        print("\n⚠️  疑问人脸（需人工确认）:")
        for item in attendance_data["uncertain"]:
            if item["xh"]:
                print(f"  [{item['face_id']}] {item['name']} ({item['xh']}) - 置信度: {item['confidence']:.2f}")
            else:
                print(f"  [{item['face_id']}] 未知人脸 - bbox={item['bbox']}")

    print(f"\n✅ 完成！考勤数据已保存: {args.output}")
    print(f"\n可直接传给 zfsoft-rollcall-cli:")
    print(f"  python /path/to/zfsoft-rollcall-cli/scripts/rollcall_auto.py \\")
    print(f"    --date {date_str} \\")
    print(f"    --course \"{args.course}\" \\")
    print(f"    --input {args.output}")


if __name__ == "__main__":
    main()
