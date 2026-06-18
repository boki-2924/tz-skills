---
name: topic-literature-review
description: "Use-case 层：专题文献综述助手。用于用户围绕中文研究主题生成可核验综述、证据表、主题线索、年份/期刊分布和 HTML 报告时。必须从用户意图出发，编排 evidence、corpus、citation 和 rendering workflows，不直接替代底层 utility。"
---

# topic-literature-review

## Layer Contract

- Layer: `usecase`
- Role: business-facing entry point that turns user intent into final deliverables.
- Allowed dependencies: workflow and utility skills only.
- Must not be used as a generic utility. If the user asks for one atomic action, route to a utility instead.

## Business Goal

研究人员要写综述或需要围绕一个主题形成证据化、可追溯的文献综述。

## Execution Order

1. 解析用户主题、范围、输出深度和 limit；未指定时先用中等样本生成可读版本。
2. 调用 assemble-evidence-pack 召回文献、补齐文档元数据和 chunk 证据，生成 evidence.json 与 answer_context.md。
3. 调用 analyze-literature-corpus 统计年份、期刊、作者、关键词和主题线索。
4. 需要引用定位或用户要求可核验出处时，调用 build-citation-preview 生成 PDF 页面或 bbox 高亮预览。
5. 组织综述提纲、证据卡片、统计图表和结论边界，渲染最终 HTML/JSON。

## Inputs

- `topic` or natural-language research question for research use-cases.
- Optional `limit`, `topic-file`, `output-dir`, evidence constraints, and requested views.
- For health audit, optional sample size and environment configuration.

## Dependencies

- `assemble-evidence-pack`
- `analyze-literature-corpus`
- `html-report-renderer`
- `build-citation-preview`

## Scripts

- `scripts/topic_review.py` imports `make_run_dir, evidence_pack, save_evidence_outputs, corpus_stats, write_json, write_html, bar_table, print_json, metric_cards, evidence_cards, read_text_arg`

## Robustness Rules

- Treat each user topic as dynamic. Do not hard-code titles, years, journals, keywords, paths, or HTML copy.
- Preserve intermediate artifacts even when the final rendering fails.
- If a dependency returns partial data, continue with explicit caveats rather than inventing missing evidence.
- Keep provenance: retain `documentId`, `chunkId`, paths, score, year, journal, and source fields whenever available.
- When result volume is too large, render a readable top-N view and keep full data in JSON.

## Validation Checklist

- literature_review.json
- evidence.json
- answer_context.md
- previews/index.html
- Generated HTML opens locally and contains the requested use-case sections.
- Evidence count, node count, or health metrics are consistent with the JSON artifacts.

## Example Command

```bash
python scripts/topic_review.py "丝绸之路经济带建设对新疆口岸经济的影响" --limit 10
```
