#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, read_json, write_json, write_html, print_json


def main():
    parser = argparse.ArgumentParser(description="渲染实体关系图谱。")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    data = read_json(Path(args.input))
    nodes = []
    for kind in ["authors", "journals", "keywords"]:
        for name, count in (data.get(kind) or {}).items():
            nodes.append({"id": name, "type": kind, "count": count})
    graph = {"nodes": nodes, "edges": data.get("edges") or []}
    run_dir = make_run_dir("graph", "entity-graph", args.output_dir)
    node_html = "".join(f"<span class='node'>{html.escape(str(n['id']))} <small>{n['type']}:{n['count']}</small></span>" for n in nodes[:160])
    edge_rows = "".join(f"<tr><td>{html.escape(str(e.get('source')))}</td><td>{html.escape(str(e.get('target')))}</td><td>{html.escape(str(e.get('type')))}</td></tr>" for e in graph["edges"][:300])
    body = f"<h1>专家/机构/关键词关系图谱</h1><div class='card'>{node_html}</div><h2>关系边</h2><table><tr><th>源</th><th>目标</th><th>类型</th></tr>{edge_rows}</table>"
    preview = run_dir / "previews" / "graph.html"
    write_html(preview, "关系图谱", body)
    write_json(run_dir / "graph.json", graph)
    print_json({"run_dir": str(run_dir), "preview_html": str(preview), "graph_json": str(run_dir / "graph.json")})


if __name__ == "__main__":
    main()
