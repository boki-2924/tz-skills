#!/usr/bin/env python3
import argparse
import html
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, evidence_pack, split_people, extract_keywords, write_json, write_html, print_json


def main():
    parser = argparse.ArgumentParser(description="构建专家/机构关系图谱。")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    pack = evidence_pack(args.query, limit=args.limit)
    authors, journals, keywords, edges = Counter(), Counter(), Counter(), []
    for item in pack["items"]:
        doc = item.get("documentId")
        for author in split_people(item.get("authors")):
            authors[author] += 1
            edges.append({"source": author, "target": doc, "type": "author-document"})
        if item.get("journalName"):
            journals[item["journalName"]] += 1
        for kw in extract_keywords(item.get("extraMeta"), item.get("title"), limit=5):
            keywords[kw] += 1
            edges.append({"source": kw, "target": doc, "type": "keyword-document"})
    graph = {"query": args.query, "nodes": [{"id": k, "type": "author", "count": v} for k, v in authors.items()] + [{"id": k, "type": "journal", "count": v} for k, v in journals.items()] + [{"id": k, "type": "keyword", "count": v} for k, v in keywords.items()], "edges": edges}
    run_dir = make_run_dir("entity-graph", args.query, args.output_dir)
    write_json(run_dir / "entities.json", {"authors": dict(authors), "journals": dict(journals), "keywords": dict(keywords), "edges": edges})
    write_json(run_dir / "graph.json", graph)
    node_html = "".join(f"<span class='node'>{html.escape(str(n['id']))} <small>{n['type']}:{n['count']}</small></span>" for n in graph["nodes"][:160])
    rows = "".join(f"<tr><td>{html.escape(str(e['source']))}</td><td>{html.escape(str(e['target']))}</td><td>{e['type']}</td></tr>" for e in edges[:300])
    preview = run_dir / "previews" / "graph.html"
    write_html(preview, "专家/机构关系图谱", f"<h1>专家/机构关系图谱</h1><div class='card'>{node_html}</div><table><tr><th>源</th><th>目标</th><th>关系</th></tr>{rows}</table>")
    print_json({"run_dir": str(run_dir), "entities_json": str(run_dir / "entities.json"), "graph_json": str(run_dir / "graph.json"), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
