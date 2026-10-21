#!/Users/scfmac/.hermes/hermes-agent/venv/bin/python
"""
一键集成脚本：人脸识别 → 正方系统提交

完整流程:
1. 人脸识别生成考勤JSON
2. 调用 zfsoft-rollcall-cli 提交到正方系统
"""

import argparse
import sys
import subprocess
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
        description="人脸识别 + 正方系统提交一键集成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 基本用法
  python scripts/integrate_zfsoft.py \\
    --photo class_photo.jpg \\
    --database face_database.pkl \\
    --roster students.xlsx \\
    --course "体育3" \\
    --zfsoft-cli /path/to/zfsoft-rollcall-cli

  # 指定日期
  python scripts/integrate_zfsoft.py \\
    --photo class_photo.jpg \\
    --database face_database.pkl \\
    --roster students.xlsx \\
    --date 2026-10-20 \\
    --course "体育3" \\
    --zfsoft-cli /path/to/zfsoft-rollcall-cli
        """,
    )

    parser.add_argument("--photo", required=True, help="课堂合照路径")
    parser.add_argument("--database", required=True, help="人脸数据库 (.pkl)")
    parser.add_argument("--roster", required=True, help="班级名单 (.xlsx)")
    parser.add_argument("--course", required=True, help="课程名称")
    parser.add_argument(
        "--zfsoft-cli", required=True, help="zfsoft-rollcall-cli 项目路径"
    )

    parser.add_argument("--date", help="日期 (YYYY-MM-DD，默认今天)")
    parser.add_argument("--threshold", type=float, default=0.70, help="匹配阈值")
    parser.add_argument(
        "--temp-dir", default="./temp", help="临时文件目录"
    )
    parser.add_argument(
        "--keep-temp", action="store_true", help="保留临时文件"
    )

    return parser.parse_args()


def main() -> None:
    """主函数"""
    args = parse_args()

    # 创建临时目录
    temp_dir = Path(args.temp_dir)
    temp_dir.mkdir(exist_ok=True)

    date_str = args.date if args.date else datetime.now().strftime("%Y-%m-%d")
    attendance_json = temp_dir / f"attendance_{date_str}.json"
    annotated_img = temp_dir / f"annotated_{date_str}.jpg"

    print("=" * 70)
    print("🎯 人脸识别 + 正方系统提交 - 一键集成")
    print("=" * 70)

    # ========== 阶段1: 人脸识别 ==========
    print("\n【阶段1】人脸识别")
    print("-" * 70)

    # 加载数据库
    print(f"正在加载人脸数据库: {args.database}")
    database = FaceDatabaseBuilder.load(args.database)
    print(f"✓ 数据库: {len(database)} 条记录")

    # 加载名单
    print(f"正在加载班级名单: {args.roster}")
    roster_df = pd.read_excel(args.roster)
    print(f"✓ 名单: {len(roster_df)} 人")

    # 检测人脸
    print(f"正在检测人脸: {args.photo}")
    detector = FaceDetector()
    faces = detector.detect_faces(args.photo, min_confidence=0.9)
    print(f"✓ 检测到 {len(faces)} 张人脸")

    # 匹配人脸
    print(f"正在匹配人脸（阈值={args.threshold}）...")
    matcher = FaceMatcher(database, threshold=args.threshold)
    match_results = matcher.match_faces(faces)
    stats = matcher.get_match_statistics(match_results)
    print(f"✓ 匹配结果: 确定={stats['matched']}, 不确定={stats['uncertain']}, 未知={stats['unknown']}")

    # 导出考勤数据
    print(f"正在导出考勤数据: {attendance_json}")
    exporter = AttendanceExporter(roster_df)
    attendance_data = exporter.export_attendance(
        match_results, str(attendance_json), date=date_str, course=args.course
    )

    # 生成标注图片
    print(f"正在生成标注图片: {annotated_img}")
    annotator = ImageAnnotator()
    annotator.annotate_matches(args.photo, match_results, str(annotated_img))

    # 输出疑问提示
    if attendance_data["uncertain"]:
        print("\n⚠️  检测到疑问人脸，建议人工确认后再提交:")
        for item in attendance_data["uncertain"]:
            if item["xh"]:
                print(f"  • {item['name']} ({item['xh']}) - 置信度: {item['confidence']:.2f}")
            else:
                print(f"  • 未知人脸 [face_id={item['face_id']}]")

        confirm = input("\n是否继续提交到正方系统? (y/n): ").strip().lower()
        if confirm != "y":
            print("已取消提交")
            sys.exit(0)

    # ========== 阶段2: 提交到正方系统 ==========
    print("\n【阶段2】提交到正方系统")
    print("-" * 70)

    zfsoft_script = Path(args.zfsoft_cli) / "scripts" / "rollcall_auto.py"
    if not zfsoft_script.exists():
        print(f"✗ 错误: 找不到 zfsoft-rollcall-cli 脚本: {zfsoft_script}")
        sys.exit(1)

    cmd = [
        "python",
        str(zfsoft_script),
        "--date",
        date_str,
        "--course",
        args.course,
        "--input",
        str(attendance_json),
    ]

    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)

    if result.returncode == 0:
        print("\n✅ 提交成功！")
    else:
        print(f"\n✗ 提交失败 (exit code: {result.returncode})")
        sys.exit(1)

    # 清理临时文件
    if not args.keep_temp:
        print(f"\n正在清理临时文件...")
        attendance_json.unlink(missing_ok=True)
        print(f"✓ 已删除: {attendance_json}")
    else:
        print(f"\n临时文件保留:")
        print(f"  考勤数据: {attendance_json}")
        print(f"  标注图片: {annotated_img}")

    print("\n" + "=" * 70)
    print("🎉 完成！考勤数据已成功提交到正方教务系统")
    print("=" * 70)


if __name__ == "__main__":
    main()
