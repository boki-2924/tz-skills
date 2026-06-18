---
name: doris-sql-readonly
description: "Utility 层：通过 Datonos Doris/Iceberg execute 接口执行安全只读 SQL。用于 SELECT、SHOW、DESC、DESCRIBE、EXPLAIN 等查询；必须拒绝 DDL、DML、删除、写入和危险语句。"
---

# doris-sql-readonly

## Layer Contract

- Layer: `utility`
- Role: independent atomic capability.
- Dependencies: none on workflow or usecase skills.
- Can be called directly for simple user requests or by workflows/usecases.

## Capability

Utility 层：通过 Datonos Doris/Iceberg execute 接口执行安全只读 SQL。用于 SELECT、SHOW、DESC、DESCRIBE、EXPLAIN 等查询；必须拒绝 DDL、DML、删除、写入和危险语句。

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

- `scripts/query.py` imports `none`

## Safety And Robustness

- Do not broaden scope into a workflow. This skill should complete one bounded operation.
- Return actionable errors with backend name, query/id/path, and failure reason.
- For read-only database utilities, reject write, delete, DDL, DML, shell escape, or multi-statement hazards.
- For renderers, keep HTML content derived from input data and avoid hard-coded demo values.

## Validation Checklist

- Command exits cleanly or returns a structured error.
- Output can be consumed by a workflow.

## Example Command

```bash
python scripts/query.py "SELECT 1 AS ok"
```
