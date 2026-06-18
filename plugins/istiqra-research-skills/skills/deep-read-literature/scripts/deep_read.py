#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, fetch_documents, fetch_chunks, write_json, write_html, print_json


def main():
    parser = argparse.ArgumentParser(description="深读单篇文献。")
    parser.add_argument("document_id")
    parser.add_argument("--chunk-limit", type=int, default=20)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    run_dir = make_run_dir("deep-read", args.document_id, args.output_dir)
    docs = fetch_documents([args.document_id])
    chunks = fetch_chunks(args.document_id, limit=args.chunk_limit)
    payload = {"document": docs[0] if docs else {}, "chunks": chunks}
    write_json(run_dir / "deep_read.json", payload)
    lines = [f"# 文献深读\n\n文档：`{args.document_id}`\n\n"]
    if docs:
        lines.append(f"题名：{docs[0].get('title')}\n\n期刊：{docs[0].get('journal_name')}，年份：{docs[0].get('publish_year')}\n\n")
    for c in chunks:
        lines.append(f"## Chunk {c.get('chunk_index')}\n\n{c.get('chunk_content') or c.get('abstract') or ''}\n\n")
    (run_dir / "answer_context.md").write_text("".join(lines), encoding="utf-8")
    rows = "".join(f"<tr><td>{c.get('chunk_index')}</td><td>{html.escape(str(c.get('page_num')))}</td><td>{html.escape(str(c.get('chunk_content') or c.get('abstract') or ''))}</td></tr>" for c in chunks)
    preview = run_dir / "previews" / "deep_read.html"
    write_html(preview, "文献深读", f"<h1>文献深读</h1><pre>{html.escape(str(payload['document']))}</pre><table><tr><th>序号</th><th>页码</th><th>内容</th></tr>{rows}</table>")
    print_json({"run_dir": str(run_dir), "deep_read_json": str(run_dir / "deep_read.json"), "answer_context": str(run_dir / "answer_context.md"), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
