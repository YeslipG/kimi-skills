---
name: quotation-generator
description: Generate professional Chinese quotation documents for two company versions - Beijing GuoHua and Nantong Hope. Use when the user asks to create a quotation, 报价单, 报价, price quote, or quote document.
---

# Quotation Generator

Generate formatted quotation documents based on a two-company template system.

## Supported Outputs

| Format | Supported | Default |
|--------|-----------|---------|
| DOCX | Yes | Yes |
| PDF | Yes | No |

## Workflow

### Step 1: Identify the Company Version

- **北京国华 / 国华** -> Read `references/guohua_version.md`
- **南通厚普 / 厚普** -> Read `references/hope_version.md`

If not specified, ask user to clarify.

### Step 2: Read Reference Files

Read both before generating:
- `references/style_contract.md`
- `references/structure_contract.md`

### Step 3: Extract Data from User Screenshot

Extract: customer name, date, product items (name, model, unit, quantity, unit price, remarks).

### Step 4: Generate Document

#### CRITICAL Layout Rules

1. **No Logo**: Do NOT insert any logo image.

2. **Company name (top of page)**:
   - Chinese: bold + italic, 18pt, centered, **single line only** (shrink if needed, min 16pt)
   - English: italic, 11.5pt, centered, directly below Chinese, **single line only**

3. **"报 价 单" + date**: Use 3-column borderless table: [empty] | ["报 价 单" bold 20pt centered] | ["日 期 ：YYYY-MM-DD" right-aligned]. This centers the title on the page.

4. **Unified 8-column table**: Single table for all content (company info + items + notes), merged cells for layout.

5. **Column widths**:
   - 序号: 0.75cm (minimum)
   - 名称: ~8cm (remaining space)
   - 型号/规格: 2.0cm
   - 单位: 0.75cm (minimum)
   - 数量: 0.85cm (minimum)
   - 单价(元): 1.7cm
   - 总价(元): 1.7cm
   - 备注: 1.2cm

6. **Single-line rule**: All text on single line. If >6 Chinese chars, shrink font (base 10pt, min 8pt).

7. **Info area (rows 1-5)**:
   - Row 1 left: "客户名：**[name]**" (8pt, single line)
   - Row 1 right: "报价单位：[company]" (8pt, single line)
   - Rows 2-5: address/contact/tel/fax (8pt)
   - All 5 rows: **identical fixed height 0.55cm** (use trHeight with hRule="atLeast")
   - Line spacing: 11pt, paragraph spacing: 0

8. **Borders**: All cells solid black borders.

#### Document Structure

Top (before table):
- Chinese company name (bold+italic, 18pt, centered, single line)
- English company name (italic, 11.5pt, centered, single line)
- 3-col layout: [empty] | "报 价 单" (bold 20pt) | "日 期 ：YYYY-MM-DD" (right)

Unified 8-col table:
- Row 1: "客户名：**xxx**" | "报价单位：xxx"
- Row 2: empty | "地址：xxx"
- Row 3: empty | "联系人：xxx"
- Row 4: empty | "电话：xxx"
- Row 5: empty | "传真：xxx" (GuoHua only)
- Greeting: merged 8 cols, 9pt
- Headers: 序号 名称 型号/规格 单位 数量 单价(元) 总价(元) 备注
- Data rows
- Total row
- Notes: merged 8 cols

#### Typography

- Font: NotoSans CJK or Microsoft YaHei consistently
- Info area: 8pt, line spacing 11pt, no paragraph spacing
- Greeting: 9pt
- Headers/data: auto 10pt/8pt based on char count
- All content single line

### Step 5: Calculate Totals

- 总价 = 数量 x 单价
- 合计 = sum of all 总价

## Important Notes

- **NO LOGO**
- Hope version has no fax row
- Greeting and 4 notes are identical across versions
- Date: "日 期 ：YYYY-MM-DD" (with spaces)
- "报 价 单": single spaces
- Use current date if none provided
- Company title: bold AND italic
- Info rows 1-5: identical fixed height 0.55cm
- Shrink font (min 8pt) if content exceeds 6 chars
- "客户名" followed by colon: "客户名：**xxx**"
- "报 价 单" centered via 3-column layout
