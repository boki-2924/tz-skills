#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, evidence_pack, save_evidence_outputs, print_json


def main():
    parser = argparse.ArgumentParser(description="组装文献证据包。")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    run_dir = make_run_dir("evidence-pack", args.query, args.output_dir)
    pack = evidence_pack(args.query, limit=args.limit)
    result = save_evidence_outputs(run_dir, pack, title="文献证据包")
    print_json(result)


if __name__ == "__main__":
    main()
