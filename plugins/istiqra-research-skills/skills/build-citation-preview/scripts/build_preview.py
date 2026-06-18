#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, render_citation_preview, print_json


def main():
    parser = argparse.ArgumentParser(description="构建引用预览。")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    run_dir = make_run_dir("citation-preview", args.query, args.output_dir)
    result = render_citation_preview(args.query, run_dir, top_k=args.top_k)
    result["run_dir"] = str(run_dir)
    print_json(result)


if __name__ == "__main__":
    main()
