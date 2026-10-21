#!/Users/scfmac/.hermes/hermes-agent/venv/bin/python
"""
人脸数据库构建工具

支持单人照和合照建库
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from facecall.face.database import FaceDatabaseBuilder
from facecall.face.detector import FaceDetector


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="人脸数据库构建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:

  # 合照建库（交互式）
  python scripts/build_database.py \\
    --mode group \\
    --photo class_photo.jpg \\
    --roster students.xlsx \\
    --output face_database.pkl

  # 合照建库（CSV批量）
  python scripts/build_database.py \\
    --mode group \\
    --photo class_photo.jpg \\
    --roster students.xlsx \\
    --mapping mapping.csv \\
    --output face_database.pkl

  # 单人照批量建库（文件名模式）
  python scripts/build_database.py \\
    --mode single \\
    --photos-dir photos/ \\
    --roster students.xlsx \\
    --output face_database.pkl

  # 单人照批量建库（CSV映射模式）
  python scripts/build_database.py \\
    --mode single \\
    --photos-dir photos/ \\
    --roster students.xlsx \\
    --single-mapping single_mapping.csv \\
    --output face_database.pkl

  # 追加模式（增量添加）
  python scripts/build_database.py \\
    --mode single \\
    --photos-dir new_students/ \\
    --roster students.xlsx \\
    --database face_database.pkl \\
    --output face_database.pkl
        """,
    )

    parser.add_argument(
        "--mode",
        choices=["single", "group"],
        required=True,
        help="建库模式: single=单人照, group=合照",
    )

    parser.add_argument("--roster", required=True, help="班级名单文件 (.xlsx)")

    parser.add_argument("--output", required=True, help="输出数据库文件 (.pkl)")

    # 合照模式参数
    group_args = parser.add_argument_group("合照模式参数")
    group_args.add_argument("--photo", help="合照路径")
    group_args.add_argument("--mapping", help="CSV映射文件（face_id,xh,name）")

    # 单人照模式参数
    single_args = parser.add_argument_group("单人照模式参数")
    single_args.add_argument("--photos-dir", help="单人照片目录")
    single_args.add_argument(
        "--single-mapping",
        help="单人照 CSV 映射文件（photo_filename,xh,name）"
    )

    # 追加模式
    parser.add_argument(
        "--database", help="已有数据库路径（追加模式）"
    )

    return parser.parse_args()


def load_mapping_from_csv(csv_path: str) -> List[Tuple[int, str, str]]:
    """从CSV加载映射"""
    df = pd.read_csv(csv_path)

    # 验证列
    required_cols = ["face_id", "xh", "name"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"CSV缺少列: {col}")

    mapping = []
    for _, row in df.iterrows():
        mapping.append((int(row["face_id"]), str(row["xh"]), str(row["name"])))

    return mapping


def interactive_mapping(
    faces, roster_df: pd.DataFrame
) -> List[Tuple[int, str, str]]:
    """交互式人脸匹配"""
    print(f"\n检测到 {len(faces)} 张人脸")
    print("=" * 60)
    print("请按标注图中的序号输入对应的学号")
    print("输入 'skip' 跳过当前人脸")
    print("输入 'quit' 提前结束")
    print("=" * 60)

    roster_dict = roster_df.set_index("xh")["name"].to_dict()
    mapping = []

    for face in faces:
        while True:
            xh_input = input(f"\n[{face.face_id}] 学号: ").strip()

            if xh_input.lower() == "skip":
                print("   ⊗ 已跳过")
                break

            if xh_input.lower() == "quit":
                print(f"\n提前结束，已录入 {len(mapping)} 人")
                return mapping

            # 验证学号
            if xh_input in roster_dict:
                name = roster_dict[xh_input]
                print(f"   ✓ {name}")
                mapping.append((face.face_id, xh_input, name))
                break
            else:
                print(f"   ✗ 学号 '{xh_input}' 不在名单中，请重新输入")

    return mapping


def main() -> None:
    """主函数"""
    args = parse_args()

    # 加载班级名单
    print(f"\n正在加载班级名单: {args.roster}")
    roster_df = pd.read_excel(args.roster)

    # 验证名单格式
    required_cols = ["xh", "name"]
    for col in required_cols:
        if col not in roster_df.columns:
            print(f"✗ 错误: 名单缺少列 '{col}'")
            sys.exit(1)

    print(f"✓ 名单加载完成: {len(roster_df)} 人")

    # 初始化构建器
    detector = FaceDetector()
    builder = FaceDatabaseBuilder(detector=detector, database_path=args.database)

    # 根据模式执行
    if args.mode == "group":
        # 合照模式
        if not args.photo:
            print("✗ 错误: 合照模式需要 --photo 参数")
            sys.exit(1)

        # 检测人脸
        faces = builder.build_from_group_photo(
            args.photo, output_preview="annotated_preview.jpg"
        )

        if len(faces) == 0:
            print("✗ 错误: 未检测到人脸")
            sys.exit(1)

        # 匹配人脸
        if args.mapping:
            # CSV批量导入
            print(f"\n正在加载映射文件: {args.mapping}")
            mapping = load_mapping_from_csv(args.mapping)
            print(f"✓ 映射加载完成: {len(mapping)} 条")
        else:
            # 交互式输入
            print("\n请打开预览图 (annotated_preview.jpg) 查看人脸编号")
            input("按回车键继续...")

            # macOS 自动打开预览图
            import subprocess
            import platform

            if platform.system() == "Darwin":
                subprocess.run(["open", "annotated_preview.jpg"], check=False)

            mapping = interactive_mapping(faces, roster_df)

        # 添加记录
        builder.add_face_records(faces, mapping, args.photo)

    elif args.mode == "single":
        # 单人照模式
        if not args.photos_dir:
            print("✗ 错误: 单人照模式需要 --photos-dir 参数")
            sys.exit(1)

        builder.build_from_single_photos(
            args.photos_dir,
            roster_df,
            mapping_csv=args.single_mapping
        )

    # 保存数据库
    builder.save(args.output)

    # 统计信息
    stats = builder.get_statistics()
    print("\n数据库统计:")
    print(f"  总记录数: {stats['total']}")
    print(f"  平均质量: {stats['avg_quality']:.2f}")
    print(f"  最低质量: {stats['min_quality']:.2f}")
    print(f"  最高质量: {stats['max_quality']:.2f}")

    print(f"\n✅ 完成！数据库已保存: {args.output}")


if __name__ == "__main__":
    main()
