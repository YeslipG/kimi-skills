# Style Contract - Production Dispatch Order

Reference source type: uploaded artifact
Reference artifact type: XLS
Reference File Type: XLSX

## Typography

- **Primary font**: 宋体 (SimSun) for all form content
- **Signature line font**: 等线 (DengXian) at 11pt
- **Font sizes** (precise from reference):
  - Company name (row 1): 22pt 宋体
  - Form title (row 2): 18pt 宋体
  - All labels and body text (rows 3-16): 14pt 宋体
  - Signature line (row 17): 11pt 等线
- **All text is regular weight** (not bold, not italic) — this is critical
- **Default text color**: black

### CJK Font Strategy

When 宋体 is not available, use a CJK-capable serif/song-style font such as:
- Noto Serif CJK SC
- Source Han Serif SC
- Any system-default Chinese serif font

Maintain consistent font across all cells. Do not mix Latin-only fonts with CJK fallback.

## Layout Grid

- **Columns**: A through I (9 columns total)
- **Defined column widths** (xlrd internal units, approximate character widths):
  - Col A: 2944 (~11.5 chars)
  - Col B: default (~8.4 chars)
  - Col C: 4949 (~19.3 chars, wider for item names)
  - Col D: default
  - Col E: default
  - Col F: 3157 (~12.3 chars, remarks start)
  - Col G: default
  - Col H: default
  - Col I: default
- **Row heights** (xlrd internal units, in points):
  - Row 1 (company): 28.0 pt
  - Row 2 (title): 23.5 pt
  - Rows 3-14 (form body + data rows): 17.5-18.0 pt
  - Row 15 (special requirements): 35.5 pt
  - Row 16 (actually row index 15 in 0-based): 35.5 pt — wait, check: row index 15 = row 16 = special requirements row = 35.5pt
  - Row 17 (signature): 28.5 pt

Corrected row heights from xlrd analysis:
- Row 1: 560 internal = 28.0 pt
- Row 2: 470 internal = 23.5 pt
- Rows 3-4 (metadata): 350 internal = 17.5 pt
- Rows 5-14 (header + 10 data rows): 360 internal = 18.0 pt each
- Row 15 (special requirements): 710 internal = 35.5 pt
- Row 16 (signature): Wait — let me recount. The reference has 17 rows (0-16 in 0-based):
  - Row index 0 = company: 560 = 28.0pt
  - Row index 1 = title: 470 = 23.5pt
  - Row index 2-3 = metadata: 350 = 17.5pt
  - Row index 4-14 = header + data: 360 = 18.0pt (11 rows)
  - Row index 15 = special requirements: 710 = 35.5pt
  - Row index 16 = signature: 570 = 28.5pt

## Color Palette

- **Background**: white (no fill, fill_pattern=0 throughout)
- **Text**: black
- **Borders**: black/gray auto color
- **No accent colors, no background fills, no conditional formatting**
- **CRITICAL**: The table header row (row 5) must NOT have any background color — it is plain white like all other cells

## Border Style (Precise Per-Cell Map)

Border line style codes: 0=none, 1=thin, 2=medium

### Row 1 (Company name) — Row 2 (Title)
- No borders on these rows (all edges = 0)
- These rows float above the bordered form area

### Row 3 (文件编号 / 发放日期)
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A3 (文件编号) | medium | thin | medium | thin |
| B3-D3 (blank value) | medium | thin | thin | thin |
| E3-F3 (发放日期 label) | medium | thin | thin | none |
| G3-I3 (blank value) | medium | thin | thin | medium |

### Row 4 (使用方 / 完成日期)
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A4 (使用方) | thin | thin | medium | thin |
| B4-D4 (blank value) | thin | thin | thin | thin |
| E4-F4 (完成日期 label) | thin | thin | thin | none |
| G4-I4 (blank value) | thin | thin | thin | medium |

### Row 5 (Header row)
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A5 (订单内容 top) | thin | none | medium | thin |
| B5 (序号) | thin | thin | thin | thin |
| C5 (名称) | thin | thin | thin | thin |
| D5 (数量) | thin | thin | thin | thin |
| E5 (单位) | thin | thin | thin | thin |
| F5-I5 (备注) | thin | none | thin | thin |

### Rows 6-14 (Data rows, 0-based 5-13)
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A6-A14 (订单 content blank) | none | none | medium | thin |
| B6-B14 (sequence) | thin | thin | thin | thin |
| C6-C14 (name) | none/n/a | thin/n/a | 0/thin | thin/n/a |
| D6-D14 (quantity) | none | thin | 0 | thin |
| E6-E14 (unit) | none | thin | 0 | thin |
| F6-I14 (remarks per row) | thin | thin | varies | varies |

Note: For the last data row (row 14, 0-based index 13), the bottom border transitions:
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A14 | none | none | medium | thin |
| B14 | thin | thin | thin | thin |
| F14-I14 | thin | thin | left varies | medium |

### Row 15 (last data row, 0-based 14)
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A15 | none | none | medium | thin |
| B15 | thin | thin | thin | thin |
| C15-E15 | none | thin | 0 | thin |
| F15 | thin | thin | medium | none |
| G15-H15 | thin | thin | none | none |
| I15 | thin | thin | none | medium |

### Row 16 (特殊要求, 0-based 15)
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A16 | thin | medium | medium | thin |
| B16-I16 | thin | medium | thin | thin |

### Row 17 (签发, 0-based 16)
| Cell | Top | Bottom | Left | Right |
|------|-----|--------|------|-------|
| A17-I17 | medium | none | none | none |

## Simplified Border Rule

For practical implementation, use this simplified approach:
- Apply a medium outer border to the entire form body (rows 3-16, cols A-I)
- Apply thin inner borders throughout
- Ensure left edge of column A and right edge of column I use medium weight
- Ensure top of row 3 and bottom of row 16 use medium weight
- The header/title rows (1-2) have no borders
- The signature row (17) has only a medium top border

## Alignment (Precise Per-Cell)

| Cell | Horizontal | Vertical | Wrap |
|------|------------|----------|------|
| A1 (company) | center | center | no |
| A2 (title) | center | center | no |
| A3 (文件编号) | left | center | no |
| A4 (使用方) | center | center | no |
| A5:A13 (订单内容) | center | center | YES |
| A16 (特殊要求) | center | center | YES |
| B5-E5 (table headers) | left | center | varies |
| F5:I5 (备注 header) | center | center | no |
| B6:B15 (sequence) | left | center | no |
| A17 (签发) | left | bottom | no |

Note: E3:F3 (发放日期) and E4:F4 (完成日期) labels are center-aligned horizontally.

## Cell Merging Pattern

Exact merge ranges from reference:
- A1:I1 (company name)
- A2:I2 (form title)
- B3:D3 (file number value area)
- E3:F3 (issue date label)
- G3:I3 (issue date value area)
- B4:D4 (user value area)
- E4:F4 (completion date label)
- G4:I4 (completion date value area)
- A5:A13 (order content label — spans all 10 data rows)
- F5:I5 (remarks header)
- F6:I6 through F14:I14 (remarks per data row, rows 6-14)
- F15:I15 (last data row remarks)
- B16:I16 (special requirements value area)
- A17:I17 (signature line)

## Print & Display

- Sheet view: gridlines shown
- No print-area restrictions
- Portrait orientation
- Standard A4 paper size implied
