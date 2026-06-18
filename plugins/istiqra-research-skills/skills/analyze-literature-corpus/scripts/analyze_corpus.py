#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, evidence_pack, corpus_stats, write_json, write_html, bar_table, print_json


def main():
    parser = argparse.ArgumentParser(description="分析文献语料分布。")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    pack = evidence_pack(args.query, limit=args.limit)
    stats = corpus_stats(pack["items"])
    run_dir = make_run_dir("corpus-analysis", args.query, args.output_dir)
    write_json(run_dir / "corpus_stats.json", stats)
    body = "<h1>文献语料分析</h1>" + bar_table("年份", stats["years"]) + bar_table("期刊", stats["journals"]) + bar_table("作者", stats["authors"]) + bar_table("关键词", stats["keywords"])
    preview = run_dir / "previews" / "charts.html"
    write_html(preview, "文献语料分析", body)
    print_json({"run_dir": str(run_dir), "stats_json": str(run_dir / "corpus_stats.json"), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
