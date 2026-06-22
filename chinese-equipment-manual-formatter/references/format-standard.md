# Fixed formatting standard

Use this standard unless the user provides a newer rule in the current request. Current user instructions always take precedence.

## Numbering

| Level | Format | Example |
|---|---|---|
| Heading 1 | Chinese numeral + `、` | `一、` `二、` `三、` |
| Heading 2 | Arabic numeral + period | `1.` `2.` `3.` |
| Heading 3 | Hierarchical Arabic numerals | `1.1` `1.2` `2.1` |
| Heading 4 | Three-part hierarchy | `1.1.1` `1.1.2` |
| List/step | Arabic numeral + right parenthesis | `1)` `2)` `3)` |

Numbering is part of the visible paragraph text unless the existing document uses reliable automatic multilevel numbering that can be preserved without changing appearance.

## Fonts

- Chinese headings: SimHei (`黑体`).
- Chinese body: SimSun (`宋体`).
- Western text and digits: Times New Roman.
- Font color: theme `Text 1` or black.

Set both East Asian and Western font attributes. Do not assume changing only the visible Latin font also changes Chinese glyphs.

## Heading styles

| Property | Heading 1 | Heading 2 | Heading 3 |
|---|---:|---:|---:|
| Chinese font | SimHei | SimHei | SimHei |
| Western font | Times New Roman | Times New Roman | Times New Roman |
| Size | 16 pt / 三号 | 15 pt / 小三 | 14 pt / 四号 |
| Weight | Bold | Bold | Bold |
| Color | Text 1 | Text 1 | Text 1 |
| Space before | 18 pt | 10 pt | 10 pt |
| Space after | 0.5 line | 0.5 line | 0.5 line |
| Alignment | Left | Left | Left |

For Heading 4, use SimHei + Times New Roman, bold, no larger than Heading 3, and retain a clear visual distinction from body text.

Avoid leaving a heading alone at the bottom of a page. Use keep-with-next where supported.

## Body

- Chinese: SimSun.
- Western text/digits: Times New Roman.
- Preserve reasonable existing body size, line spacing, indentation, emphasis, and paragraph relationships unless the user supplied more specific body settings.
- Remove meaningless repeated empty paragraphs only when they create visible layout defects.

## Tables

- Horizontal alignment inside cells: left.
- Vertical alignment inside cells: center.
- First row: bold with light gray fill.
- Cell top margin: 0.2 cm (approximately 113 twips).
- Cell left margin: 0.2 cm (approximately 113 twips).
- Chinese: SimSun; Western/digits: Times New Roman.
- Preserve merged cells, borders, row order, and column widths unless required to keep the table within page margins.

## TOC

- Automatic TOC with heading levels 1–3.
- Contents and page numbers must be fully updated after formatting.
- TOC must end before the body section break.
- Do not leave an unintended blank page between the TOC and body.

## Header

- No visible header on cover or TOC pages.
- Begin on the first body page.
- Left aligned.
- Add a short black vertical decorative line at the far left, then the full cover title.
- Exclude company name, organization name, date, and version metadata.
- Chinese: SimSun; Western: Times New Roman; recommended size 9 pt.
- Keep the header clear of body content.

A paragraph left border is an acceptable implementation of the decorative line when it produces a short, stable vertical rule beside the title.

## Footer and page fields

- No visible page number on cover or TOC pages.
- Restart body numbering at 1.
- Center the footer.
- Visible format: `第X页/共Y页`.
- Use live fields: `第{ PAGE }页/共{ SECTIONPAGES }页`.
- Do not use `NUMPAGES` when front matter must be excluded from the total.

## Output

- Output `.docx` only unless another format is requested.
- Do not overwrite the source.
- Default filename: `[原文件名]_按规则排版.docx`.
