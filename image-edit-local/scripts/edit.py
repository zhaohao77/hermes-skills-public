#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Offline image editing helpers (Pillow only, no network).

Subcommands: info, crop, resize, rotate, adjust, text, redact, mark, collage,
convert, strip.

Safety: never overwrites the input file.
"""
from __future__ import annotations

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    r"C:\Windows\Fonts\simsun.ttc",
]


def _font(size: int):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _open(path: str) -> Image.Image:
    if not os.path.exists(path):
        sys.exit(f"input not found: {path}")
    return Image.open(path)


def _save(img: Image.Image, out: str, src: str) -> None:
    if os.path.abspath(out) == os.path.abspath(src):
        sys.exit("refusing to overwrite the input file; choose a different --out")
    d = os.path.dirname(os.path.abspath(out))
    if d:
        os.makedirs(d, exist_ok=True)
    if out.lower().endswith((".jpg", ".jpeg")) and img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(out)
    print(f"saved: {os.path.abspath(out)}  size={img.size} mode={img.mode}")


def _box(s: str) -> tuple:
    parts = [int(p) for p in s.replace(" ", "").split(",")]
    if len(parts) != 4:
        sys.exit("--box expects L,T,R,B")
    return tuple(parts)


def cmd_info(a) -> None:
    img = _open(a.input)
    print(f"path   : {os.path.abspath(a.input)}")
    print(f"size   : {img.size[0]} x {img.size[1]}")
    print(f"mode   : {img.mode}")
    print(f"format : {img.format}")
    exif = img.getexif()
    print(f"exif   : {len(exif)} tags" + (" (contains GPS)" if 34853 in exif else ""))


def cmd_crop(a) -> None:
    img = _open(a.input)
    box = _box(a.box)
    if box[2] <= box[0] or box[3] <= box[1]:
        sys.exit("invalid box: right/bottom must be greater than left/top")
    _save(img.crop(box), a.out, a.input)


def cmd_resize(a) -> None:
    img = _open(a.input)
    w, h = img.size
    if a.height:
        nw, nh = a.width, a.height
    else:
        nw = a.width
        nh = max(1, round(h * nw / w))
    _save(img.resize((nw, nh), Image.LANCZOS), a.out, a.input)


def cmd_rotate(a) -> None:
    img = _open(a.input)
    _save(img.rotate(-a.degrees, expand=True), a.out, a.input)


def cmd_adjust(a) -> None:
    img = _open(a.input)
    if a.brightness:
        img = ImageEnhance.Brightness(img).enhance(a.brightness)
    if a.contrast:
        img = ImageEnhance.Contrast(img).enhance(a.contrast)
    if a.sharpness:
        img = ImageEnhance.Sharpness(img).enhance(a.sharpness)
    _save(img, a.out, a.input)


def cmd_text(a) -> None:
    img = _open(a.input).convert("RGBA")
    draw = ImageDraw.Draw(img)
    font = _font(a.size)
    x, y = [int(p) for p in a.at.split(",")]
    draw.text((x, y), a.text, font=font, fill=a.color)
    _save(img, a.out, a.input)


def cmd_redact(a) -> None:
    img = _open(a.input).convert("RGBA")
    box = _box(a.box)
    if a.mode == "blur":
        region = img.crop(box).filter(ImageFilter.GaussianBlur(radius=a.radius))
        img.paste(region, box)
    else:
        ImageDraw.Draw(img).rectangle(box, fill=a.color)
    _save(img, a.out, a.input)


def cmd_mark(a) -> None:
    img = _open(a.input).convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    font = _font(a.size)
    text_w = draw.textlength(a.text, font=font)
    step_x = int(text_w + a.gap)
    step_y = a.size * 4
    alpha = int(255 * a.opacity / 100)
    for y in range(-step_y, img.size[1] + step_y, step_y):
        for x in range(-step_x, img.size[0] + step_x, step_x):
            draw.text((x, y), a.text, font=font, fill=(255, 255, 255, alpha))
    out = Image.alpha_composite(img, layer.rotate(a.angle, expand=False))
    _save(out, a.out, a.input)


def cmd_collage(a) -> None:
    imgs = [_open(p).convert("RGB") for p in a.inputs]
    cols = max(1, a.cols)
    rows = (len(imgs) + cols - 1) // cols
    cw = a.cell_width
    scaled = []
    for im in imgs:
        ratio = cw / im.size[0]
        scaled.append(im.resize((cw, max(1, round(im.size[1] * ratio))), Image.LANCZOS))
    ch = max(i.size[1] for i in scaled)
    canvas = Image.new("RGB", (cols * cw + (cols - 1) * a.gap, rows * ch + (rows - 1) * a.gap), a.background)
    for idx, im in enumerate(scaled):
        r, c = divmod(idx, cols)
        canvas.paste(im, (c * (cw + a.gap), r * (ch + a.gap)))
    _save(canvas, a.out, a.inputs[0])


def cmd_convert(a) -> None:
    img = _open(a.input)
    fmt = a.format.lower().lstrip(".")
    if not a.out:
        a.out = os.path.splitext(a.input)[0] + "_out." + fmt
    _save(img, a.out, a.input)


def cmd_strip(a) -> None:
    img = _open(a.input)
    data = list(img.getdata())
    clean = Image.new(img.mode, img.size)
    clean.putdata(data)
    _save(clean, a.out, a.input)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Offline image editing (Pillow)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("info"); s.add_argument("input"); s.set_defaults(func=cmd_info)

    s = sub.add_parser("crop")
    s.add_argument("input"); s.add_argument("--box", required=True); s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_crop)

    s = sub.add_parser("resize")
    s.add_argument("input"); s.add_argument("--width", type=int, required=True)
    s.add_argument("--height", type=int); s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_resize)

    s = sub.add_parser("rotate")
    s.add_argument("input"); s.add_argument("--degrees", type=float, required=True)
    s.add_argument("--out", required=True); s.set_defaults(func=cmd_rotate)

    s = sub.add_parser("adjust")
    s.add_argument("input"); s.add_argument("--brightness", type=float, default=1.0)
    s.add_argument("--contrast", type=float, default=1.0)
    s.add_argument("--sharpness", type=float, default=1.0)
    s.add_argument("--out", required=True); s.set_defaults(func=cmd_adjust)

    s = sub.add_parser("text")
    s.add_argument("input"); s.add_argument("--text", required=True)
    s.add_argument("--at", default="20,20"); s.add_argument("--size", type=int, default=36)
    s.add_argument("--color", default="red"); s.add_argument("--out", required=True)
    s.set_defaults(func=cmd_text)

    s = sub.add_parser("redact")
    s.add_argument("input"); s.add_argument("--box", required=True)
    s.add_argument("--mode", choices=["blur", "fill"], default="blur")
    s.add_argument("--radius", type=int, default=18)
    s.add_argument("--color", default="#000000")
    s.add_argument("--out", required=True); s.set_defaults(func=cmd_redact)

    s = sub.add_parser("mark")
    s.add_argument("input"); s.add_argument("--text", required=True)
    s.add_argument("--opacity", type=int, default=50); s.add_argument("--size", type=int, default=42)
    s.add_argument("--angle", type=float, default=30); s.add_argument("--gap", type=int, default=40)
    s.add_argument("--out", required=True); s.set_defaults(func=cmd_mark)

    s = sub.add_parser("collage")
    s.add_argument("inputs", nargs="+"); s.add_argument("--cols", type=int, default=2)
    s.add_argument("--cell-width", dest="cell_width", type=int, default=800)
    s.add_argument("--gap", type=int, default=12); s.add_argument("--background", default="#ffffff")
    s.add_argument("--out", required=True); s.set_defaults(func=cmd_collage)

    s = sub.add_parser("convert")
    s.add_argument("input"); s.add_argument("--format", default="png")
    s.add_argument("--out"); s.set_defaults(func=cmd_convert)

    s = sub.add_parser("strip")
    s.add_argument("input"); s.add_argument("--out", required=True); s.set_defaults(func=cmd_strip)
    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
