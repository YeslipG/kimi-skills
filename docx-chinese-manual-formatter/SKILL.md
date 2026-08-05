---
name: docx-chinese-manual-formatter
description: |
  Use this skill whenever the user wants to format, reformat, typeset, or standardize an existing Word document (.docx) according to Chinese technical manual / instruction manual layout standards.

  Trigger on requests like: "format this docx", "reformat this manual", "apply heading styles", "standardize document layout", "排版这份文档", "重排说明书", "规范文档格式", "按这个格式排版", "给这个文档排版", or when the user provides a .docx file and asks for formatting, 排版, 样式调整, 标题层级, 字体设置, or 表格格式.

  This skill applies heading level numbering, Chinese/Western fonts, paragraph spacing, and table formatting for Chinese technical documentation.
---

# Word 中文技术手册排版 Skill

## When to use

Use this skill when the user provides an existing `.docx` file (or a path to one) and asks you to format or reformat it according to Chinese technical manual conventions. The skill covers:

- Heading level numbering and styles
- Chinese and Western fonts
- Paragraph spacing before/after headings
- List item numbering for procedures/checklists
- Table formatting (alignment, first-row style, cell margins)

## Formatting Rules

### Heading Numbering

| Level | Style | Example |
|-------|-------|---------|
| Level 1 | Chinese numeral + 顿号 | 一、二、三、… |
| Level 2 | Arabic numeral + period | 1. 2. 3. |
| Level 3 | Arabic decimal | 1.1  1.2  2.1 |
| Level 4 | Arabic decimal | 1.1.1  1.1.2 |
| List items / steps | Parenthesized numeral | 1)  2)  3) |

### Fonts

- **All headings**: 黑体 (Chinese), Times New Roman (Western), **Bold**
- **Body text**: 宋体 (Chinese), Times New Roman (Western)
- **Heading sizes**:
  - Level 1: 三号 (16 pt)
  - Level 2: 小三 (15 pt)
  - Level 3: 四号 (14 pt)
  - Level 4: 四号 (14 pt) — or follow document convention
- **Font color**: "文字 1" (default text color, usually black)

### Paragraph Spacing

| Level | Space Before | Space After |
|-------|--------------|-------------|
| Level 1 | 18 pt | 0.5 line |
| Level 2 | 10 pt | 0.5 line |
| Level 3 | 10 pt | 0.5 line |
| Level 4 | 10 pt | 0.5 line |

### Table Formatting

- Horizontal alignment: left
- Vertical alignment: center
- First row: bold + gray background
- Cell margins: top = 0.2 cm, left = 0.2 cm

## Workflow

1. **Read the source document** using `python-docx` or another appropriate tool.
2. **Analyze structure**: identify which paragraphs are headings and which are body text / list items / steps.
3. **Apply heading styles** with correct numbering, fonts, sizes, bold, color, and paragraph spacing.
4. **Convert procedure/checklist paragraphs** to parenthesized numbering (`1)`, `2)`, `3)` …) within each section.
5. **Format tables** according to the table rules above.
6. **Save the output** as a new `.docx` file. Prefer adding a suffix like `_排版重排` or `_formatted` to avoid overwriting the original.
7. **Report** the output path and a brief summary of changes.

## Bundled Script

Use the bundled Python script at `scripts/format_docx.py` for deterministic formatting:

```bash
python scripts/format_docx.py <input.docx> <output.docx>
```

The script performs the core formatting automatically. After running it, inspect the output and make any manual adjustments needed for edge cases (unusual tables, mixed numbering, page headers/footers, etc.).

## Edge Cases

- If a heading is missing its numbering (e.g. "结构和组成"), infer the correct decimal prefix from the surrounding headings.
- If a paragraph contains multiple numbered steps (e.g. "4.1 …；4.2 …"), split it into separate paragraphs and renumber.
- If lettered list items (a, b, c, d) appear, convert them to `a) b) c) d)` and ensure continuity.
- Preserve cover pages, table of contents, headers, footers, and version information without reformatting unless explicitly requested.
- Do not alter document content — only formatting, numbering, and styles.
