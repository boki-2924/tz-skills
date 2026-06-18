#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, read_json, write_json, write_html, evidence_pack, corpus_stats, extract_keywords, bar_table, print_json


def build_map(items):
    nodes = []
    links = []
    topic_seen = {}
    for item in items:
        doc_id = item.get("documentId")
        doc_node = {"id": doc_id, "type": "document", "label": item.get("title"), "year": item.get("publishYear")}
        nodes.append(doc_node)
        for kw in extract_keywords(item.get("extraMeta"), item.get("title"), limit=5):
            topic_id = "topic:" + kw
            if topic_id not in topic_seen:
                topic_seen[topic_id] = True
                nodes.append({"id": topic_id, "type": "topic", "label": kw})
            links.append({"source": topic_id, "target": doc_id, "type": "topic-document"})
    return {"nodes": nodes, "links": links}


def main():
    parser = argparse.ArgumentParser(description="渲染文献地图。")
    parser.add_argument("--input")
    parser.add_argument("--query")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    payload = read_json(Path(args.input)) if args.input else evidence_pack(args.query or "新疆", limit=args.limit)
    items = payload.get("items") or []
    map_data = build_map(items)
    stats = corpus_stats(items)
    run_dir = make_run_dir("literature-map", payload.get("query") or "literature-map", args.output_dir)
    nodes_html = "".join(f"<span class='node'>{html.escape(str(n.get('label') or n.get('id')))}</span>" for n in map_data["nodes"][:120])
    body = "<h1>文献地图</h1><div class='card'>" + nodes_html + "</div>" + bar_table("年份分布", stats["years"]) + bar_table("期刊分布", stats["journals"])
    preview = run_dir / "previews" / "literature_map.html"
    write_html(preview, "文献地图", body)
    write_json(run_dir / "literature_map.json", map_data)
    print_json({"run_dir": str(run_dir), "preview_html": str(preview), "map_json": str(run_dir / "literature_map.json")})


if __name__ == "__main__":
    main()
