---
name: contract-from-reconciliation
description: 根据手写对账单整理后的 Excel 对账表，自动生成格式统一的《工矿机械产品买卖合同》Word 文档。支持自动识别配件小计、运杂费/管理费/税费并合并为其他加工费，生成前须经用户确认金额。
---

# 从对账表生成买卖合同

## 触发条件

当用户提出以下任一需求时调用本 Skill：
- “根据对账表生成合同”
- “从 Excel 对账单生成买卖合同”
- “把对账表转成合同”
- 任何意图将手写对账单/Excel 对账表转换为《工矿机械产品买卖合同》的请求

## 输入要求

执行前必须向用户收集或确认以下两项：
1. **Excel 对账表路径**（.xlsx）：由 `handwritten-reconciliation` Skill 生成或同格式文件，至少包含配件明细、运费/管理费/税费、合计等字段。
2. **Word 合同模板路径**（.doc 或 .docx）：标准《工矿机械产品买卖合同》模板，包含主标的表、买卖双方信息、合同条款、附件明细表。

若用户未指定模板，默认使用最近一次使用过的合同模板；若不存在，则询问用户模板路径。

## 执行流程

### 第一步：读取 Excel 对账表

使用 `openpyxl` 读取 Excel，解析每个工作表（通常按月份拆分），提取以下数据：
- 月份标识（如 5月、6月）
- 配件明细：序号、日期、物品名称和规格、数量、单位、单价、总价、备注
- 配件小计
- 其他加工费（若 Excel 中已存在该字段）
- 运杂费、管理费、税费（若 Excel 中分别列出）
- 当月总计

### 第二步：计算其他加工费

- 如果 Excel 中已经存在“其他加工费”字段，直接使用该值。
- 如果 Excel 中没有“其他加工费”字段，则默认将 **运费 + 管理费 + 税费** 之和作为其他加工费。
- 计算完成后，向用户展示计算明细，例如：

```
5月：配件小计 23,165.00 + 其他加工费 2,829.00（运费 2,382 + 管理费 190 + 税费 257）= 25,994.00
6月：配件小计 25,504.00 + 其他加工费 3,148.00（运费 2,650 + 管理费 212 + 税费 286）= 28,652.00
主标总价：25,994.00 + 28,652.00 = 54,646.00
```

**必须等待用户回复“确认”或金额无误后，再继续执行。** 若用户提出修改，先按用户要求调整金额。

### 第三步：准备合同数据

确认金额后，整理生成合同所需数据：
- 标题月份：根据对账表月份自动改为“X年X-X月配”
- 合同编号：`ZKHP` + 当前系统日期（YYYYMMDD），如 `ZKHP20260711`
- 签订时间：当前系统日期
- 主标总价：各月“当月总计”之和（含配件 + 其他加工费）
- 大写金额：将主标总价转换为中文大写，如“伍万肆仟陆佰肆拾陆元整”
- 附件明细表：按月份拆分为多个子表，每个子表包含配件明细、合计、其他加工费、总计

### 第四步：生成 Word 合同

1. 用 `pywin32` 或 `pypandoc` 将 `.doc` 模板转换为 `.docx`（若模板为旧格式）。
2. 用 `python-docx` 打开 `.docx` 模板。
3. 替换以下占位/原内容：
   - 标题中的月份，**标题字号统一为三号字（16pt）**
   - 出卖方段落中的合同编号
   - 签订时间
   - 主标的表中的名称、数量、单价、总价
   - 主标的表金额行：左侧第一个单元格写“人民币”，其余单元格写大小写金额
   - 附件明细表：清空后重新填入新的月份明细表，每个子表包含表头、数据行、合计、其他加工费、总计
4. **注意：** 用 `paragraph.text = ...` 重新赋值会清除该段落原有字体格式。因此，修改完“出卖方/合同编号”和“买受方/签订地点”段落后，必须重新对段落内所有 run 应用统一的字号、字体、加粗。
5. **附件明细表必须为每个单元格设置上下左右四边边框。**
6. **统一买卖双方信息表（Table 1）的字号、字体和加粗格式**，确保出卖方与买受方视觉一致。即使模板原格式存在差异，也应在保存前强制统一。

### 第五步：最终检查

保存合同后，必须重新读取生成的 Word 文件，确认以下项目：
- [ ] 标题月份正确，标题字号为三号字（16pt）
- [ ] 合同编号格式为 `ZKHPYYYYMMDD`
- [ ] 签订时间为当前日期
- [ ] 主标总价 = 各月总计之和
- [ ] 金额行左侧单元格为“人民币”
- [ ] 附件表列顺序正确：序号 / 日期 / 项目名称/物品 / 数量/规格 / 单价 / 总价 / 备注
- [ ] 附件表每个单元格均有四边边框
- [ ] 数据行无列错位
- [ ] 买卖双方信息表（出卖方/买受方）字号、字体、加粗一致
- [ ] “出卖方/合同编号”与“买受方/签订地点”两行段落字号、字体、加粗一致

### 第六步：交付

1. 将生成的合同保存到项目目录。
2. 按 `desktop-copy` Skill 规则，复制一份到桌面：`C:\Users\yesli\OneDrive\桌面\`
3. 向用户报告：主文件路径、桌面副本路径、主标总价、其他加工费明细、检查结论。

## 关键代码参考

### 设置单元格四边边框

```python
from docx.oxml.ns import qn
from docx.oxml import parse_xml

def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in('w:tcBorders')
    if tcBorders is None:
        tcBorders = parse_xml(r'<w:tcBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
        tcPr.append(tcBorders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = tcBorders.find(qn(tag))
            if element is None:
                element = parse_xml(r'<w:%s xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>' % edge)
                tcBorders.append(element)
            for key in ["sz", "val", "color", "space"]:
                if key in edge_data:
                    element.set(qn('w:{}'.format(key)), str(edge_data[key]))

def apply_all_borders(cell):
    set_cell_border(cell,
        top={"sz": 4, "val": "single", "color": "000000", "space": "0"},
        bottom={"sz": 4, "val": "single", "color": "000000", "space": "0"},
        left={"sz": 4, "val": "single", "color": "000000", "space": "0"},
        right={"sz": 4, "val": "single", "color": "000000", "space": "0"},
    )
```

### 统一买卖双方信息表字体格式

```python
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import parse_xml

def unify_cell_font(cell, font_name='宋体', font_size=Pt(10.5), bold=True):
    """统一单元格内所有 run 的字体、字号、加粗。默认五号字 10.5pt。"""
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
            run.font.size = font_size
            run.font.bold = bold
            # 同时设置 w:sz 和 w:szCs，确保 Word 显示一致（五号字 = 10.5pt = 21 半点）
            rPr = run._r.get_or_add_rPr()
            for tag in ['w:sz', 'w:szCs']:
                sz = rPr.find(qn(tag))
                if sz is None:
                    sz = parse_xml(r'<w:%s xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>' % tag.split(':')[1])
                    rPr.append(sz)
                sz.set(qn('w:val'), str(int(font_size / 12700 * 2)))

for row in doc.tables[1].rows:
    for cell in row.cells:
        unify_cell_font(cell)
```

### 数字转中文大写

```python
def num_to_chinese(num):
    num = int(round(num))
    units = ['', '拾', '佰', '仟']
    nums = '零壹贰叁肆伍陆柒捌玖'
    unit_big = ['', '万', '亿', '万亿']
    s = str(num)
    result = ''
    zero_flag = False
    group_count = 0
    while s:
        group = s[-4:]
        s = s[:-4]
        group_str = ''
        for i, ch in enumerate(reversed(group)):
            n = int(ch)
            if n == 0:
                if not zero_flag and group_str:
                    zero_flag = True
            else:
                if zero_flag:
                    group_str = '零' + group_str
                    zero_flag = False
                group_str = nums[n] + units[i] + group_str
        if group_str:
            group_str += unit_big[group_count]
        result = group_str + result
        group_count += 1
    result = result.replace('零零', '零').replace('零万', '万').replace('零亿', '亿')
    if result.startswith('零'):
        result = result[1:]
    if not result:
        result = '零'
    return result + '元整'
```

## 注意事项

- 生成合同前**必须**经用户确认金额，不得自动跳过确认步骤。
- 若 Excel 中“其他加工费”字段已存在，优先使用 Excel 中的值，不再重新计算运费+管理费+税费。
- 主标总价应包含配件合计和其他加工费，即各月“当月总计”之和。
- 合同编号必须使用当前系统日期，格式严格为 `ZKHPYYYYMMDD`。
- 生成的 Word 合同除标题、合同编号、签订时间、价格、附件明细表外，不得修改模板中的其他内容（买卖双方信息、合同条款等）。
- 交付时必须同时生成项目目录文件和桌面副本。
