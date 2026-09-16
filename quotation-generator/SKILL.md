---
name: quotation-generator
description: Generate professional Chinese quotation documents (报价单) for Beijing GuoHua or Nantong Hope. Use whenever the user asks for a quotation, 报价单, 报价, price quote, quote document, or needs to turn a contract/screenshot into a formatted Word quotation. Also use whenever a 梅花 (Meihua) inquiry sheet (询价单 xlsx) appears — price it against the 梅花年度合同 attachment price list and generate the quotation.
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

- **北京国华 / 国华** -> Use template: `C:/Users/yesli/Desktop/2026项目/260426进行中/260402段王报价单99000/国华/260402报价单模板段王-国华.docx`
- **南通厚普 / 厚普** -> Use template: `C:/Users/yesli/Desktop/2026项目/260426进行中/260402段王报价单99000/厚普/260402报价单模板段王-厚普.docx`

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
- Copy it to the desktop: `C:/Users/yesli/Desktop/报价单_<公司>_<客户简称>.docx`.
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

## 梅花集团报价流程 (Meihua inquiry + annual contract)

Use this dedicated flow whenever the source is a 梅花询价单 xlsx (filename like `...询价单.xlsx`, sheet named `<基地>-订单`) plus the 梅花年度合同 PDF. The quoting company is always **北京国华** (乙方 of the annual contract).

### Inputs

- **询价单 xlsx**: header rows give 需方 (吉林梅花/新疆梅花/通辽梅花), 询价单位 `梅花集团采购部`, 询价联系人 `田帅鹏 18031609705`. The item table columns are: `序号 | 五金编码 | 名称型号 | 数量 | 单位 | 单价 | 金额 | 使用部门 | 备注 | 基地 | 货期 | 运输方式`. 单价/金额 are blank — they must come from the annual contract.
- **年度合同 PDF**: the user usually passes the path; otherwise look in `D:/YeslipW/021-Daily/1-Contract/` for the latest `梅花*年度合同.pdf`. **It is a scanned PDF with no text layer** — `page.get_text()` returns empty. Render every page to PNG at 200 dpi with `fitz` and read the images visually.

### Pricing: match against 附件1 定标清单

The contract's last pages hold `附件1 定标清单` with columns: `序号 | 执行基地 | 物料代码 | 长描述 | 单位 | 含税含运费单价 | 品牌 | 货期 | 质保期 | 备注`.

- Match each inquiry item by code: 询价单 **五金编码** = 清单 **物料代码**. Do not match by name alone — names can differ slightly.
- Take **含税含运费单价** as the unit price.
- Split the inquiry's 名称型号 at `\`: part before it is 产品名称, part after is 规格型号 with the trailing brand word `国华` dropped (e.g. `跳汰机畚斗\YSD02-002 316L 国华` → 名称 `跳汰机畚斗`, 规格 `YSD02-002 316L`).

### Fixed field values

- 收件单位：`梅花集团采购部`；收件人：`田帅鹏`；电话：`18031609705`
- 关于：`跳汰机配件报价` (or adapt to the actual items)
- Note paragraph (replaces the template's `注：本报价未税含运费。`), derived from contract clauses 5.5/6.2/6.3 and 附件1:

  `注：本报价含13%增值税专用发票，含运费；付款方式：货到验收合格后付款（电汇50%，银行承兑50%）；货期30天，质保期12个月；本报价有效期30天。`

  If a newer annual contract changes these terms, follow the newer contract.

Everything else (template, generation, layout gate, delivery) follows the standard workflow above.
