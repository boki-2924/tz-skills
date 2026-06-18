---
name: build-literature-map
description: "Workflow 层：基于检索证据构建文献地图数据和 HTML。用于把 evidence items 转换为 document/topic 节点、topic-document 边、年份和期刊分布，可被文献地图 use-case 复用。"
---

# build-literature-map

## Layer Contract

- Layer: `workflow`
- Role: reusable process that produces intermediate artifacts.
- Allowed dependencies: utility skills only.
- Must not call usecase skills. A workflow can be used directly for narrow tasks or by multiple usecases.

## Workflow Goal

基于检索证据构建文献地图数据和 HTML。用于把 evidence items 转换为 document/topic 节点、topic-document 边、年份和期刊分布，可被文献地图 use-case 复用。

## Execution Order

1. 读取 evidence items
2. 生成 document 节点并合并重复 documentId
3. 从 extra_meta、关键词和标题抽取 topic 节点
4. 建立 topic-document 关系边
5. 计算年份/期刊分布并渲染 HTML

## Inputs

- Accept the smallest stable input needed: query, document_id, evidence JSON, health sample size, or input file.
- Accept `--output-dir` where scripts support it.
- Do not assume a fixed research topic; all evidence and HTML content must follow runtime input.

## Utility Dependencies

- `entity-extractor`
- `literature-map-renderer`
- `chart-renderer`

## Scripts

- `scripts/build_map.py` imports `make_run_dir, evidence_pack, extract_keywords, corpus_stats, write_json, write_html, bar_table, print_json`

## Robustness Rules

- Write intermediate JSON before rendering HTML whenever possible.
- Degrade per step: retrieval/query/object/render failures should be recorded with context.
- Keep output schemas stable so downstream usecases can consume the workflow across topics.
- Do not synthesize evidence. If data is missing, mark it as missing.

## Validation Checklist

- literature_map.json
- previews/literature_map.html
- Output JSON parses successfully.
- HTML preview, when produced, opens locally.
- Counts and labels reflect the actual input evidence.

## Example Command

```bash
python scripts/build_map.py "丝绸之路经济带" --limit 20
```
