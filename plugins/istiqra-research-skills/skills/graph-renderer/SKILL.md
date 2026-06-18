---
name: graph-renderer
description: "Utility 层：将实体和共现关系渲染为中文专家/机构/关键词关系图谱 HTML。"
---

# graph-renderer

## Layer Contract

- Layer: `utility`
- Role: independent atomic capability.
- Dependencies: none on workflow or usecase skills.
- Can be called directly for simple user requests or by workflows/usecases.

## Capability

Utility 层：将实体和共现关系渲染为中文专家/机构/关键词关系图谱 HTML。

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

- `scripts/render_graph.py` imports `make_run_dir, read_json, write_json, write_html, print_json`

## Safety And Robustness

- Do not broaden scope into a workflow. This skill should complete one bounded operation.
- Return actionable errors with backend name, query/id/path, and failure reason.
- For read-only database utilities, reject write, delete, DDL, DML, shell escape, or multi-statement hazards.
- For renderers, keep HTML content derived from input data and avoid hard-coded demo values.

## Validation Checklist

- entities.json
- graph.html
- graph.json

## Example Command

```bash
python scripts/render_graph.py --input entities.json
```
