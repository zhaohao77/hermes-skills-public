#!/usr/bin/env python3
"""
长图自动切割工具
- 自动将长图按高度分段（默认1200px一段，overlap 80px）
- 分段保存到同一目录，方便AI逐段读取
- 可选：输出切割信息供后续拼接

用法：
  python long_image_slicer.py <图片路径> [--max-height 1200] [--overlap 80] [--out-dir ./slices]
"""

import argparse
import os
import sys
from pathlib import Path
from PIL import Image


def slice_long_image(
    image_path: str,
    max_height: int = 1200,
    overlap: int = 80,
    out_dir: str = None,
    verbose: bool = True,
):
    """
    将长图按高度分段

    Args:
        image_path: 图片路径
        max_height: 每段最大高度（像素）
        overlap: 相邻段重叠像素
        out_dir: 输出目录（默认同目录下的 slices/）
        verbose: 是否打印切割信息
    """
    img = Image.open(image_path)
    width, height = img.size

    # 自动判断是否需要切
    if height <= max_height:
        if verbose:
            print(f"✅ 图片高度 {height}px ≤ {max_height}px，无需切割")
            print(f"原图路径: {image_path}")
        return [image_path]

    # 输出目录
    stem = Path(image_path).stem
    if out_dir is None:
        out_dir = Path(image_path).parent / f"{stem}_slices"
    else:
        out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 计算分段
    slices = []
    y = 0
    slice_idx = 0
    while y < height:
        y_end = min(y + max_height, height)
        # 最后一段如果剩余太少（< max_height/3）就合并到上一段
        if y > 0 and (height - y) < max_height // 3:
            # 重新切上一段，延伸到结尾
            prev_slice_path = slices[-1]
            prev_img = Image.open(prev_slice_path)
            prev_y_start = slice_idx - 1  # 这不是准确值，下面重新算
            break

        # 切割
        box = (0, y, width, y_end)
        slice_img = img.crop(box)

        # 保存
        slice_path = out_dir / f"{stem}_slice_{slice_idx:03d}.png"
        slice_img.save(slice_path)
        slices.append(str(slice_path))

        if verbose:
            print(f"  [{slice_idx:03d}] y={y}~{y_end} ({y_end-y}px) → {slice_path.name}")

        y = y_end - overlap  # 重叠
        slice_idx += 1

    # 处理最后一段太短的情况（合并到上一段）
    # 重新扫描一遍，保证最后一段不短
    if height > max_height:
        # 重新精确切割
        slices.clear()
        y = 0
        slice_idx = 0
        while y < height:
            y_end = min(y + max_height, height)
            remaining = height - y_end

            # 如果剩余部分小于 max_height/3，合并到当前段
            if remaining > 0 and remaining < max_height // 3:
                y_end = height  # 直接切到底

            box = (0, y, width, y_end)
            slice_img = img.crop(box)
            slice_path = out_dir / f"{stem}_slice_{slice_idx:03d}.png"
            slice_img.save(slice_path)
            slices.append(str(slice_path))

            if verbose:
                print(f"  [{slice_idx:03d}] y={y}~{y_end} ({y_end-y}px) → {slice_path.name}")

            if y_end == height:
                break

            y = y_end - overlap
            slice_idx += 1

    if verbose:
        print(f"\n✅ 完成！共 {len(slices)} 段")
        print(f"输出目录: {out_dir}")
        print(f"\n📌 读取顺序：")
        for i, s in enumerate(slices):
            print(f"   第{i+1}段: {s}")

    return slices


def main():
    parser = argparse.ArgumentParser(
        description="长图自动切割工具 — 解决AI无法一次读取超长图片的问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("image", help="图片路径")
    parser.add_argument("--max-height", type=int, default=1200,
                        help="每段最大高度（默认1200px）")
    parser.add_argument("--overlap", type=int, default=80,
                        help="相邻段重叠像素（默认80px，避免内容被切断）")
    parser.add_argument("--out-dir", help="输出目录（默认图片同目录下 slices/ 文件夹）")
    parser.add_argument("--info-only", action="store_true",
                        help="只显示图片信息，不切割")

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"❌ 文件不存在: {args.image}")
        sys.exit(1)

    # 先显示图片基本信息
    img = Image.open(args.image)
    width, height = img.size
    print(f"📐 图片尺寸: {width}×{height}px")
    print(f"📦 格式: {img.format} | 模式: {img.mode}")
    print(f"📁 路径: {os.path.abspath(args.image)}")

    if args.info_only:
        estimated_slices = (height + args.max_height - args.overlap - 1) // (args.max_height - args.overlap)
        print(f"\n🔪 若按 max_height={args.max_height}px, overlap={args.overlap}px 切割：")
        print(f"   预计约 {max(1, estimated_slices)} 段")
        return

    slice_long_image(
        image_path=args.image,
        max_height=args.max_height,
        overlap=args.overlap,
        out_dir=args.out_dir,
    )


if __name__ == "__main__":
    main()
