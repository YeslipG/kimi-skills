---
name: oa-sales-contract-entry-kimi
description: |
  Use this skill whenever the user asks to enter, upload, or record a sales contract into the OA system / 销售合同台账 / 合同台账, especially when they provide a contract PDF or say to follow the same OA contract entry process. This skill extracts contract fields from the attachment, opens the logged-in OA page via Kimi WebBridge, fills the new sales contract ledger form, uploads the contract attachment, verifies every required field, and stops before final save unless the user explicitly asks to save.
  当用户需要将销售合同录入OA系统"销售合同台账"、上传合同附件、或按相同流程录入合同时，必须使用此skill。即使只说"录合同"、"传合同"、"合同台账"也应触发。
---

# OA Sales Contract Entry (Kimi WebBridge Edition)

Use this skill to 录入新销售合同到 OA 的"销售合同台账". The goal is speed with verification: extract once, fill by stable WebBridge controls, verify the form, and avoid final submission unless explicitly approved.

> **Prerequisite**: Kimi WebBridge daemon must be running. Check status first:
> ```bash
> ~/.kimi-webbridge/bin/kimi-webbridge status
> ```
> If not healthy, read `kimi-webbridge` skill's `references/operations.md` to install/start.

---

## 必须遵守的核心规则

填表顺序非常重要，**不能调整**。OA 表单存在联动逻辑，顺序错了会导致已填内容被清空。

**固定顺序如下：**

1. **先上传合同附件**。
2. **再选择 `合同类型` 为 `销售合同`**。
3. **再选择 `合同单位` 为 `北京国华技术有限公司`**。
4. **最后填写其他字段**。

> ⚠️ 如果先填了金额、名称等，再改 `合同类型` 或 `合同单位`，页面可能清空已经填写的内容。
> **只要顺序错了、字段被清空了、附件不对了，就不要在旧表单上修补，直接放弃当前新建页，回到列表重新新建。**

---

## Success criteria

The task is complete when the OA new contract form is filled and visibly verified with these fields:

- 合同附件: exactly the user-provided contract file, not extra files.
- 合同类型: 销售合同.
- 合同年份: year from the contract date.
- 合同单位: 北京国华技术有限公司, unless the user says otherwise.
- 甲方: the party identified in the contract as 甲方 or 买受方.
- 乙方: 北京国华技术有限公司.
- 金额: the contract tax-included total, using the OA field unit.
- 付款方式: 开票挂账付全款, unless the user says otherwise.
- 合同名称: the attachment filename.
- 省份: province/region inferred from 甲方地址.
- 文件类型: 复印件.
- 份数: 2.
- 合同说明: the attachment filename.

Stop on the filled form before clicking 保存 / 保存并新建 / 提交, unless the user explicitly instructs final saving.

---

## Inputs to extract

From each contract PDF/image:

1. **文件名**: use the exact basename, including extension.
2. **合同日期**: use order date, signing date, or document date. If multiple dates exist, prefer the contract/order date that identifies the transaction.
3. **合同年份**: `YYYY` from 合同日期.
4. **含税金额总计**: extract the total tax-included amount in yuan.
5. **甲方名称/买受方名称** and **甲方地址/买受方地址**: fill OA `甲方` with the identified 甲方 or 买受方 name, and use the address to infer 省份.
6. **乙方/合同单位**: usually 北京国华技术有限公司.

If the OA field label is `金额(万元)`, convert yuan to ten-thousand yuan. Example: `38260` yuan -> `3.826000` 万元. Do not enter raw yuan into a 万元 field.

---

## Workflow

### Step 1: Read the contract first

- Use PDF/OCR tools to extract text and tables.
- Prepare a small field checklist before opening OA.
- If a required value is ambiguous, stop and ask before browser entry.

### Step 2: Open OA via Kimi WebBridge

Use a dedicated session (e.g., `"session":"oa-contract"`) to isolate operations.

**Navigate to OA portal** (always use `newTab:true` on first call):

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{
    "action":"navigate",
    "args":{"url":"http://114.116.12.172:8899/wui/index.html#/main/portal/portal-10-15?menuIds=0,10&menuPathIds=0,10&_key=7um3hj","newTab":true},
    "session":"oa-contract"
  }'
```

If a tab titled `合同台账` or `销售合同台账` is already open and it is the sales contract ledger list, reuse it via `find_tab`:

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{
    "action":"find_tab",
    "args":{"url":"114.116.12.172:8899","active":true},
    "session":"oa-contract"
  }'
```

If not logged in, tell the user to log in first and then continue.

### Step 3: Enter the sales contract ledger

- Use `snapshot` to read the page and locate the right-side `销售合同台账` shortcut or the existing `合同台账` tab.
- Click it with `click` using its `@e` ref from snapshot.
- If a modal says the previous page/project will auto-exit, click `确定`.
- On the ledger list page, use `snapshot` again, then `click` the top-right `新建` button.

**进入干净的新建页**：
- 进入新建表单后，确认页面标题是 `合同台账`，且是空白表单。
- 如果页面上已有残留附件、残留字段、弹窗未关闭，**直接退出当前新建页，重新从列表点 `新建`**。

### Step 4: Upload the attachment first

**必须第一步就做，顺序不能变。**

- Use `snapshot` to locate the `上传附件` / `选择文件` control.
- Use `upload` with the exact provided contract file path:

```bash
curl -s -X POST http://127.0.0.1:10086/command \
  -H 'Content-Type: application/json' \
  -d '{
    "action":"upload",
    "args":{"selector":"@eX","files":["/absolute/path/to/contract.pdf"]},
    "session":"oa-contract"
  }'
```

> ⚠️ **Upload rules**:
> - Upload exactly the provided contract file. Do not rename, do not upload other files.
> - Avoid selecting multiple files. Do not use `Ctrl+A` in the file dialog.
> - After upload, use `snapshot` to verify the attached filename and size row appears before filling the rest.
> - **注意**：OA 可能仍显示 `选择文件: 未选择任何文件`，这不代表失败。只要附件列表里出现了正确的文件名和大小，就认为附件已上传成功。
> - If extra files are accidentally attached, **当前表单不能继续用，必须退出重新新建**.

### Step 5: Fill fixed and extracted fields

**前三步完成后，才填写下面这些字段。推荐顺序如下：**

1. **合同年份**：例如 `2026`。
2. **甲方**：选择 PDF 识别出的甲方或买受方，例如 `内蒙古伊品生物科技有限公司`。
3. **乙方**：选择 `北京国华技术有限公司`。
4. **金额(万元)**：例如 `2.483000`。
5. **付款方式**：`开票挂账付全款`。
6. **合同名称**：PDF 文件名。
7. **省份**：例如 `内蒙古`。
8. **文件类型**：`复印件`。
9. **份数**：`2`。
10. **合同说明**：PDF 文件名。

Use `fill` for text inputs and `click` for dropdowns/combos. Always `snapshot` first to get current `@e` refs.

| OA field | Value | How to fill |
|---|---|---|
| 合同类型 | 销售合同 | **必须在附件之后、合同单位之前填写。** Click combo → snapshot list → click `销售合同` row. Do NOT pick `销售采购合同`. |
| 合同年份 | extracted year | `fill` or click combo and select exact year. |
| 合同单位 | 北京国华技术有限公司 | **必须在合同类型之后填写。** Expand combo, select exact item. |
| 甲方 | extracted 甲方 or 买受方 | `fill` with the name. |
| 金额 / 金额(万元) | extracted total, converted if 万元 | `fill` with the numeric value. |
| 付款方式 | 开票挂账付全款 | `fill` or select from combo. |
| 合同名称 | exact attachment filename | `fill` with filename. |
| 省份 | province from 甲方地址 | `fill` or select from combo. |
| 文件类型 | 复印件 | Select from combo. |
| 份数 | 2 | `fill` with "2". |
| 合同说明 | exact attachment filename | `fill` with filename. |

> **甲方和乙方**一般是搜索选择控件，不是普通文本框。打开搜索弹窗后，在搜索框输入公司全称，点击搜索，再双击或点击精确匹配的公司行。

### Step 6: Verify and stop

- Take a screenshot via the helper script for visual verification:

```bash
bash "C:/Users/yesli/.agents/Skills/kimi-webbridge/scripts/screenshot.sh" -s oa-contract
```

- Use `Read` tool to view the screenshot and confirm every required value.
- Tell the user the form is filled and not saved.
- **Only** click 保存 / 保存并新建 if the user explicitly asks to save.

---

## Browser control guidance (Kimi WebBridge)

Always prefer `snapshot` + `@e` refs over raw CSS selectors — `@e` refs survive CSS class hash changes.

- **For combo boxes** (合同单位, 合同年份, 文件类型): `click` to expand, `snapshot` to read options, `click` the exact `@e` row.
- **For 合同类型**: the field may open a search/list popup. Use `snapshot` to read rows, then `click` the `销售合同` row. If the popup has no obvious OK button, clicking the full row may directly return the value.
- **If focus is lost**: use `find_tab` with `active:true` to re-activate the OA tab.
- **Before final verification**: use `snapshot` to ensure all fields are readable.
- **Do not rely on one snapshot** after window changes; re-query with fresh `snapshot`.

---

## 出错恢复规则

### 1. 附件上传错了

**现象**：
- 上传了多个文件。
- 上传了不是本次合同的文件。
- 附件区没有出现正确 PDF。

**处理**：
1. 不要保存。
2. 关闭当前新建页。
3. 回销售合同台账列表。
4. 重新点 `新建`。
5. 从上传附件重新开始。

### 2. 顺序错了

**现象**：
- 先填了金额、名称等，再选合同类型或合同单位。
- 选择合同类型/合同单位后字段被清空。

**处理**：
- **直接放弃当前新建页，重新来。不要补旧表单。**

### 3. 弹窗选项点击不生效

**处理**：
- 先确认弹窗确实在前台。
- 对精确匹配的 `DataItem` 行尝试双击。
- 如果仍不生效，按 `Esc` 关闭弹窗，再重新打开该字段选择。
- 不要用浏览器地址栏执行脚本，容易被 Chrome 当成搜索并离开 OA 页面。

### 4. 浏览器跳走或标签页混乱

**处理**：
- 先找标题为 `销售合同台账` 或 `合同台账` 的标签页。
- 如果没有，就从 OA 门户重新进入。
- 如果当前新建表单状态不确定，直接回列表重新新建。

---

## Known OA quirks

- The right-side portal shortcut may not show `销售合同台账` at first. If a `合同台账` tab is already open, using `find_tab` + `click` is faster.
- The contract type selector may show a modal titled `合同类型`; rows can include `外购合同`, `销售合同`, `销售采购合同`. Choose exactly `销售合同`, not `销售采购合同`.
- The form may visually show a file input text like `选择文件: 未选择文件` even after upload; trust the uploaded attachment row above it if the filename and size are visible.
- Screen scaling does not affect WebBridge `@e` refs, but always verify via screenshot if coordinates were ever used.
- **填表顺序是硬性要求**：附件 → 合同类型 → 合同单位 → 其他字段。任何顺序错误都可能导致字段联动清空。

---

## UI Automation reference (supplementary)

When WebBridge controls are insufficient, the OA form can also be driven via UI Automation. Common control types and patterns:

```text
Button       按钮，例如 新建、上传附件、搜索图标
ComboBox     下拉框，例如 合同单位、合同年份、文件类型
Edit         文本输入框，例如 金额、付款方式、合同名称、省份、份数、合同说明
DataItem     表格单元格或弹窗搜索结果
Hyperlink    已选择的甲方/乙方/附件链接
```

Recommended patterns:
- `新建`、`上传附件`：优先用 `InvokePattern.Invoke()`。
- 下拉框：用 `ExpandCollapsePattern.Expand()` 展开，再选择精确文本的 `MenuItem`。
- 甲方/乙方/合同类型弹窗：搜索后优先双击精确匹配的 `DataItem` 行。
- 文本框：用 `ValuePattern.SetValue()` 写入，避免键盘输入丢字。

### PowerShell/UIA example snippets

**Find and click a button:**
```powershell
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.AndCondition `
  ([System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Button
  )),
  ([System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::NameProperty,
    '新 建'
  ))

$btn = $root.FindFirst([System.Windows.Automation.TreeScope]::Subtree, $cond)
if (-not $btn) { throw '未找到新建按钮' }
$btn.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
```

**Set value on an Edit near coordinates:**
```powershell
function Set-EditNear([int]$x, [int]$y, [string]$value) {
  $root = [System.Windows.Automation.AutomationElement]::RootElement
  $cond = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::Edit
  )
  $els = $root.FindAll([System.Windows.Automation.TreeScope]::Subtree, $cond)
  $best = $null
  $dmin = 99999

  foreach ($e in $els) {
    $r = $e.Current.BoundingRectangle
    if (-not [double]::IsInfinity($r.X) -and $r.Width -gt 100 -and $r.Height -gt 20) {
      $d = [Math]::Abs([int]$r.X - $x) + [Math]::Abs([int]$r.Y - $y)
      if ($d -lt $dmin) {
        $dmin = $d
        $best = $e
      }
    }
  }

  if (-not $best -or $dmin -gt 100) {
    throw "edit near $x,$y not found"
  }

  $best.SetFocus()
  Start-Sleep -Milliseconds 80
  $best.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($value)
}
```

**Select a ComboBox item near coordinates:**
```powershell
function Select-ComboItemNear([int]$x, [int]$y, [string]$name) {
  $root = [System.Windows.Automation.AutomationElement]::RootElement
  $cond = [System.Windows.Automation.PropertyCondition]::new(
    [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
    [System.Windows.Automation.ControlType]::ComboBox
  )
  $els = $root.FindAll([System.Windows.Automation.TreeScope]::Subtree, $cond)
  $combo = $null
  $best = 99999

  foreach ($e in $els) {
    $r = $e.Current.BoundingRectangle
    if (-not [double]::IsInfinity($r.X)) {
      $d = [Math]::Abs([int]$r.X - $x) + [Math]::Abs([int]$r.Y - $y)
      if ($d -lt $best) {
        $best = $d
        $combo = $e
      }
    }
  }

  if (-not $combo -or $best -gt 120) {
    throw "combo near $x,$y not found"
  }

  $combo.SetFocus()
  Start-Sleep -Milliseconds 100
  $combo.GetCurrentPattern([System.Windows.Automation.ExpandCollapsePattern]::Pattern).Expand()
  Start-Sleep -Milliseconds 350

  $itemCond = New-Object System.Windows.Automation.AndCondition `
    ([System.Windows.Automation.PropertyCondition]::new(
      [System.Windows.Automation.AutomationElement]::ControlTypeProperty,
      [System.Windows.Automation.ControlType]::MenuItem
    )),
    ([System.Windows.Automation.PropertyCondition]::new(
      [System.Windows.Automation.AutomationElement]::NameProperty,
      $name
    ))

  $item = $root.FindFirst([System.Windows.Automation.TreeScope]::Subtree, $itemCond)
  if (-not $item) { throw "item $name not found" }

  try {
    $item.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
  } catch {
    $item.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select()
  }
}
```

---

## Final response format

When done, respond concisely in Chinese:

```text
已填好并停在表单页，未点"保存/保存并新建"。

已核对：合同类型、年份、合同单位、甲方、乙方、金额、付款方式、合同名称、省份、文件类型、份数、附件和合同说明。
金额按页面单位填写为：[value]。
```

If something could not be completed, state the exact blocker and the current safe state.
