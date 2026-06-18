---
name: analyze-literature-corpus
description: "Workflow 层：分析一组文献证据的年份、期刊、作者、关键词和主题分布。用于证据包统计和图表生成，只编排统计与渲染 utility，不直接承担最终 use-case。"
---

# analyze-literature-corpus

## Layer Contract

- Layer: `workflow`
- Role: reusable process that produces intermediate artifacts.
- Allowed dependencies: utility skills only.
- Must not call usecase skills. A workflow can be used directly for narrow tasks or by multiple usecases.

## Workflow Goal

分析一组文献证据的年份、期刊、作者、关键词和主题分布。用于证据包统计和图表生成，只编排统计与渲染 utility，不直接承担最终 use-case。

## Execution Order

1. 读取 evidence.json 或直接按 query 召回小样本
2. 计算 corpus_stats：years、journals、authors、keywords
3. 调用 chart-renderer 生成 charts.html
4. 输出 corpus_stats.json 和统计预览

## Inputs

- Accept the smallest stable input needed: query, document_id, evidence JSON, health sample size, or input file.
- Accept `--output-dir` where scripts support it.
- Do not assume a fixed research topic; all evidence and HTML content must follow runtime input.

## Utility Dependencies

- `chart-renderer`
- `entity-extractor`

## Scripts

- `scripts/analyze_corpus.py` imports `make_run_dir, evidence_pack, corpus_stats, write_json, write_html, bar_table, print_json`

## Robustness Rules

- Write intermediate JSON before rendering HTML whenever possible.
- Degrade per step: retrieval/query/object/render failures should be recorded with context.
- Keep output schemas stable so downstream usecases can consume the workflow across topics.
- Do not synthesize evidence. If data is missing, mark it as missing.

## Validation Checklist

- corpus_stats.json
- charts.html
- Output JSON parses successfully.
- HTML preview, when produced, opens locally.
- Counts and labels reflect the actual input evidence.

## Example Command

```bash
python scripts/analyze_corpus.py "新疆教育" --limit 20
```
