---
name: deep-read-literature
description: "Workflow 层：按 document_id 深读单篇文献。用于读取文档元数据和 chunk，输出结构化阅读笔记、关键段落和 HTML 原文导读，只编排 document/chunk/MinIO/render utilities。"
---

# deep-read-literature

## Layer Contract

- Layer: `workflow`
- Role: reusable process that produces intermediate artifacts.
- Allowed dependencies: utility skills only.
- Must not call usecase skills. A workflow can be used directly for narrow tasks or by multiple usecases.

## Workflow Goal

按 document_id 深读单篇文献。用于读取文档元数据和 chunk，输出结构化阅读笔记、关键段落和 HTML 原文导读，只编排 document/chunk/MinIO/render utilities。

## Execution Order

1. 接收 document_id 或精确标题
2. 查询 kb_document 元数据
3. 读取该文档 chunks 并按页码/章节排序
4. 必要时读取 MinIO 原文
5. 输出阅读笔记和 HTML 导读

## Inputs

- Accept the smallest stable input needed: query, document_id, evidence JSON, health sample size, or input file.
- Accept `--output-dir` where scripts support it.
- Do not assume a fixed research topic; all evidence and HTML content must follow runtime input.

## Utility Dependencies

- `kb-document-query`
- `kb-chunk-query`
- `minio-object-get`
- `html-report-renderer`

## Scripts

- `scripts/deep_read.py` imports `make_run_dir, fetch_documents, fetch_chunks, write_json, write_html, print_json`

## Robustness Rules

- Write intermediate JSON before rendering HTML whenever possible.
- Degrade per step: retrieval/query/object/render failures should be recorded with context.
- Keep output schemas stable so downstream usecases can consume the workflow across topics.
- Do not synthesize evidence. If data is missing, mark it as missing.

## Validation Checklist

- reading_notes.json
- previews/deep_read.html
- Output JSON parses successfully.
- HTML preview, when produced, opens locally.
- Counts and labels reflect the actual input evidence.

## Example Command

```bash
python scripts/deep_read.py 623739c36e7c4ecb97397feeba3454bf
```
