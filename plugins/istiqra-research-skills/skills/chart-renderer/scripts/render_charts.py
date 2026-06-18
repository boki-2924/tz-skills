#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, read_json, write_json, write_html, corpus_stats, bar_table, print_json


def main():
    parser = argparse.ArgumentParser(description="渲染文献统计图表。")
    parser.add_argument("--input")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    payload = read_json(Path(args.input)) if args.input else {"items": []}
    items = payload.get("items") or payload.get("evidence") or []
    stats = corpus_stats(items)
    run_dir = make_run_dir("charts", payload.get("query") or "charts", args.output_dir)
    body = "<h1>文献统计图表</h1>" + bar_table("年份分布", stats["years"]) + bar_table("期刊分布", stats["journals"]) + bar_table("作者分布", stats["authors"]) + bar_table("关键词分布", stats["keywords"])
    preview = run_dir / "previews" / "charts.html"
    write_html(preview, "文献统计图表", body)
    write_json(run_dir / "charts.json", stats)
    print_json({"run_dir": str(run_dir), "preview_html": str(preview), "charts_json": str(run_dir / "charts.json")})


if __name__ == "__main__":
    main()
