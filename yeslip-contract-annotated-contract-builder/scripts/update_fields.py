# -*- coding: utf-8 -*-
"""
用本机 Word（COM 自动化）刷新合同文档：
  1) 重新分页；2) 更新全部目录(TOC)域写入页码；3) 保存 docx；4) 可选导出 PDF 预览。

为什么需要这一步：python-docx 插入的 TOC 域只有占位文字，
必须由 Word 实际计算页码后目录才可用；页码域同理。

用法：
  python update_fields.py 合同.docx [--pdf 预览.pdf]

依赖：pywin32（本机 D:/Kimi/.venv-xlsx 的 python 已具备），且机器装有 Microsoft Word。
"""
import argparse
import os
import sys


def update_fields(docx_path, pdf_path=None):
    import win32com.client
    src = os.path.abspath(docx_path)
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(src)
        doc.Repaginate()
        for i in range(1, doc.TablesOfContents.Count + 1):
            doc.TablesOfContents.Item(i).Update()
        doc.Save()
        pages = doc.ComputeStatistics(2)
        sections = doc.Sections.Count
        if pdf_path:
            doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)  # 17 = wdFormatPDF
        doc.Close(False)
        return {"pages": pages, "sections": sections,
                "toc_count": doc.TablesOfContents.Count if not doc else None}
    finally:
        word.Quit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", help="待刷新的合同 docx 路径")
    ap.add_argument("--pdf", help="可选：同时导出 PDF 预览路径")
    args = ap.parse_args()
    info = update_fields(args.docx, args.pdf)
    print(f"OK pages={info['pages']} sections={info['sections']}")
    if args.pdf:
        print("pdf:", os.path.abspath(args.pdf))


if __name__ == "__main__":
    sys.exit(main())
