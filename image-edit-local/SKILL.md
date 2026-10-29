---
name: image-edit-local
description: 本地改图（离线、零 API、零成本）。裁剪/缩放/旋转/拼图/加水印/加文字标注/局部遮盖打码/调亮度对比度/格式转换/去 EXIF。当用户说"改一下这张图""裁一下""加水印""把这块挡住""调亮点""转 PNG""拼图"时使用。不用于伪造凭证（票据/发票/合同/签名/日期），遇到直接拒绝并给正规路径。
---

# 本地改图（离线）

用本机 Python + Pillow 完成常规图片处理。**不联网、不花钱、不上传**。
需要"按语义重画/改文字"（如把照片里的招牌换成别的字），本地做不到，走生成式模型；本技能只管**几何类与像素类**操作。

## 红线（先看这条）

以下请求**一律不做**，并说明原因 + 给正规路径（重开票/流水/情况说明）：

- 改票据、发票、合同、收据、工资条上的**日期、金额、抬头、印章、签名**
- 把一张图里的凭证信息"平移"到另一个时间/主体
- 制作可用于报销、对账、审计、诉讼的"看起来像原件"的图

裁边、调亮、去反光、加水印、打码、拼图、改尺寸 —— 这些随便做。

## 环境

- Python：`python`（本机 3.11，Pillow 12.x 已装）
- 脚本：`scripts/edit.py`（同目录下的相对路径）
- 中文字体：自动找 `C:\Windows\Fonts\msyh.ttc` / `simhei.ttf`

## 命令

```powershell
python <skill>/scripts/edit.py info   <in> 
python <skill>/scripts/edit.py crop   <in> --box L,T,R,B --out <out>
python <skill>/scripts/edit.py resize <in> --width 1080 --out <out>            # 等比
python <skill>/scripts/edit.py rotate <in> --degrees 90 --out <out>
python <skill>/scripts/edit.py adjust <in> --brightness 1.15 --contrast 1.1 --out <out>
python <skill>/scripts/edit.py text   <in> --text "备注" --at 20,40 --size 36 --color "#ff0000" --out <out>
python <skill>/scripts/edit.py redact <in> --box 100,200,400,260 --mode blur --out <out>
python <skill>/scripts/edit.py mark   <in> --text "内部资料" --opacity 60 --out <out>
python <skill>/scripts/edit.py collage <in1> <in2> [<in3>...] --cols 2 --out <out>
python <skill>/scripts/edit.py convert <in> --format png --out <out>
python <skill>/scripts/edit.py strip  <in> --out <out>                        # 去 EXIF/GPS
```

`--box` 是左,上,右,下（像素）。`redact --mode` 取 `blur`（模糊）或 `fill`（纯色块，颜色用 `--color`）。

## 流程

1. 先 `info` 看尺寸/模式，确认坐标不会越界
2. 原图**另存**，永远不覆盖输入（脚本默认拒绝 out == in）
3. 改完 `info` 复核输出尺寸；涉及文字的，用 `vision_analyze` 看一眼成品
4. 交付时给绝对路径，并在回复里写明做了什么操作

## 已知限制

- 不能"擦除后智能补全"（去水印后背景是模糊块，不是重建）
- 不能改照片里已有的印刷/手写文字
- 中文字体缺失时会退回默认字体，字形可能难看——先 `info` 报错不如先试小图
