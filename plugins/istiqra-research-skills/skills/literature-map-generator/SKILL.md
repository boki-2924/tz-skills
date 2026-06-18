---
name: literature-map-generator
description: "Use-case 层：文献地图生成器。用于用户要求围绕研究主题生成文献地图、主题节点、文献节点、年份时间线、期刊分布和交互 HTML 时。必须编排 evidence 与 map workflows，并保留可追溯证据包。"
---

# literature-map-generator

## Layer Contract

- Layer: `usecase`
- Role: business-facing entry point that turns user intent into final deliverables.
- Allowed dependencies: workflow and utility skills only.
- Must not be used as a generic utility. If the user asks for one atomic action, route to a utility instead.

## Business Goal

负责人或研究者要快速看清一个主题的研究版图和文献/主题分布。

## Execution Order

1. 读取自然语言 topic 或 --topic-file，确定 limit、输出目录和地图粒度。
2. 调用 assemble-evidence-pack 形成证据包，保留 documentId、title、year、journal、extra_meta。
3. 调用 build-literature-map 抽取 document/topic 节点，建立 topic-document 边。
4. 调用 chart-renderer 或 literature-map-renderer 生成年份时间线、期刊分布和地图 HTML。
5. 输出 literature_map.json、evidence.json 和 previews/literature_map.html。

## Inputs

- `topic` or natural-language research question for research use-cases.
- Optional `limit`, `topic-file`, `output-dir`, evidence constraints, and requested views.
- For health audit, optional sample size and environment configuration.

## Dependencies

- `assemble-evidence-pack`
- `build-literature-map`
- `chart-renderer`
- `literature-map-renderer`

## Scripts

- `scripts/generate_literature_map.py` imports `make_run_dir, evidence_pack, save_evidence_outputs, extract_keywords, corpus_stats, write_json, write_html, bar_table, print_json, metric_cards, evidence_cards, read_text_arg`

## Robustness Rules

- Treat each user topic as dynamic. Do not hard-code titles, years, journals, keywords, paths, or HTML copy.
- Preserve intermediate artifacts even when the final rendering fails.
- If a dependency returns partial data, continue with explicit caveats rather than inventing missing evidence.
- Keep provenance: retain `documentId`, `chunkId`, paths, score, year, journal, and source fields whenever available.
- When result volume is too large, render a readable top-N view and keep full data in JSON.

## Validation Checklist

- literature_map.json
- evidence.json
- answer_context.md
- previews/literature_map.html
- Generated HTML opens locally and contains the requested use-case sections.
- Evidence count, node count, or health metrics are consistent with the JSON artifacts.

## Example Command

```bash
python scripts/generate_literature_map.py "新疆教育" --limit 20
```
