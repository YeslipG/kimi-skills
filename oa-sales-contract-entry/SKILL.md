---
name: oa-sales-contract-entry
description: Use this skill whenever the user asks to enter, upload, or record a sales contract into the OA system / 销售合同台账 / 合同台账, especially when they provide a contract PDF or say to follow the same OA contract entry process. This skill extracts contract fields from the attachment, opens the logged-in Edge OA page, fills the new sales contract ledger form, uploads the contract attachment, verifies every required field, and stops before final save unless the user explicitly asks to save.
---

# OA Sales Contract Entry

Use this skill to录入新销售合同到 OA 的“销售合同台账”. The goal is speed with verification: extract once, fill by stable controls, verify the form, and avoid final submission unless explicitly approved.

## Success criteria

The task is complete when the OA new contract form is filled and visibly verified with these fields:

- 合同附件: exactly the user-provided contract file, not extra files.
- 合同类型: 销售合同.
- 合同年份: year from the contract date.
- 合同单位: 北京国华技术有限公司, unless the user says otherwise.
- 甲方: the party identified in the contract as 甲方 or 买受方.
- 金额: the contract tax-included total, using the OA field unit.
- 付款方式: 开票挂账付全款, unless the user says otherwise.
- 合同名称: the attachment filename.
- 省份: province/region inferred from 甲方地址.
- 文件类型: 复印件.
- 份数: 2.
- 合同说明: the attachment filename.

Stop on the filled form before clicking 保存 / 保存并新建 / 提交, unless the user explicitly instructs final saving.

## Inputs to extract

From each contract PDF/image:

1. 文件名: use the exact basename, including extension.
2. 合同日期: use order date, signing date, or document date. If multiple dates exist, prefer the contract/order date that identifies the transaction.
3. 合同年份: `YYYY` from 合同日期.
4. 含税金额总计: extract the total tax-included amount in yuan.
5. 甲方名称/买受方名称 and 甲方地址/买受方地址: fill OA `甲方` with the identified 甲方 or 买受方 name, and use the address to infer 省份.
6. 乙方/合同单位: usually 北京国华技术有限公司.

If the OA field label is `金额(万元)`, convert yuan to ten-thousand yuan. Example: `38260` yuan -> `3.826000` 万元. Do not enter raw yuan into a 万元 field.

## Fast path

1. Read the contract first.
   - Use PDF/OCR tools to extract text and tables.
   - Prepare a small field checklist before opening OA.
   - If a required value is ambiguous, stop and ask before browser entry.

2. Use Edge with the user's logged-in session.
   - Prefer the existing Edge window/tab if it is already logged in.
   - If needed, open:
     `http://114.116.12.172:8899/wui/index.html#/main/portal/portal-10-15?menuIds=0,10&menuPathIds=0,10&_key=7um3hj`
   - If not logged in, ask the user to log in and then continue.

3. Enter the sales contract ledger.
   - Click the right-side `销售合同台账` entry when visible.
   - If an Edge tab titled `合同台账` is already open and it is the sales contract ledger list, use it directly.
   - If a modal says the previous page/project will auto-exit, click `确定`.
   - On the ledger list page, click top-right `新建`.

4. Upload the attachment first.
   - Use the form's `上传附件` / `选择文件` control.
   - Upload exactly the provided contract file path.
   - Avoid selecting multiple files in the file dialog. Do not use `Ctrl+A` inside the file list.
   - After upload, verify the attached filename and size row appears before filling the rest.
   - If extra files are accidentally attached and the record has not been saved, abandon that new form and create a clean one.

5. Fill fields in the required OA order.
   - The order is mandatory because OA may clear dependent fields when earlier fields change.
   - First: upload and verify the contract attachment.
   - Second: set `合同类型` to `销售合同`.
   - Third: set `合同单位` to `北京国华技术有限公司`.
   - Fourth: fill all remaining fields.
   - If this order is broken, or if setting a field clears earlier values, abandon the current new form and restart from a clean new form instead of patching the old state.

6. Fill fixed and extracted fields.

| OA field | Value |
|---|---|
| 合同类型 | 销售合同 |
| 合同年份 | extracted year |
| 合同单位 | 北京国华技术有限公司 |
| 甲方 | extracted 甲方 or 买受方 |
| 金额 / 金额(万元) | extracted tax-included total, converted if field says 万元 |
| 付款方式 | 开票挂账付全款 |
| 合同名称 | exact attachment filename |
| 省份 | province/region from 甲方地址 |
| 文件类型 | 复印件 |
| 份数 | 2 |
| 合同说明 | exact attachment filename |

7. Verify and stop.
   - Confirm every required value via screenshot or UI Automation text.
   - Tell the user the form is filled and not saved.
   - Only click 保存 / 保存并新建 if the user explicitly asks to save.

## Browser control guidance

Prefer stable UI Automation / accessibility controls over raw screenshots when possible.

- For combo boxes such as 合同单位, 合同年份, 文件类型, expand the combo and select the exact menu item.
- For 合同类型, the field may open a search/list popup. Select `销售合同` from the list. If the popup has no obvious OK button, invoking the full row may directly return the value to the form.
- If a screenshot or Codex window steals focus, reactivate Edge before clicking.
- If Chrome or another browser is accidentally foregrounded, minimize it or activate Edge by the process/window title `合同台账`.
- Maximize Edge before final verification so all fields are readable.
- Do not rely on one screenshot coordinate after window size changes; re-query controls or take a fresh screenshot.

## Known OA quirks

- The right-side portal shortcut may not show `销售合同台账` at first. If a `合同台账` tab is already open, using it is faster.
- Field order matters: attachment must be uploaded first, `合同类型` must be selected second, and `合同单位` third. Changing these fields later can clear values already entered below.
- The contract type selector may show a modal titled `合同类型`; rows can include `外购合同`, `销售合同`, `销售采购合同`. Choose exactly `销售合同`, not `销售采购合同`.
- The form may visually show a file input text like `选择文件: 未选择文件` even after upload; trust the uploaded attachment row above it if the filename and size are visible.
- Screen scaling can make screenshot coordinates differ from physical click coordinates. Use UIA element rectangles or browser/window automation when available.

## Final response format

When done, respond concisely in Chinese:

```text
已填好并停在表单页，未点“保存/保存并新建”。

已核对：合同类型、年份、合同单位、甲方、金额、付款方式、合同名称、省份、文件类型、份数、附件和合同说明。
金额按页面单位填写为：[value]。
```

If something could not be completed, state the exact blocker and the current safe state.
