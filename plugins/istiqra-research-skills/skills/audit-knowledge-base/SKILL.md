---
name: audit-knowledge-base
description: "Workflow 层：巡检 Istiqra 知识库。用于检查 Doris 表规模、embedding 状态、collection 状态、MinIO 样本对象和异常清单，只编排只读 SQL、catalog、embedding 和 MinIO utilities。"
---

# audit-knowledge-base

## Layer Contract

- Layer: `workflow`
- Role: reusable process that produces intermediate artifacts.
- Allowed dependencies: utility skills only.
- Must not call usecase skills. A workflow can be used directly for narrow tasks or by multiple usecases.

## Workflow Goal

巡检 Istiqra 知识库。用于检查 Doris 表规模、embedding 状态、collection 状态、MinIO 样本对象和异常清单，只编排只读 SQL、catalog、embedding 和 MinIO utilities。

## Execution Order

1. 检查 catalog/database/table 元数据
2. 执行只读统计 SQL
3. 查询 embedding mapping 摘要
4. 抽样检查 MinIO 对象可达性
5. 汇总 health/audit JSON

## Inputs

- Accept the smallest stable input needed: query, document_id, evidence JSON, health sample size, or input file.
- Accept `--output-dir` where scripts support it.
- Do not assume a fixed research topic; all evidence and HTML content must follow runtime input.

## Utility Dependencies

- `doris-catalog-inspect`
- `doris-sql-readonly`
- `kb-embedding-map-query`
- `minio-object-get`

## Scripts

- `scripts/audit_kb.py` imports `make_run_dir, execute_sql, rows, fetch_embedding_summary, stat_minio, write_json, write_html, print_json`

## Robustness Rules

- Write intermediate JSON before rendering HTML whenever possible.
- Degrade per step: retrieval/query/object/render failures should be recorded with context.
- Keep output schemas stable so downstream usecases can consume the workflow across topics.
- Do not synthesize evidence. If data is missing, mark it as missing.

## Validation Checklist

- health.json
- audit.json
- Output JSON parses successfully.
- HTML preview, when produced, opens locally.
- Counts and labels reflect the actual input evidence.

## Example Command

```bash
python scripts/audit_kb.py --sample 5
```
