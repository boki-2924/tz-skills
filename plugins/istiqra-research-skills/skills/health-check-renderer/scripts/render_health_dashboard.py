#!/usr/bin/env python3
import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, read_json, write_html, print_json


def main():
    parser = argparse.ArgumentParser(description="渲染知识库健康巡检看板。")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    data = read_json(Path(args.input))
    run_dir = make_run_dir("health-dashboard", "health", args.output_dir)
    cards = "".join(f"<div class='card'><h2>{html.escape(str(k))}</h2><pre>{html.escape(json.dumps(v, ensure_ascii=False, indent=2, default=str))}</pre></div>" for k, v in data.items())
    preview = run_dir / "previews" / "health.html"
    write_html(preview, "知识库健康巡检", f"<h1>知识库健康巡检</h1><div class='grid'>{cards}</div>")
    print_json({"run_dir": str(run_dir), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
