---
name: build-citation-preview
description: "Workflow 层：为检索证据生成 PDF bbox 高亮引用页。用于增强综述、证据卡和报告的可核验性，只编排 MinIO 读取和 citation preview renderer。"
---

# build-citation-preview

## Layer Contract

- Layer: `workflow`
- Role: reusable process that produces intermediate artifacts.
- Allowed dependencies: utility skills only.
- Must not call usecase skills. A workflow can be used directly for narrow tasks or by multiple usecases.

## Workflow Goal

为检索证据生成 PDF bbox 高亮引用页。用于增强综述、证据卡和报告的可核验性，只编排 MinIO 读取和 citation preview renderer。

## Execution Order

1. 读取 query 或 evidence
2. 定位 PDF/Markdown 对象路径
3. 调用 MinIO 检查或读取对象
4. 用 bbox/page 信息生成引用预览
5. 输出 citation_preview.json 和 previews/preview.html

## Inputs

- Accept the smallest stable input needed: query, document_id, evidence JSON, health sample size, or input file.
- Accept `--output-dir` where scripts support it.
- Do not assume a fixed research topic; all evidence and HTML content must follow runtime input.

## Utility Dependencies

- `citation-preview-renderer`
- `minio-object-get`

## Scripts

- `scripts/build_preview.py` imports `make_run_dir, render_citation_preview, print_json`

## Robustness Rules

- Write intermediate JSON before rendering HTML whenever possible.
- Degrade per step: retrieval/query/object/render failures should be recorded with context.
- Keep output schemas stable so downstream usecases can consume the workflow across topics.
- Do not synthesize evidence. If data is missing, mark it as missing.

## Validation Checklist

- citation_preview.json
- previews/preview.html
- previews/E01.html
- Output JSON parses successfully.
- HTML preview, when produced, opens locally.
- Counts and labels reflect the actual input evidence.

## Example Command

```bash
python scripts/build_preview.py "丝绸之路经济带" --top-k 2
```
