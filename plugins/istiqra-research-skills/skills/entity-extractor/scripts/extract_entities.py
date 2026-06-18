#!/usr/bin/env python3
import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, read_json, write_json, split_people, extract_keywords, print_json


def main():
    parser = argparse.ArgumentParser(description="从文献证据包抽取实体。")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    payload = read_json(Path(args.input))
    items = payload.get("items") or payload.get("evidence") or []
    authors, journals, keywords = Counter(), Counter(), Counter()
    edges = []
    for item in items:
        doc_id = item.get("documentId")
        for author in split_people(item.get("authors")):
            authors[author] += 1
            if doc_id:
                edges.append({"source": author, "target": doc_id, "type": "author-document"})
        if item.get("journalName"):
            journals[item["journalName"]] += 1
        for kw in extract_keywords(item.get("extraMeta"), item.get("title"), limit=8):
            keywords[kw] += 1
            if doc_id:
                edges.append({"source": kw, "target": doc_id, "type": "keyword-document"})
    result = {"authors": dict(authors.most_common()), "journals": dict(journals.most_common()), "keywords": dict(keywords.most_common()), "edges": edges}
    run_dir = make_run_dir("entities", payload.get("query") or "entities", args.output_dir)
    out = run_dir / "entities.json"
    write_json(out, result)
    print_json({"run_dir": str(run_dir), "entities_json": str(out), "summary": {k: len(v) if isinstance(v, dict) else len(v) for k, v in result.items()}})


if __name__ == "__main__":
    main()
