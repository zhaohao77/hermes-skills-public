#!/usr/bin/env python3
"""
长图并行OCR工具 — 快读方案
- 自动切图 + 用Qwen3-VL并行OCR
- 依赖ms-qwen-vl skill的API配置
"""

import os
import sys
import json
from pathlib import Path
from PIL import Image
import concurrent.futures
import subprocess
import time
import random

SKILL_DIR = Path.home() / ".claude" / "skills" / "ms-qwen-vl"
SCRIPT = SKILL_DIR / "scripts" / "ms_qwen_vl.py"
MAX_HEIGHT = 1900  # Qwen3-VL限制2048，留余量
OVERLAP = 80

def slice_image(img_path, out_dir):
    """切割长图"""
    img = Image.open(img_path)
    width, height = img.size

    if height <= MAX_HEIGHT:
        return [img_path]

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    slices = []
    y = 0
    idx = 0
    while y < height:
        y_end = min(y + MAX_HEIGHT, height)
        remaining = height - y_end
        if remaining > 0 and remaining < MAX_HEIGHT // 3:
            y_end = height

        box = (0, y, width, y_end)
        slice_path = out_dir / f"slice_{idx:03d}.png"
        img.crop(box).save(slice_path)
        slices.append(str(slice_path))

        if y_end == height:
            break
        y = y_end - OVERLAP
        idx += 1

    return slices

def ocr_one(slice_path):
    """调Qwen3-VL OCR一段"""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), slice_path, "--task", "ocr"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return f"[OCR ERROR: {result.stderr[:200]}]"

def main():
    if len(sys.argv) < 2:
        print("用法: python long_image_fast_ocr.py <图片路径> [--out结果保存路径]")
        sys.exit(1)

    img_path = sys.argv[1]
    out_path = None
    if "--out" in sys.argv:
        idx = sys.argv.index("--out")
        out_path = sys.argv[idx + 1]

    # Step 1: 切割
    print(f"📐 原图尺寸: {Image.open(img_path).size}")
    print("🔪 切割中...", end=" ", flush=True)
    slices = slice_image(img_path, Path(img_path).parent / f"{Path(img_path).stem}_slices_fast")
    print(f"共 {len(slices)} 段")

    if len(slices) == 1:
        text = ocr_one(slices[0])
    else:
        # Step 2: 限流并行OCR（最多8路，每路之间错开500ms避免429）
        max_workers = min(len(slices), 8)
        print(f"🚀 并行OCR ({len(slices)}段, {max_workers}路并发, 错峰500ms)...")
        start = time.time()

        results = [None] * len(slices)
        def ocr_with_index(idx_path):
            idx, path = idx_path
            # 错峰：根据索引间隔500ms打开发送
            delay = idx * 0.5 * (len(slices) / max_workers)
            if delay > 0:
                time.sleep(delay)
            # 随机再加0~200ms抖动，避免精准同时命中限流
            time.sleep(random.random() * 0.2)
            return idx, ocr_one(path)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            for idx, text in ex.map(ocr_with_index, enumerate(slices)):
                results[idx] = text

        elapsed = time.time() - start
        print(f"⏱ 耗时: {elapsed:.1f}秒")

        # Step 3: 拼接
        text_parts = []
        for i, (s, r) in enumerate(zip(slices, results)):
            text_parts.append(f"--- [第{i+1}段] ---")
            text_parts.append(r)
        text = "\n".join(text_parts)

    # Step 4: 输出
    print(f"\n📝 总字数: {len(text)}")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"💾 已保存 → {out_path}")
    else:
        print("\n" + "="*50)
        print(text)

    # 清理切片
    for s in slices:
        try:
            os.remove(s)
        except:
            pass

if __name__ == "__main__":
    main()
