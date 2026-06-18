---
name: minio-object-get
description: "Utility 层：安全读取 tongzhan MinIO bucket 中对象状态或内容预览。用于根据 markdownUrl、pdfUrl、md_path_in_minio、pdf_path_in_minio 获取对象可达性、大小、预览文本或下载结果。"
---

# minio-object-get

## Layer Contract

- Layer: `utility`
- Role: independent atomic capability.
- Dependencies: none on workflow or usecase skills.
- Can be called directly for simple user requests or by workflows/usecases.

## Capability

Utility 层：安全读取 tongzhan MinIO bucket 中对象状态或内容预览。用于根据 markdownUrl、pdfUrl、md_path_in_minio、pdf_path_in_minio 获取对象可达性、大小、预览文本或下载结果。

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

- `scripts/get_object.py` imports `none`

## Safety And Robustness

- Do not broaden scope into a workflow. This skill should complete one bounded operation.
- Return actionable errors with backend name, query/id/path, and failure reason.
- For read-only database utilities, reject write, delete, DDL, DML, shell escape, or multi-statement hazards.
- For renderers, keep HTML content derived from input data and avoid hard-coded demo values.

## Validation Checklist

- documents/.../file.md
- raw/.../file.pdf
- file.pdf

## Example Command

```bash
python scripts/get_object.py --key "documents/.../file.md" --preview-bytes 800
```
