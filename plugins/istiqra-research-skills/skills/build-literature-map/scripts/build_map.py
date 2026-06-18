#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, evidence_pack, extract_keywords, corpus_stats, write_json, write_html, bar_table, print_json


def main():
    parser = argparse.ArgumentParser(description="构建文献地图。")
    parser.add_argument("query")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    pack = evidence_pack(args.query, limit=args.limit)
    nodes, links, seen = [], [], set()
    for item in pack["items"]:
        doc = item.get("documentId")
        nodes.append({"id": doc, "type": "document", "label": item.get("title"), "year": item.get("publishYear")})
        for kw in extract_keywords(item.get("extraMeta"), item.get("title"), limit=5):
            tid = "topic:" + kw
            if tid not in seen:
                seen.add(tid)
                nodes.append({"id": tid, "type": "topic", "label": kw})
            links.append({"source": tid, "target": doc, "type": "topic-document"})
    map_data = {"query": args.query, "nodes": nodes, "links": links}
    stats = corpus_stats(pack["items"])
    run_dir = make_run_dir("literature-map", args.query, args.output_dir)
    write_json(run_dir / "literature_map.json", map_data)
    node_html = "".join(f"<span class='node'>{html.escape(str(n.get('label') or n.get('id')))}</span>" for n in nodes[:160])
    preview = run_dir / "previews" / "literature_map.html"
    write_html(preview, "文献地图", "<h1>文献地图</h1><div class='card'>" + node_html + "</div>" + bar_table("年份", stats["years"]) + bar_table("期刊", stats["journals"]))
    print_json({"run_dir": str(run_dir), "map_json": str(run_dir / "literature_map.json"), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
