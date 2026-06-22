---
name: chinese-equipment-manual-formatter
description: Standardize and typeset Chinese equipment manuals in Word (.doc/.docx), including heading hierarchy and numbering, Chinese/Western fonts, tables, automatic TOC, section-based headers and page numbering, and final visual QA. Use this skill whenever the user asks to 排版、规范格式、统一说明书格式、插入目录、设置页眉页脚、正文重新从第1页计页、制作“第X页/共Y页”，or says “其他要求和前面一样” for a Chinese machinery/equipment manual. Prefer this skill even when the request only mentions part of the workflow, because those changes can affect sections, TOC, pagination, and layout together.
compatibility: Requires a toolchain capable of editing Word documents and updating Word fields; Microsoft Word automation is preferred on Windows. A DOCX renderer or PDF export is required for final visual verification.
---

# Chinese Equipment Manual Formatter

Apply the user's established Chinese equipment-manual standard to an existing Word document and deliver a verified `.docx` copy. Treat the source content as controlled material: change presentation and numbering only, not technical meaning.

## Required reading

Before editing, read [references/format-standard.md](references/format-standard.md). Use it as the source of truth for typography, numbering, tables, headers, footers, and output naming.

Before delivery, read and execute [references/verification-checklist.md](references/verification-checklist.md). Do not claim completion from XML inspection alone; pagination and field results must also be visually verified.

## Inputs and defaults

Accept one `.doc` or `.docx` manual. If the user provides several files, process only the explicitly named current file unless batch processing is requested.

Use these defaults unless the user overrides them:

- Preserve all wording, pictures, tables, formulas, captions, and document order.
- Do not overwrite the source file.
- Name the output `[原文件名]_按规则排版.docx`.
- Use the full cover title in the body header, excluding company name, date, version, and other cover metadata.
- Keep the cover and TOC without visible header or page number.
- Restart body page numbering at 1 and display `第X页/共Y页`, where `Y` counts body pages only.

If title boundaries or the cover/TOC boundary are genuinely ambiguous, inspect the document structure and rendering first. Ask only when two plausible choices would materially change the result.

## Workflow

### 1. Preserve and inventory the source

1. Work on a copy.
2. Convert legacy `.doc` to `.docx` with Word-compatible conversion before other edits.
3. Record baseline facts: section count, page count, paragraphs, tables, images/media, TOC fields, headers/footers, tracked changes, and existing page-number settings.
4. Identify the cover, the TOC, the first body paragraph, and the full main title.
5. Preserve existing user content and media. Do not accept a result that loses images, tables, or substantive text.

### 2. Determine structure conservatively

Infer heading levels using several signals together: existing styles, TOC entries, numbering pattern, font/size/bold treatment, paragraph spacing, semantic position, and nearby headings.

Avoid false positives. Equipment models, patent numbers, dates, technical parameters, quantities, and numbered claims are not headings merely because they begin with digits.

When a heading and body text were accidentally combined in one paragraph, split only at an evident boundary and preserve the body text exactly.

### 3. Apply numbering and styles

Apply the hierarchy in the format standard:

- Level 1: `一、二、三、…`
- Level 2: `1. 2. 3.`
- Level 3: `1.1 1.2 2.1`
- Level 4: `1.1.1 1.1.2`
- Lists/steps: `1) 2) 3)`

Renumber in document order and keep the TOC synchronized. Preserve patent-claim numbering and other legally meaningful internal numbering unless the user explicitly asks to change it.

Apply fonts through both style definitions and direct formatting where necessary, because imported Word files often contain local overrides. Set East Asian and Western font properties separately.

### 4. Format tables

Apply the standard to every true data table while preserving merged cells, column structure, borders, and content. Set cell margins at the table XML/property level when the high-level API cannot express the exact value.

Do not turn layout-only containers into styled data tables unless they are visibly intended as tables.

### 5. Rebuild or update the TOC

Use an automatic TOC covering heading levels 1–3. Update the entire TOC after heading edits, not page numbers only.

Remove only redundant empty paragraphs between the TOC and the preserved section break. Never remove the section break itself. Confirm that the TOC does not create an unintended blank page.

### 6. Configure sections, header, and footer

Create or retain a section boundary immediately after the TOC.

For the front-matter section:

- Remove visible headers and footers.
- Do not display page numbers.

For the body section:

- Unlink header and footer from the previous section.
- Restart page numbering at 1.
- Add a left-aligned header containing a short black vertical decorative line followed by the complete main title.
- Exclude the company name and other cover metadata from the header.
- Center the footer and construct it with live fields as `第{ PAGE }页/共{ SECTIONPAGES }页`.
- Use `SECTIONPAGES`, not `NUMPAGES`, so the total excludes cover and TOC pages.

If the document uses different first-page or odd/even headers, normalize those variants so the requested result is consistent on every body page and still absent from front matter.

### 7. Update fields and stabilize layout

Update the TOC, all fields, headers, and footers. Repaginate the document, save, reopen, update again if needed, and save once more. Word pagination can change after TOC expansion, so field refresh and repagination are part of the same loop.

Do not close or terminate a Word instance that existed before this task. Close only the document/application instance created for the edit.

### 8. Verify and deliver

Run the complete verification checklist. At minimum, inspect the rendered cover, TOC, first body page, representative middle pages, table/image pages, and last page.

Confirm that:

- Cover and TOC have no visible header or footer page number.
- First body footer is `第1页/共Y页`.
- Last body footer is `第Y页/共Y页`.
- Header title is complete, excludes the company, and has the vertical line.
- TOC entries and page numbers match the final body.
- No extra blank page, clipped table, shifted image, orphan heading, or damaged content remains.

Deliver only after the final copy opens without a repair warning and matches the verified working file.

## Completion report

Keep the user-facing report concise. State:

- Output file link/path.
- Body page range and total.
- Header title used.
- Whether the TOC and all fields were updated.
- Whether representative pages and the final page were visually checked.

Do not expose temporary conversion files or implementation scripts unless the user asks.
