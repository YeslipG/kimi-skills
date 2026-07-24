---
name: purchase-order-to-supplier-contract
description: 根据采购订单/销售合同（PDF 或图片）和 Word 模板，自动生成供应商侧的《工矿机械产品买卖合同》Word 文档。支持多行物料、图片 OCR 提取、销售合同号自动替换。当用户要求“把采购订单/销售合同做成采购合同”“按订单和模板生成合同”“采购订单转供应商合同”“根据 PDF/图片订单套用模板做合同”或类似任务时触发。
---

# 采购订单/销售合同 → 供应商采购合同 Skill

## 功能说明
读取采购订单或销售合同（PDF 或图片），套用现有 Word 合同模板，自动生成供应商采购合同 Word 文档，并同步保存到桌面。

## 触发条件
- “按这个采购订单/销售合同和模板做合同”
- “把订单 PDF/图片转成合同”
- “用模板套采购订单生成合同”
- “采购订单/销售合同生成供应商合同”
- 用户提供：`文件1.pdf/.jpg` + `模板.doc/.docx`

## 输入参数

| 参数 | 说明 |
|------|------|
| `file1` | 采购订单/销售合同 PDF 或图片路径 |
| `template` | Word 合同模板路径（`.doc` 或 `.docx`） |
| `--output-dir` / `-o` | 可选，输出目录，默认当前目录 |
| `--discount` / `-d` | 可选，折扣系数，默认 `0.8` |
| `--buyer` | 可选，手动指定买方全称（OCR 识别不准时使用） |
| `--seller` | 可选，手动指定卖方全称 |
| `--order-date` | 可选，手动指定签订/订单日期 `YYYY-MM-DD` |
| `--items-json` | 可选，手动指定物料 JSON 列表（覆盖自动提取） |

`--items-json` 示例：

```json
[
  {"product":"头轮总成","model":"THY01-0506","unit":"套","quantity":"1","unit_price":9950,"total_price":9950},
  {"product":"尾轮总成","model":"THY02-0102","unit":"套","quantity":"1","unit_price":3750,"total_price":3750},
  {"product":"涨紧轮总成","model":"THY04-0506","unit":"套","quantity":"1","unit_price":4000,"total_price":4000}
]
```

## 核心规则

1. **签订时间** = 文件1签订/订单日期 + 5 天
2. **交（提）货时间** = 文件1签订/订单日期 + 60 天
3. **单价、总价** = 文件1金额 × 折扣（默认 0.8），每行物料分别打折
4. **合同编号** = `HPGH` + 签订日期(yy/mm/dd)简写 + `-1`
5. **销售合同号**：从文件1文件名末尾提取 `BGJ` 开头、数字结尾的合同号，替换模板结算条款中的对应内容；提取不到则替换为 **补充销售合同号**
6. **多行物料**：自动在产品表格中插入/删除行，保持一页 A4 完整显示
7. **文件名** = `当日日期(YYMMDD)-hpgh-买方全称-折后总价.doc`
9. **交付规则**：生成的文件原路径保存一份，桌面（`C:/Users/yesli/OneDrive/桌面`）保存同名副本

## 使用方式

### 方式1：自动提取（推荐 PDF）

```bash
python <skill-path>/scripts/generate_contract.py \
  "采购订单.pdf" \
  "合同模板.doc" \
  -o "D:/Kimi/output"
```

### 方式2：图片 + 手动指定物料（OCR 复杂表格时）

```bash
python <skill-path>/scripts/generate_contract.py \
  "销售合同.jpg" \
  "合同模板.doc" \
  -o "D:/Kimi/output" \
  --buyer "内蒙古巴山淀粉有限公司" \
  --order-date "2026-03-05" \
  --items-json '[{"product":"头轮总成","model":"THY01-0506","unit":"套","quantity":"1","unit_price":9950,"total_price":9950}]'
```

## 依赖

- Python 3.10+
- `pdfplumber`（PDF 表格提取）
- `python-docx`
- `pywin32` + Microsoft Word（用于 `.doc` 读写）
- `easyocr`（图片 OCR，可选；提供 `--items-json` 时可不依赖）

## 注意事项

- 脚本依赖 Windows + Word COM 来读写 `.doc` 格式。
- 图片 OCR 对复杂/扫描件表格识别可能不完整，遇到识别不准时建议用 `--buyer`、`--order-date`、`--items-json` 手动覆盖关键字段。
- 若文件1文件名不含 `BGJ...` 销售合同号，结算条款会显示“补充销售合同号”，请用户在 Word 中补充实际编号。
