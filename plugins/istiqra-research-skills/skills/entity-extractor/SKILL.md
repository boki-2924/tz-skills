---
name: entity-extractor
description: "Utility 层：从 evidence 或文档元数据中抽取作者、机构、期刊、关键词等实体。用于图谱、文献地图和专题综述的实体层数据准备。"
---

# entity-extractor

## Layer Contract

- Layer: `utility`
- Role: independent atomic capability.
- Dependencies: none on workflow or usecase skills.
- Can be called directly for simple user requests or by workflows/usecases.

## Capability

Utility 层：从 evidence 或文档元数据中抽取作者、机构、期刊、关键词等实体。用于图谱、文献地图和专题综述的实体层数据准备。

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

- `scripts/extract_entities.py` imports `make_run_dir, read_json, write_json, split_people, extract_keywords, print_json`

## Safety And Robustness

- Do not broaden scope into a workflow. This skill should complete one bounded operation.
- Return actionable errors with backend name, query/id/path, and failure reason.
- For read-only database utilities, reject write, delete, DDL, DML, shell escape, or multi-statement hazards.
- For renderers, keep HTML content derived from input data and avoid hard-coded demo values.

## Validation Checklist

- evidence.json
- entities.json

## Example Command

```bash
python scripts/extract_entities.py --input evidence.json
```
