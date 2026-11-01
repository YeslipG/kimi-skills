# 泛微 E-cology 差旅费报销单（workflowid=156）字段映射

适用于 `http://114.116.12.172:8899/spa/workflow/static4form/...workflowid=156...` 创建页。
不同环境/表单版本字段 id 可能变化——先按「通用字段探测」一节核对，再套用本表。
（下列字段 id 于 2026-09-01 实测验证通过）

## 主表字段

| 字段 id | 标签 | 类型 | 说明 |
|---|---|---|---|
| `requestname` | 标题 | text | 自动带出「差旅费报销单-姓名-日期」 |
| `field6416` | 发起部门 | browse | 创建人部门，自动带出 |
| `field6417` | 发起日期 | date | 自动带出当天 |
| `field6418` | 出差人姓名 | browse | 自动带出创建人 |
| `field8769` | 公司名称 | select | 必填。选项 id 为 "0"~"6"，见下表 |
| `field7731` | 项目名称 | browse | 可空 |
| `field7871` | 财务会计审核 | browse（人员） | **必填，必须用户指定人选** |
| `field6423` | 出差事由 | textarea | |
| `field6424` | 备注 | textarea | |
| `field6553` | 金额合计 | 数值 | 明细小计联动自动算，不要手写 |
| `field6554` | 金额合计大写 | 只读联动 | getFieldValue 读到的是数字，但页面显示自动转中文大写；不要 changeFieldValue 写它（会把值清空，需 `WfForm.triggerFieldBindEvent("field6553")` 恢复） |
| `field8636` | 附件上传 | 附件 | |

公司名称选项（实测）：0=唐山国华科技有限公司，**1=唐山国华科技国际工程有限公司**，
2=北京国华科技集团有限公司，3=北京国华技术有限公司，4=唐山国华科技洁净煤技术有限公司，
5=唐山国华科技矿山装备有限公司，6=唐山班班机械制造有限公司。
用 `WfForm.getSelectShowName("field8769")` 验证选中项。

## 明细表字段（行后缀 `_0`, `_1`, …）

加行：`WfForm.addDetailRow("detail_1", {})`，每次加一行，间隔 ~400ms。

| 字段 id | 列 | 说明 |
|---|---|---|
| `field6464_i` | 出发时间 | **纯日期控件**，只接受 `YYYY-MM-DD`，带时分秒会被拒（值变空） |
| `field6425_i` | 车种 | 如「高铁二等座」「汽车」「出租车」 |
| `field6426_i` | 车次 | 如「G98」，汽车/出租车可空 |
| `field6427_i` | 起点 | |
| `field6428_i` | 到达时间 | 纯日期，同上 |
| `field6429_i` | 终点 | |
| `field6430_i` | 车船费 | 金额，字符串如 "671.00" |
| `field6431_i` / `field6432_i` | 开车补助 标准/金额 | |
| `field6433_i` / `field6434_i` | 途中补助 标准/金额 | |
| `field6435_i` / `field6436_i` | 住宿补助 标准/金额 | |
| `field9316_i` | 市内交通费 | 注意 id 跳号，不是 6437 |
| `field6438_i` | 旅馆费 | |
| `field6439_i` | 其他 | 退票费、杂费等 |
| `field6440_i` | 小计 | 自动联动，无需填写 |

## 通用字段探测（遇到陌生表单/字段 id 对不上时）

1. `snapshot` 拿到的 @e 引用没有字段标签，直接用 JS：
   - 列出可见输入框：`document.querySelectorAll("input,textarea,select")`，过滤 `getBoundingClientRect().width>0`
   - 找字段标签：对每个 `input[id^=field]`，取 `el.closest("td").previousElementSibling.innerText`
2. 明细表列头：取某字段 `closest("table")`，读表头行 `innerText`，注意二级表头（标准/金额）会导致列错位，
   **以截图肉眼核对为准**。
3. 截图确认整体布局后再动手填。

## 页面行为要点（实测）

- 页面暴露 `window.WfForm` API（E9 SPA）：`changeFieldValue(fieldMark,{value})`、`getFieldValue`、
  `getSelectShowName`、`addDetailRow`、`triggerFieldBindEvent`。**一律用 WfForm API 写字段**，
  直接改 DOM value 不进 React 状态，提交会丢。
- select 字段：选项 id 是字符串序号（"0","1",…），可用 changeFieldValue 直接设，设完用 getSelectShowName 验证。
- 下拉菜单在两次 webbridge 调用之间会自动关闭，「开下拉+点选项」必须放在同一次 evaluate 里——
  所以优先用 changeFieldValue 绕过下拉。
- 金额联动：填完明细金额后小计/合计自动算；若无反应，对该金额字段 `triggerFieldBindEvent`。
- 页面提交按钮「提 交」在 snapshot 顶部；**永远先让用户确认再点**。
