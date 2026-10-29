---
name: long-image-slicer
description: 长图自动切割+并行OCR工具。解决AI不能一次读取超长图片（>1200px或受限2048×2048）的问题。支持两种模式：(1)纯切割模式：自动按高度分段，带重叠避免内容切断；(2)快速OCR模式：切割+并行调Qwen3-VL OCR一次性读完。依赖ms-qwen-vl skill。
---

# 长图自动切割 + 并行OCR工具

## 什么时候用
- 遇到超长截图（公众号长文截图、微博长图、聊天记录长图、叶荣添/仙子/乐晴观点长图等），图片高度远超模型限制
- 魔搭Qwen3-VL限制2048×2048，长图需要先切割再逐段读取

## 使用方式

### 模式一：纯切割（依赖Pillow，零API Key）
```bash
python scripts/long_image_slicer.py /path/to/long_image.png
```
- 自动按1900px一段切割，带80px重叠
- 输出到原图同目录 `{图片名}_slices/` 文件夹
- 可选参数：`--max-height 1500` `--overlap 100` `--out-dir D:\slices`

### 模式二：快速并行OCR（依赖ms-qwen-vl skill）
```bash
python scripts/long_image_fast_ocr.py /path/to/long_image.jpg [--out result.txt]
```
- 自动切割 + 并行调Qwen3-VL-30B模型OCR（限流8路+错峰防429）
- 默认输出到终端，`--out` 可保存到文件
- 完成后自动清理临时切片文件

## 依赖
- **模式一**：Pillow（已安装）
- **模式二**：Pillow + ms-qwen-vl skill（需配置魔搭MODELSCOPE_API_KEY）

## 技术要点
- 错峰并行：每路间隔500ms + 随机0~200ms抖动，避免429限流
- 尾部合并：最后一段如果 < max_height/3 自动合并到上一段，避免碎片
- 自动清理：OCR完成后自动删除临时切片，不留垃圾
