---
name: build-entity-graph
description: "Workflow 层：从文献证据中抽取作者、机构、期刊、关键词并构建关系图谱。用于生成 entities.json、graph.json 和 graph.html，只编排 entity extraction 与 graph rendering utilities。"
---

# build-entity-graph

## Layer Contract

- Layer: `workflow`
- Role: reusable process that produces intermediate artifacts.
- Allowed dependencies: utility skills only.
- Must not call usecase skills. A workflow can be used directly for narrow tasks or by multiple usecases.

## Workflow Goal

从文献证据中抽取作者、机构、期刊、关键词并构建关系图谱。用于生成 entities.json、graph.json 和 graph.html，只编排 entity extraction 与 graph rendering utilities。

## Execution Order

1. 读取 evidence.json 和文档元数据
2. 抽取作者、机构、期刊、关键词实体
3. 统计实体频次和共现关系
4. 构建 nodes/edges 图结构
5. 输出 graph.json 并渲染图谱 HTML

## Inputs

- Accept the smallest stable input needed: query, document_id, evidence JSON, health sample size, or input file.
- Accept `--output-dir` where scripts support it.
- Do not assume a fixed research topic; all evidence and HTML content must follow runtime input.

## Utility Dependencies

- `entity-extractor`
- `graph-renderer`

## Scripts

- `scripts/build_graph.py` imports `make_run_dir, evidence_pack, split_people, extract_keywords, write_json, write_html, print_json`

## Robustness Rules

- Write intermediate JSON before rendering HTML whenever possible.
- Degrade per step: retrieval/query/object/render failures should be recorded with context.
- Keep output schemas stable so downstream usecases can consume the workflow across topics.
- Do not synthesize evidence. If data is missing, mark it as missing.

## Validation Checklist

- entities.json
- graph.json
- graph.html
- Output JSON parses successfully.
- HTML preview, when produced, opens locally.
- Counts and labels reflect the actual input evidence.

## Example Command

```bash
python scripts/build_graph.py "新疆教育" --limit 20
```
