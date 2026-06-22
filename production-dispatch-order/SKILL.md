---
name: production-dispatch-order
description: Generate production task dispatch order forms (生产任务派工单) in Excel format. Replicate the style and layout of a reference dispatch order form, then auto-fill content from user-provided screenshots. Use when the user asks to create a 派工单, dispatch order, production task form, or wants to replicate the style of a manufacturing dispatch form. Also use when the user uploads a screenshot of a dispatch order and asks to extract and fill data into a formatted Excel form. Supports Chinese/CJK content.
---

# Production Dispatch Order Skill

Generate production task dispatch order forms (生产任务派工单) matching a reference visual style, with auto-fill capability from screenshot content.

## Reference Information

- **Reference source**: Uploaded XLS artifact
- **Reference artifact type**: XLS
- **Reference File Type**: XLSX
- **Style contract**: See `references/style_contract.md`
- **Structure contract**: See `references/structure_contract.md`

## Supported Outputs

- XLSX (default and primary)

## Default Output

XLSX when user does not explicitly request a format.

## Workflow Overview

1. Analyze user input (screenshot or explicit data)
2. Extract form data from screenshot if provided
3. Determine the user company (使用方)
4. Build the Excel form with reference styling
5. Fill extracted data into the form
6. Save the output workbook

## Step 1: Analyze User Input

Determine what the user has provided:

- **Screenshot uploaded**: Extract all visible text and tabular data from the image
- **Explicit data provided**: Use the data directly
- **No data**: Create a blank template with the reference styling

## Step 2: Extract Data from Screenshot

When a screenshot is provided, carefully read all visible text:

1. **Find company names** in the screenshot:
   - 南通厚普机械科技有限公司 (or 南通厚普) = the ISSUER, always goes in header row 1
   - 北京国华 (or any variation) = IGNORE for the user field
   - Any OTHER company name = the USER (使用方) field value

2. **Find tabular order content**: item names, quantities, units, remarks

3. **Find dates**: issue date and completion date

4. **Find special requirements text**

5. **Find file number** if present

## Step 3: Determine User Company (使用方)

Apply this rule strictly:

- The issuing company is always 南通厚普机械科技有限公司
- The user field (使用方) should contain the OTHER company appearing in the screenshot
- If the only companies visible are 南通厚普 and 北京国华, leave 使用方 blank
- Use the full company name or its abbreviation as it appears in the screenshot

## Step 4: Build the Excel Form

Read `references/style_contract.md` for complete visual specifications.

### Critical Layout Rules (17 rows x 9 columns A-I)

The form MUST have exactly 17 rows and 9 columns (A through I). Do not add extra rows or columns.

| Row | Content | Merge Range | Font Size | Alignment |
|-----|---------|-------------|-----------|-----------|
| 1 | Company name "南通厚普机械科技有限公司" | A1:I1 | 22pt宋体 | center, center |
| 2 | Form title "生产任务派工单" | A2:I2 | 18pt宋体 | center, center |
| 3 | "文件编号" label / blank value / "发放日期" label / blank value | A3 alone, B3:D3, E3:F3, G3:I3 | 14pt宋体 | label: left,center; date labels: center,center |
| 4 | "使用方" label / blank value / "完成日期" label / blank value | A4 alone, B4:D4, E4:F4, G4:I4 | 14pt宋体 | label: center,center; date labels: center,center |
| 5 | Header: "序号"/"名称"/"数量"/"单位" + "备注" + A5:A13 merged | B5,C5,D5,E5,F5:I5, A5:A13 | 14pt宋体 | headers left,center; 备注 center,center |
| 6-15 | 10 data rows with sequence 1-10 | F6:I6 through F15:I15 (remarks merged per row) | 14pt宋体 | sequence left,center |
| 16 | "特殊要求" label + blank value area | A16 alone, B16:I16 | 14pt宋体 | label center,center; wrap text |
| 17 | "签发：" + blank space | A17:I17 | 11pt等线 | left, bottom |

### Critical Styling Rules

- **Font**: 宋体 (SimSun) for all text except signature line which uses 等线 (DengXian)
- **All text regular weight** (no bold anywhere)
- **No background fill colors** (white background throughout)
- **No header row background color** (the table header row is plain white, not dark gray)
- **Alignment**: Follow the per-cell alignment specified in style_contract.md precisely
- **Borders**: medium-weight outer edges, thin-weight inner borders (see style_contract for exact per-cell border map)
- **Wrap text**: Enabled only for 订单内容 (A5:A13) and 特殊要求 (A16) cells

### Order Content Merged Cell (CRITICAL)

The merged cell A5:A13 containing "订单\n内容" is the most critical structural element. It must:
- Span rows 5 through 13 (all 10 data rows)
- Be in column A
- Contain the text "订单" + newline + "内容"
- Have wrap text enabled
- Be center-aligned both horizontally and vertically

### Signature Line (CRITICAL)

Row 17 must contain ONLY "签发：" followed by blank space. Do NOT add:
- "签章：" field
- "日期：" field
- Any other fields

### Labels Without Colons

All labels must NOT have trailing colons:
- Use "文件编号" not "文件编号："
- Use "使用方" not "使用方："
- Use "发放日期" not "发放日期："
- Use "完成日期" not "完成日期："

### Column Layout

Use exactly 9 columns (A through I). Do not use fewer columns.

## Step 5: Fill Extracted Data

Map extracted data to form fields:

| Form Field | Target Cell(s) | Data Source |
|-----------|----------------|-------------|
| Header company | A1:I1 | Always "南通厚普机械科技有限公司" |
| File number label | A3 | Always "文件编号" (left-aligned) |
| File number value | B3:D3 | From screenshot (leave blank if not found) |
| Issue date label | E3:F3 | Always "发放日期" (center-aligned) |
| Issue date value | G3:I3 | From screenshot (leave blank if not found) |
| User label | A4 | Always "使用方" (center-aligned) |
| User company value | B4:D4 | Other company name from screenshot (see Step 3 rules) |
| Completion date label | E4:F4 | Always "完成日期" (center-aligned) |
| Completion date value | G4:I4 | From screenshot (leave blank if not found) |
| Order content label | A5:A13 | Always "订单\n内容" |
| Table headers | B5:I5 | Always "序号"/"名称"/"数量"/"单位"/"备注" |
| Order items rows | B6:E15 | Fill sequentially from screenshot table (names, quantities, units) |
| Sequence numbers | B6:B15 | Always integers 1-10 (not 1.0, 2.0) |
| Remarks | F6:I15 (merged per row) | Fill sequentially from screenshot |
| Special requirements label | A16 | Always "特殊\n要求" |
| Special requirements value | B16:I16 | From screenshot (leave blank if not found) |
| Signature | A17:I17 | Always "签发：" followed by blank space |

Fill data rows sequentially starting from row 6. Leave unused rows blank.

## Step 6: Save Output

- Save as `.xlsx` format
- Sheet name: "派工单"
- Ensure all cells remain editable (no protection)
- No formulas; use static values only
- Row heights: row1=28pt, row2=23.5pt, rows3-14=18pt each, row15 (special requirements)=35.5pt, row16 (signature)=28.5pt
