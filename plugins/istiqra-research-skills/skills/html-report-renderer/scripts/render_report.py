#!/usr/bin/env python3
import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, read_json, write_json, write_html, evidence_table, print_json


def main():
    parser = argparse.ArgumentParser(description="将 JSON 渲染为 HTML 报告。")
    parser.add_argument("--input")
    parser.add_argument("--title", default="Istiqra HTML 报告")
    parser.add_argument("--output-dir")
    args = parser.parse_args()

    payload = read_json(Path(args.input)) if args.input else {
        "summary": "这是一个样例报告。",
        "items": [{"rank": 1, "title": "样例文献", "journalName": "样例期刊", "publishYear": "2026", "chunkContent": "样例证据片段。"}],
    }
    run_dir = make_run_dir("html-report", args.title, args.output_dir)
    items = payload.get("items") or payload.get("evidence") or []
    body = f"<h1>{html.escape(args.title)}</h1><pre>{html.escape(json.dumps(payload, ensure_ascii=False, indent=2, default=str))}</pre>"
    if isinstance(items, list) and items:
        body += "<h2>证据表</h2>" + evidence_table(items)
    preview = run_dir / "previews" / "index.html"
    write_html(preview, args.title, body)
    write_json(run_dir / "report.json", payload)
    print_json({"run_dir": str(run_dir), "preview_html": str(preview), "report_json": str(run_dir / "report.json")})


if __name__ == "__main__":
    main()
