---
name: expert-institution-graph
description: "Use-case 层：专家/机构关系图谱。用于用户围绕主题识别作者、机构、期刊、关键词和文献关系，并输出 graph.json、entities.json 和交互 HTML 图谱时。必须复用 evidence 与 entity graph workflows。"
---

# expert-institution-graph

## Layer Contract

- Layer: `usecase`
- Role: business-facing entry point that turns user intent into final deliverables.
- Allowed dependencies: workflow and utility skills only.
- Must not be used as a generic utility. If the user asks for one atomic action, route to a utility instead.

## Business Goal

用户要发现专家、机构、期刊和关键词之间的关系网络。

## Execution Order

1. 解析主题和图谱目标：专家、机构、期刊、关键词或混合关系。
2. 调用 assemble-evidence-pack 获取证据和文档元数据。
3. 调用 build-entity-graph / entity-extractor 抽取作者、机构、期刊、关键词。
4. 构建实体-文献、作者-机构、关键词-文献或共现关系。
5. 调用 graph-renderer 渲染 graph.html，并保存 entities.json 与 graph.json。

## Inputs

- `topic` or natural-language research question for research use-cases.
- Optional `limit`, `topic-file`, `output-dir`, evidence constraints, and requested views.
- For health audit, optional sample size and environment configuration.

## Dependencies

- `build-entity-graph`
- `assemble-evidence-pack`
- `graph-renderer`
- `html-report-renderer`

## Scripts

- `scripts/generate_expert_graph.py` imports `make_run_dir, evidence_pack, save_evidence_outputs, split_people, extract_keywords, write_json, write_html, print_json, metric_cards, evidence_cards, read_text_arg, fetch_documents`

## Robustness Rules

- Treat each user topic as dynamic. Do not hard-code titles, years, journals, keywords, paths, or HTML copy.
- Preserve intermediate artifacts even when the final rendering fails.
- If a dependency returns partial data, continue with explicit caveats rather than inventing missing evidence.
- Keep provenance: retain `documentId`, `chunkId`, paths, score, year, journal, and source fields whenever available.
- When result volume is too large, render a readable top-N view and keep full data in JSON.

## Validation Checklist

- entities.json
- graph.json
- evidence.json
- previews/graph.html
- Generated HTML opens locally and contains the requested use-case sections.
- Evidence count, node count, or health metrics are consistent with the JSON artifacts.

## Example Command

```bash
python scripts/generate_expert_graph.py "新疆教育" --limit 20
```
