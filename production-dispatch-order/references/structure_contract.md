# Structure Contract - Production Dispatch Order

## Form Identity

- **Form type**: Production task dispatch order (生产任务派工单)
- **Issuing company**: 南通厚普机械科技有限公司 (Nantong Houpu Machinery Technology Co., Ltd.)
- **Sheet name**: "派工单"

## Grid Dimensions

- **17 rows** (exactly, no more, no less)
- **9 columns** (A through I, exactly)
- Do not add separator rows, extra header rows, or padding rows

## Section Hierarchy

### Section 1: Header (Rows 1-2)
- **Row 1**: Company name — "南通厚普机械科技有限公司" (merged A1:I1)
- **Row 2**: Form title — "生产任务派工单" (merged A2:I2)
- These rows have NO borders

### Section 2: Metadata (Rows 3-4)
- **Row 3 - File Number & Issue Date**:
  - A3: Label "文件编号" (left-aligned, no colon)
  - B3:D3 (merged): File number value area (blank if no data)
  - E3:F3 (merged): Label "发放日期" (center-aligned, no colon)
  - G3:I3 (merged): Issue date value area (blank if no data)
- **Row 4 - User & Completion Date**:
  - A4: Label "使用方" (center-aligned, no colon, no spaces)
  - B4:D4 (merged): User company value area (blank if no data)
  - E4:F4 (merged): Label "完成日期" (center-aligned, no colon)
  - G4:I4 (merged): Completion date value area (blank if no data)

### Section 3: Order Content Table (Rows 5-15) — CRITICAL SECTION

This is the most complex section. It combines:
1. A vertically merged label cell spanning all data rows
2. A table header row
3. 10 blank data rows

#### Row 5 — Table Header
- **A5:A13** (merged, 9 rows): Label "订单" + newline + "内容" — CRITICAL, must span rows 5-13
- **B5**: "序号" (left-aligned)
- **C5**: "名称" (left-aligned)
- **D5**: "数量" (left-aligned)
- **E5**: "单位" (left-aligned)
- **F5:I5** (merged): "备注" (center-aligned)

#### Rows 6-15 — 10 Data Rows
- **A6-A15**: Empty (part of A5:A13 merge)
- **B6-B15**: Sequence numbers 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 (integers, NOT 1.0/2.0)
- **C6-C15**: Item name value areas (blank if no data)
- **D6-D15**: Quantity value areas (blank if no data)
- **E6-E15**: Unit value areas (blank if no data)
- **F6:I6 through F15:I15** (each row merged): Remarks value areas (blank if no data)

### Section 4: Special Requirements (Row 16)
- **A16**: Label "特殊" + newline + "要求" (center-aligned, wrap text)
- **B16:I16** (merged): Special requirements value area (blank if no data)
- This row is taller (35.5 pt) than standard data rows

### Section 5: Signature (Row 17)
- **A17:I17** (merged): "签发：" followed by blank space
- Font: 11pt 等线 (DengXian)
- Alignment: left horizontally, bottom vertically
- **ONLY "签发："** — do NOT add "签章：" or "日期：" fields
- Has a medium-weight top border, no other borders

## Labels Reference (No Colons)

All labels appear EXACTLY as follows (no trailing colons):
- "文件编号" (not "文件编号：")
- "使用方" (not "使用方：", not "使 用 方")
- "发放日期" (not "发放日期：")
- "完成日期" (not "完成日期：")
- "序号" (not "序号：")
- "名称" (not "名称：")
- "数量" (not "数量：")
- "单位" (not "单位：")
- "备注" (not "备注：")
- "订单" + newline + "内容"
- "特殊" + newline + "要求"
- "签发：" (this one HAS a colon, followed by spaces)

## Data Extraction Rules from Screenshots

When processing a screenshot to auto-fill this form:

1. **Identify the issuing company**: Look for company names in the screenshot
   - If "南通厚普机械科技有限公司" appears, it is the ISSUER (header row 1)
   - Do NOT use this as the "使用方" (user) field

2. **Identify the user company (使用方)**:
   - Look for OTHER company names in the screenshot that are NOT:
     - 南通厚普机械科技有限公司 (or abbreviation 南通厚普)
     - 北京国华 (or abbreviation)
   - Extract that company name (or its abbreviation) for the "使用方" field
   - If only 南通厚普 and 北京国华 appear, leave 使用方 blank
   - The extracted company name goes into B4:D4

3. **Extract order items**: Look for tabular data with:
   - Item names (名称)
   - Quantities (数量)
   - Units (单位)
   - Any remarks (备注)
   - Fill into corresponding rows 6-15
   - Sequence numbers are always 1-10, write as integers

4. **Extract dates**:
   - Issue date (发放日期) — when the form was issued
   - Completion date (完成日期) — when work should be completed
   - Format: use the date format visible in the screenshot

5. **Extract file number** (文件编号): If visible, copy as-is into B3:D3

6. **Extract special requirements** (特殊要求): Copy any special instruction text into B16:I16

7. **Leave blank** any fields for which no information is found in the screenshot

## Output Format

- Default output: XLSX (Excel workbook)
- Single worksheet named "派工单"
- The generated workbook must be a native editable Excel file
- All cells should remain editable (no protection)
- Formula-free (static values only)
- All sequence numbers must be written as integers (1, 2, 3...) not floats (1.0, 2.0, 3.0)
