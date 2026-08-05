---
name: contract-to-base
description: |
  将合同或采购订单附件（PDF/图片）自动提取关键信息后录入飞书多维表格（Base）。支持查重功能：若附件中的合同号或订单号在多维表格中已存在，则跳过录入并返回查重结果。
  触发词："录入合同到多维表格"、"合同录入base"、"上传合同到台账"、"订单录入多维表格"。
---

# 合同/订单录入多维表格（Contract to Base）

## 目标

将用户提供的合同或采购订单附件（PDF、JPG 等）提取关键字段后，录入指定的飞书多维表格。录入前必须先执行查重，避免重复录入。

## 默认信息补全规则

当从附件或用户指令中**未能提取到某字段**时，按以下默认值补全，避免录入失败：

| 字段 | 默认值 |
|------|--------|
| 合同号/订单号 | 执行 skill 当日的日期，格式 `YYYY-MM-DD` |
| 甲方/买受人/采购方 | `某某公司` |
| 乙方/出卖人/销售方 | `南通厚普机械科技有限公司` |
| 签订日期/订单日期 | 执行 skill 当日的日期，格式 `YYYY-MM-DD` |
| 含税金额总计 | `0` |
| 产品清单/合同内容摘要 | `货物` |
| 备注 | 空字符串（不填） |

> **规则**：提取到的真实信息**优先于默认值**；仅当信息确实缺失时才使用默认值。日期以执行 skill 当天的实际日期为准，动态生成。

## 前置条件

1. **lark-cli 已配置并登录**：`lark-cli auth login`
2. **Base 访问权限**：调用者必须是目标多维表格的管理员
3. **文件可读**：附件必须在当前工作目录内，或先复制到当前工作目录

## Base 配置

执行本 skill 时，按以下优先级确定目标多维表格：

1. **用户本次提供的 Base 链接/URL（最高优先级）**：从链接中解析 `base_token`、`table_id`、`view_id` 并直接使用。
2. **本地默认配置文件**：若用户未提供链接，则读取项目根目录下的配置文件：

   ```text
   D:/DaliyWork/contract_base_config.json
   ```

   文件格式：

   ```json
   {
     "base_token": "AmuqbgOCkax4TtsTEfrchb5EnPc",
     "table_id": "tblVuMC2ginVS9nA",
     "view_id": "vew5AfTRIX"
   }
   ```

3. **询问用户**：若以上都没有，向用户索取 Base 链接或 token；完成后自动将配置写入上述文件，供下次复用。

## 核心流程

### Step 0: 读取 Base 配置

先检查用户是否提供了 Base 链接。若提供，解析出 `base_token` 和 `table_id`；若未提供，再检查 `D:/DaliyWork/contract_base_config.json` 是否存在并解析；若仍不存在，进入 Step 1 前先向用户索取并保存。

### Step 1: 提取附件信息

对每一个附件文件，使用 PDF/OCR 工具提取以下字段：

| 字段 | 说明 |
|------|------|
| 合同号/订单号 | 原始合同编号或采购订单编号，如 `SST-2026-06-003`、`6300179733` |
| 甲方/买受人/采购方 | 合同中的买方名称 |
| 乙方/出卖人/销售方 | 合同中的卖方名称 |
| 签订日期/订单日期 | 合同生效日期 |
| 含税金额总计 | 合同总金额（数字） |
| 产品清单 | 合同中物料/产品的名称、型号、数量、单价、总价 |

> **注意**：不同合同格式可能使用不同关键词，如"合同编号"、"订单编号"、"甲方"、"买受人"、"采购方"、"出卖人"、"乙方"、"销售方"等，提取时应兼容这些变体。
> 
> **默认值**：若某字段提取失败或用户未提供，按[默认信息补全规则](#默认信息补全规则)填写。

### Step 2: 查重逻辑（必须执行）

使用 `原始合同编号` 字段进行**精确查重**。

#### 查重命令

```bash
lark-cli base +data-query \
  --base-token <base_token> \
  --dsl '{
    "datasource": {"type": "table", "table": {"tableId": "<table_id>"}},
    "dimensions": [
      {"field_name": "合同编号", "alias": "hp_id"},
      {"field_name": "原始合同编号", "alias": "contract_no"},
      {"field_name": "采购方", "alias": "buyer"},
      {"field_name": "合同金额", "alias": "amount"}
    ],
    "measures": [{"field_name": "合同编号", "aggregation": "count", "alias": "cnt"}],
    "filters": {
      "type": 1,
      "conjunction": "and",
      "conditions": [
        {"field_name": "原始合同编号", "operator": "is", "value": ["<提取的合同号/订单号>"]}
      ]
    },
    "shaper": {"format": "flat"}
  }'
```

#### 查重结果判定

- **`main_data` 非空** → 该合同号/订单号已存在，标记为**重复**，**不录入**，返回已有记录的 `合同编号`
- **`main_data` 为空** → 该合同号/订单号不存在，标记为**新记录**，继续执行 Step 3

> **兜底策略**：若 `原始合同编号` 字段因特殊原因无法使用（如字段被删除），可退回到组合查重：`采购方 == 甲方名称 AND 合同金额 == 含税金额 AND 生效日期 == 签订日期`。

### Step 3: 创建记录

对通过查重的文件，使用 `lark-cli base +record-upsert` 创建记录。

**录入字段**（根据实际 Base 字段结构调整，未提取到则使用默认值）：

```json
{
  "采购方": "<甲方/买受人/采购方名称，默认：某某公司>",
  "销售方": "<乙方/出卖人/销售方名称，默认：南通厚普机械科技有限公司>",
  "合同金额": <含税金额数字，默认：0>,
  "生效日期": "<YYYY-MM-DD HH:mm:ss，默认：执行当日>",
  "原始合同编号": "<合同号/订单号，默认：执行当日日期>",
  "合同内容摘要": "<产品清单 markdown 表格，默认：货物>",
  "备注": "<补充说明，默认空>"
}
```

> **规则**：
> - 数字字段直接传数字，不要传字符串
> - 日期字段使用 `"YYYY-MM-DD HH:mm:ss"` 格式
> - `原始合同编号` 必须填写，这是后续查重的唯一标识
> - 不要写入 `auto_number`、`formula`、`lookup`、`created_time`、`modified_time`、`created_by`、`modified_by` 等只读字段

### Step 4: 上传附件

记录创建成功后，使用 `lark-cli base +record-upload-attachment` 上传附件：

```bash
lark-cli base +record-upload-attachment \
  --base-token <base_token> \
  --table-id <table_id> \
  --record-id <上一步返回的 record_id> \
  --field-id <附件字段ID> \
  --file "./<文件名>"
```

> **重要**：`--file` 必须是当前工作目录下的相对路径。如果文件在其他位置，先 `cp` 文件到当前目录。

## 返回结果格式

处理完成后，必须向用户返回结构化的查重与录入结果：

```text
合同/订单录入结果汇总：

1. 文件名：xxx.pdf
   合同号/订单号：XXX-2026-06-001
   查重结果：❌ 已存在（记录编号：HP20260528302）
   录入状态：已跳过

2. 文件名：yyy.pdf
   合同号/订单号：YYY-2026-06-002
   查重结果：✅ 未找到重复
   录入状态：已录入（记录编号：HP2026XXXXXX）

共处理 N 个文件，成功录入 M 条，跳过 K 条重复。
```

## 字段映射参考（目标 Base）

| 提取字段 | Base 字段名 | 字段ID | 类型 | 是否必填 |
|---------|------------|--------|------|---------|
| 附件文件 | 合同上传 | fldU1ZUWwr | attachment | 是 |
| 甲方/采购方 | 采购方 | fldKr7HNJk | text | 是 |
| 乙方/销售方 | 销售方 | fldHXzMgFz | text | 是 |
| 含税金额 | 合同金额 | fldLDigC5w | number | 是 |
| 签订日期 | 生效日期 | fldfmxd8Iy | datetime | 是 |
| 合同号/订单号 | 原始合同编号 | fldhv5Nobm | text | **是** |
| 产品清单 | 合同内容摘要 | fldOurzZhA | text | 否 |
| 补充说明 | 备注 | fldc1tnQEY | text | 否 |

## 建字段命令（参考）

若 `原始合同编号` 字段缺失，按以下命令创建：

```bash
lark-cli base +field-create \
  --base-token <base_token> \
  --table-id <table_id> \
  --json '{"type":"text","name":"原始合同编号","style":{"type":"plain"}}'
```

## 常见错误处理

| 错误 | 原因 | 解决 |
|------|------|------|
| `unsafe file path` | `--file` 使用了绝对路径 | 先 `cp` 文件到当前目录，再用相对路径 |
| `param baseToken is invalid` | 误把 wiki token 当 base token | 若 URL 是 `/wiki/...`，先调用 `lark-cli wiki spaces get_node` 获取 `obj_token` |
| `1254045` 字段名不存在 | 字段名拼写错误 | 先用 `+field-list` 确认真实字段名 |
| `1254015` 字段值类型不匹配 | 数字字段传了字符串 | 确保 `合同金额` 传数字而非字符串 |
| 并发写冲突 | 批量写入太快 | 串行写入，批次间延迟 0.5-1 秒 |
