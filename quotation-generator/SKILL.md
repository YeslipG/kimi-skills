---
name: quotation-generator
description: Generate professional Chinese quotation documents (报价单) for Beijing GuoHua or Nantong Hope. Use whenever the user asks for a quotation, 报价单, 报价, price quote, quote document, or needs to turn a contract/screenshot into a formatted Word quotation.
---

# Quotation Generator

Generate formatted quotation documents for two company versions: **北京国华** and **南通厚普**.

## Supported Outputs

| Format | Supported | Default |
|--------|-----------|---------|
| DOCX | Yes | Default |
| PDF | No | Usually not needed; PDF is only used internally for layout verification |

## Workflow

### Step 1: Identify the Company Version

- **北京国华 / 国华** -> Use template: `C:/Users/yesli/OneDrive/桌面/2026项目/260426进行中/260402段王报价单99000/国华/260402报价单模板段王-国华.docx`
- **南通厚普 / 厚普** -> Use template: `C:/Users/yesli/OneDrive/桌面/2026项目/260426进行中/260402段王报价单99000/厚普/260402报价单模板段王-厚普.docx`

If the user does not specify a company, ask which one to use. Do not guess.

If the template file is missing, fall back to the **Layout Rules** below and build a clean single-page table from scratch.

### Step 2: Extract Data

Read the source(s) the user provides (contract `.doc`/`.docx`, screenshot `.png`/`.jpg`, Excel, chat text). Extract:

- Customer name (收件单位 / 客户名)
- Contact person / phone / fax if available
- Date (use current date if not provided): `YYYY年MM月DD日`
- Subject line (e.g. `YT35-2-2-2 跳汰机配件报价`)
- Product items: name, model/spec, unit, quantity, unit price, remarks
- Term mappings the user gives (e.g. "分阀叶片就是风门总成")
- Tax / freight / payment terms if stated

If the source is an old `.doc` file, use Word COM (`win32com.client`) or `antiword` to extract text/tables. Prefer Word COM when available because it preserves Chinese characters correctly.

### Step 3: Generate the Document

**Preferred approach: modify the company template.**

1. Open the template with `python-docx`.
2. Update the info table:
   - 收件单位 / 发件单位
   - 收件人 / 电话
   - 电话 / 传真
   - 传真 / 页数 (usually `1`)
   - 关于 / 日期
3. Update the greeting line if needed.
4. Replace/extend the item rows:
   - Clone an existing item row (`copy.deepcopy(row._tr)` and insert before the total row).
   - Fill each cell: 序号, 产品名称, 规格型号, 单位, 数量, 单价, 金额, 备注.
5. Update the total row: 金额 = sum of all item 金额.
6. Update the note paragraph at the bottom with tax/freight/payment/validity terms.

**Formatting rules:**

- Use **Microsoft YaHei** consistently for Chinese text.
- Format **all monetary values** with thousands separators and two decimals (e.g. `12,000.00`).
- Keep numbers right-aligned or centered per the template.
- Do not insert any logo.
- Respect the template's existing fonts, borders, and table structure.

### Step 4: Layout Quality Gate (Mandatory)

Before telling the user the file is ready, verify the layout:

1. Save the DOCX to `D:/Kimi/output/`.
2. Use Word COM to export it to a temporary PDF:
   ```python
   from win32com.client import Dispatch
   app = Dispatch('Word.Application')
   app.Visible = False
   doc = app.Documents.Open(docx_path)
   doc.ExportAsFixedFormat(pdf_path, ExportFormat=17, OpenAfterExport=False)
   doc.Close(False)
   app.Quit()
   ```
3. Render page 1 (and page 2 if it exists) with `fitz` (PyMuPDF):
   ```python
   import fitz
   doc = fitz.open(pdf_path)
   for i in range(doc.page_count):
       doc.load_page(i).get_pixmap(dpi=150).save(f'preview_p{i+1}.png')
   ```
4. Inspect the PNG(s). If you see any of the following, fix the DOCX and re-verify:
   - More than one page for a simple quote.
   - Text wrapping inside narrow columns that breaks the table.
   - Column misalignment, overflow, or huge empty spaces.
   - Inconsistent amount formatting.

To fix overflows, adjust column widths (`table.columns[i].width`), shrink long text (>6 Chinese chars) down to 8pt, or shorten notes/specs.

### Step 5: Deliver

- Save final file to `D:/Kimi/output/报价单_<公司>_<客户简称>.docx`.
- Copy it to the desktop: `C:/Users/yesli/OneDrive/桌面/报价单_<公司>_<客户简称>.docx`.
- Verify the desktop copy exists and has the same byte size as the output copy.
- Tell the user the desktop path and the total amount.

## Fallback Layout Rules (if template is missing)

If you cannot use a template, build a single-page A4 DOCX with:

- Top: company name Chinese (bold+italic, 18pt, centered) and English (italic, 11.5pt, centered).
- Title: three-column borderless table: `[empty] | 报 价 单 (bold 20pt) | 日 期 ：YYYY-MM-DD`.
- A single 8-column table: 序号 | 名称 | 型号/规格 | 单位 | 数量 | 单价(元) | 总价(元) | 备注.
- Info rows, greeting, data rows, total row, notes — all inside the same table.
- All cells solid black borders.
- Row heights compact enough to fit one page.

## Critical Pitfalls to Avoid

- **Never set `w:gridCol w:w` or `w:trHeight w:val` in EMU manually.** Use python-docx properties (`column.width = Cm(x)`, `row.height = Cm(x)`, `row.height_rule = ...`) which convert to the correct Word units.
- **Do not build from scratch when a template exists.** The template already has the company format, fonts, and margins.
- **Do not skip the PDF preview.** Visual inspection catches layout problems that text extraction cannot.
- **Do not deliver until the file is on the desktop** per project rules.

## Example Notes Block

Use terms consistent with the source contract. Common defaults:

- `含13%增值税专用发票，含运费。`
- `付款方式：预付30%，余款70%发货前付清。`
- `本报价单有效期30天。`

If the source contract uses different terms, use those instead.
