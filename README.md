# Kimi Code Skills

Kimi Code CLI 自定义技能集合，涵盖合同处理、文档排版、报价单生成等业务场景。

## Skills 列表

| Skill | 说明 |
|-------|------|
| **contract-generator** | 根据买方/卖方信息、产品参数，自动生成标准格式的《工矿机械产品买卖合同》Word 文档 |
| **contract-to-base** | 将合同/采购订单（PDF/图片）自动提取关键信息后录入飞书多维表格，支持查重 |
| **contract-to-delivery-note** | 从合同 PDF/图片 OCR 结果中提取信息，生成标准 Word 发货单 |
| **contract-workflow** | 合同全链路处理工作流：录入多维表格 → 生成报价单 → 生成发货单 → 生成派工单 |
| **quotation-generator** | 生成专业中文报价单（北京国华 / 南通希望两个版本） |
| **production-dispatch-order** | 生成 Excel 格式的生产任务派工单 |
| **chinese-equipment-manual-formatter** | 中文设备说明书排版规范：标题层级、中英文字体、目录、页眉页脚、页码 |

## 使用方式

将对应 skill 目录复制到 `~/.agents/Skills/` 或项目的 `.kimi-code/skills/` 下，Kimi Code CLI 会自动识别。
