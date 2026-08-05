---
name: oa-travel-expense-entry
description: 从差旅费报销单文件（.docx / .xlsx / 图片）提取行程与费用，通过 kimi-webbridge 自动填写泛微 E-cology OA 的《差旅费报销单》网页表单（workflow/req 创建页，如 workflowid=156）。当用户给出差旅费报销文件和 OA 表单网址要求"填到网页上/OA里/录入报销单"时使用；也适用于"把这个报销单填到 114.116.12.172 这类泛微流程表单"的场景。填写前必须和用户对账（小计、合计、归属不明的费用），提交按钮永远由用户确认后才点。
---

# OA 差旅费报销单自动填表

把差旅费报销文件的数据填进泛微 E-cology 网页表单。三个阶段：**取数 → 对账 → 填表**。

## 第 0 步：加载 kimi-webbridge（最先执行）

**开始任何工作之前，先调用 Skill 工具加载 `kimi-webbridge` 技能**，本 skill 的所有浏览器操作都依赖它。
加载后按其说明做健康检查：

```bash
~/.kimi-webbridge/bin/kimi-webbridge status
```

`running:true` 且 `extension_connected:true` 才能继续；否则按 kimi-webbridge skill 里的
`references/operations.md` 处理，不要自行猜测修复。

## 前置条件

- 用户已给出：① 报销单文件（docx/xlsx/图片）② OA 表单网址
- kimi-webbridge 已加载且健康检查通过（见第 0 步）

## 阶段一：提取报销数据

按文件类型提取**行程明细**（出发时间、车种、车次、起点、到达时间、终点、车船费）
和**其他费用**（补助、市内交通费、旅馆费、其他），以及出差人、部门、出差事由、日期区间：

- **docx**：`python-docx` 遍历 `doc.tables` 的所有行列；金额列常带合并单元格，注意去重
- **xlsx**：openpyxl 读单元格
- **图片**：直接读图识别（手写字迹注意数字校验）

提取后**立刻验算**：各行车船费之和 + 其他费用之和 = 总计。
若用户另给了目标合计（如"结果应该是 6172.89"），反推差额并定位差异在哪一笔——
差额不在文件里时（如退票费、附加费），明确问用户这笔钱的金额和归属，不要猜。

## 阶段二：和用户对账（关键，不要跳过）

填表前向用户确认三件事：

1. **金额对账**：车费小计、其他费用小计、总合计、大写金额
2. **归属不明的费用**：文件里对不上的差额（如退票费 163.38）记到哪一行哪一列
3. **必填但文件里没有的字段**：典型是「财务会计审核」（人员选择），让用户自己选或给姓名

## 阶段三：网页填表

字段映射和页面行为细节见 [references/workflow-156-fields.md](references/workflow-156-fields.md)，
核心流程：

1. **打开页面**：`navigate`（`newTab:true`，设 `group_title`，session 用 `"oa"`），等 ~4s 加载
2. **探测字段**：snapshot 的 @e 引用没有标签，用 evaluate 枚举 `input[id^=field]` 并取相邻 td 文本得到标签映射；
   明细表列有二级表头（标准/金额）易错位，**截图肉眼核对**
3. **填值**：页面有 `window.WfForm` API，一律用
   `WfForm.changeFieldValue("fieldXXXX_i",{value:"..."})` 填；明细行不够用 `WfForm.addDetailRow("detail_1",{})` 加行。
   每填一批用 `WfForm.getFieldValue` 读回验证
4. **截图核对**：全页截图给用户确认

### 三个必踩的坑

- **中文乱码**：Windows Git Bash 下 `curl -d` 提交含中文的 JSON 会损坏字节。
  用本 skill 的 `scripts/webbridge_eval.py` 代替 curl 执行所有含中文的 evaluate：
  `python scripts/webbridge_eval.py oa snippet.js`（ASCII 转义传输）
- **select 下拉**：两次 webbridge 调用之间下拉会自动关闭，「开下拉+点选项」必须在同一次 evaluate 内完成。
  更稳的做法：直接用 `changeFieldValue` 设选项 id（"0","1",…），再用 `getSelectShowName` 验证
- **日期控件是纯日期**：`YYYY-MM-DD HH:mm` 会被拒（字段变空），只能填 `YYYY-MM-DD`，时刻信息进不了表单

### 提交纪律

- 「金额合计」「金额合计大写」是联动字段，自动算，**不要手写**；大写字段读出来是数字但页面显示中文大写，属正常
- 填完后：截图 → 告诉用户金额和空缺项（如财务会计审核）→ **等用户明确说提交再点「提 交」**
- 收尾调用 `close_session` 前确认用户已保存/提交

## 参考数据格式（行程明细行）

```
["2026-06-10","高铁二等座","G98","唐山","2026-06-10","上海虹桥","671.00","163.38(其他列,可选)"]
```
