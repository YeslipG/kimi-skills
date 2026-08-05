# -*- coding: utf-8 -*-
"""
将 .doc 旧格式文件转换为 .docx。
依赖：本机安装 Microsoft Word + pywin32。
"""
import os
import sys


def convert_doc_to_docx(src, dst):
    from win32com import client
    word = client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    try:
        doc = word.Documents.Open(os.path.abspath(src))
        doc.SaveAs2(os.path.abspath(dst), FileFormat=16)  # wdFormatXMLDocument
        doc.Close()
    finally:
        word.Quit()
    print(f"Converted: {src} -> {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_doc.py <input.doc> <output.docx>")
        sys.exit(1)
    convert_doc_to_docx(sys.argv[1], sys.argv[2])
