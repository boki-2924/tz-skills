---
name: citation-preview-renderer
description: "Utility 层：为检索证据生成 PDF 页面 PNG 与 bbox 高亮 HTML 预览。用于引用预览和证据核验。"
---

# citation-preview-renderer

## Layer Contract

- Layer: `utility`
- Role: independent atomic capability.
- Dependencies: none on workflow or usecase skills.
- Can be called directly for simple user requests or by workflows/usecases.

## Capability

Utility 层：为检索证据生成 PDF 页面 PNG 与 bbox 高亮 HTML 预览。用于引用预览和证据核验。

## Operating Procedure

1. Validate input arguments and refuse unsafe or out-of-scope operations.
2. Execute only the atomic operation described by this skill.
3. Return structured JSON, HTML, text preview, or status data that upstream workflows can consume.
4. Preserve raw identifiers, paths, SQL, object keys, or input filenames for traceability.

## Inputs

- Use the script help or SKILL description to choose required parameters.
- Prefer explicit ids and paths (`document_id`, `chunk_id`, object key, SQL, input JSON) over fuzzy matching.
- For renderer utilities, accept input JSON files and output directories rather than embedding fixed content.

## Scripts

- `scripts/render_citation_preview.py` imports `make_run_dir, render_citation_preview, print_json`

## Safety And Robustness

- Do not broaden scope into a workflow. This skill should complete one bounded operation.
- Return actionable errors with backend name, query/id/path, and failure reason.
- For read-only database utilities, reject write, delete, DDL, DML, shell escape, or multi-statement hazards.
- For renderers, keep HTML content derived from input data and avoid hard-coded demo values.

## Validation Checklist

- previews/E01.html
- previews/preview.html

## Example Command

```bash
python scripts/render_citation_preview.py "丝绸之路经济带" --top-k 2
```
