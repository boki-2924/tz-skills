---
name: knowledge-base-health-audit
description: "Use-case 层：知识库运维巡检。用于用户要求生成知识库健康评分、Doris 表规模、embedding/Milvus 状态、MinIO 对象可达性和 HTML 巡检看板时。必须保持只读、可采样、可降级。"
---

# knowledge-base-health-audit

## Layer Contract

- Layer: `usecase`
- Role: business-facing entry point that turns user intent into final deliverables.
- Allowed dependencies: workflow and utility skills only.
- Must not be used as a generic utility. If the user asks for one atomic action, route to a utility instead.

## Business Goal

运维或数据负责人要检查知识库质量、规模、索引和对象可达性。

## Execution Order

1. 确认只读巡检范围、采样规模和输出目录。
2. 调用 audit-knowledge-base 汇总 Doris 表规模和核心字段状态。
3. 调用 embedding / Milvus 相关 utility 检查模型、维度、collection 和映射数量。
4. 抽样调用 MinIO 对象检查，记录 markdown/pdf 对象可达性。
5. 计算健康评分并调用 health-check-renderer 输出 health.json 与 health.html。

## Inputs

- `topic` or natural-language research question for research use-cases.
- Optional `limit`, `topic-file`, `output-dir`, evidence constraints, and requested views.
- For health audit, optional sample size and environment configuration.

## Dependencies

- `audit-knowledge-base`
- `health-check-renderer`
- `doris-sql-readonly`
- `minio-object-get`

## Scripts

- `scripts/run_health_audit.py` imports `make_run_dir, execute_sql, rows, fetch_embedding_summary, stat_minio, write_json, write_html, print_json, metric_cards`

## Robustness Rules

- Treat each user topic as dynamic. Do not hard-code titles, years, journals, keywords, paths, or HTML copy.
- Preserve intermediate artifacts even when the final rendering fails.
- If a dependency returns partial data, continue with explicit caveats rather than inventing missing evidence.
- Keep provenance: retain `documentId`, `chunkId`, paths, score, year, journal, and source fields whenever available.
- When result volume is too large, render a readable top-N view and keep full data in JSON.

## Validation Checklist

- health.json
- previews/health.html
- Generated HTML opens locally and contains the requested use-case sections.
- Evidence count, node count, or health metrics are consistent with the JSON artifacts.

## Example Command

```bash
python scripts/run_health_audit.py --sample 5
```
