# -*- coding: utf-8 -*-
"""
把 PDF 预览渲染成 PNG 图片，供逐页目检（颜色、错位、页码、签署栏）。

用法：
  python render_preview.py 预览.pdf 输出目录 [--pages 1,2,4,last] [--scale 1.4]
  不指定 --pages 时默认渲染 第1页、第2页、第4页、最后一页（覆盖封面/目录/正文首页/末页）。

依赖：pypdfium2（本机 D:/Kimi/.venv-pdf 的 python 已具备）。
"""
import argparse
import os

import pypdfium2 as pdfium


def parse_pages(spec, total):
    if not spec:
        picks = {0, 1, 3, total - 1}
        return sorted(i for i in picks if 0 <= i < total)
    out = []
    for part in spec.split(","):
        part = part.strip().lower()
        if part == "last":
            out.append(total - 1)
        elif part == "all":
            out.extend(range(total))
        else:
            out.append(int(part) - 1)
    return sorted(set(i for i in out if 0 <= i < total))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("out_dir")
    ap.add_argument("--pages", default=None, help="如 1,2,4,last 或 all")
    ap.add_argument("--scale", type=float, default=1.4)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    pdf = pdfium.PdfDocument(args.pdf)
    pages = parse_pages(args.pages, len(pdf))
    for i in pages:
        img = pdf[i].render(scale=args.scale).to_pil()
        img.save(os.path.join(args.out_dir, f"page_{i + 1:02d}.png"))
    print("rendered:", [i + 1 for i in pages], "of", len(pdf))


if __name__ == "__main__":
    main()
