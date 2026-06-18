---
name: assemble-evidence-pack
description: "Workflow 层：围绕研究问题组装证据包。用于把自然语言 query 转为 evidence.json、answer_context.md 和证据预览；只编排 retrieval、document、chunk、MinIO 等 utility，可被综述、地图、图谱复用。"
---

# assemble-evidence-pack

## Layer Contract

- Layer: `workflow`
- Role: reusable process that produces intermediate artifacts.
- Allowed dependencies: utility skills only.
- Must not call usecase skills. A workflow can be used directly for narrow tasks or by multiple usecases.

## Workflow Goal

围绕研究问题组装证据包。用于把自然语言 query 转为 evidence.json、answer_context.md 和证据预览；只编排 retrieval、document、chunk、MinIO 等 utility，可被综述、地图、图谱复用。

## Execution Order

1. 接收 query、limit、output-dir；不要假定固定主题，所有检索内容随输入变化。
2. 调用 istiqra-retrieval-search 获得候选文献、chunk、score、召回类型和对象路径。
3. 标准化检索结果，保留 documentId、chunkId、title、score、markdownUrl/pdfUrl。
4. 调用 kb-document-query 补齐年份、期刊、作者、分类和解析状态。
5. 按需调用 kb-chunk-query 补齐页码、bbox、摘要和原文片段。
6. 保存 evidence.json、answer_context.md 和 previews/index.html。

## Inputs

- Accept the smallest stable input needed: query, document_id, evidence JSON, health sample size, or input file.
- Accept `--output-dir` where scripts support it.
- Do not assume a fixed research topic; all evidence and HTML content must follow runtime input.

## Utility Dependencies

- `istiqra-retrieval-search`
- `kb-document-query`
- `kb-chunk-query`
- `minio-object-get`

## Scripts

- `scripts/assemble_evidence.py` imports `make_run_dir, evidence_pack, save_evidence_outputs, print_json`

## Robustness Rules

- Write intermediate JSON before rendering HTML whenever possible.
- Degrade per step: retrieval/query/object/render failures should be recorded with context.
- Keep output schemas stable so downstream usecases can consume the workflow across topics.
- Do not synthesize evidence. If data is missing, mark it as missing.

## Validation Checklist

- evidence.json
- answer_context.md
- previews/index.html
- Output JSON parses successfully.
- HTML preview, when produced, opens locally.
- Counts and labels reflect the actual input evidence.

## Example Command

```bash
python scripts/assemble_evidence.py "丝绸之路经济带" --limit 10
```
