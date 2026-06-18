#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, evidence_pack, save_evidence_outputs, extract_keywords, corpus_stats, write_json, write_html, bar_table, print_json, metric_cards, evidence_cards, read_text_arg


def map_svg(topic, topics, docs):
    width, height = 1120, 520
    center_x, center_y = 170, 260
    doc_x = 860
    topic_x = 500
    topic_nodes = topics[:8]
    doc_nodes = docs[:10]
    parts = [f"<svg viewBox='0 0 {width} {height}' width='100%' height='520' role='img' aria-label='文献地图'>"]
    parts.append("<defs><filter id='shadow'><feDropShadow dx='0' dy='8' stdDeviation='10' flood-opacity='.12'/></filter></defs>")
    parts.append(f"<circle cx='{center_x}' cy='{center_y}' r='78' fill='#2563eb' filter='url(#shadow)'/><text x='{center_x}' y='{center_y-6}' text-anchor='middle' fill='white' font-size='18' font-weight='800'>研究主题</text><text x='{center_x}' y='{center_y+22}' text-anchor='middle' fill='white' font-size='12'>Topic</text>")
    for i, kw in enumerate(topic_nodes):
        y = 78 + i * 52
        parts.append(f"<line x1='{center_x+78}' y1='{center_y}' x2='{topic_x-80}' y2='{y}' stroke='#a7c5f9' stroke-width='2'/>")
        parts.append(f"<rect x='{topic_x-80}' y='{y-20}' width='170' height='40' rx='20' fill='#eef5ff' stroke='#bfdbfe'/><text x='{topic_x+5}' y='{y+5}' text-anchor='middle' fill='#1d4ed8' font-size='13'>{html.escape(str(kw)[:18])}</text>")
    for i, doc in enumerate(doc_nodes):
        y = 50 + i * 44
        topic_y = 78 + (i % max(1, len(topic_nodes))) * 52
        parts.append(f"<line x1='{topic_x+90}' y1='{topic_y}' x2='{doc_x-34}' y2='{y}' stroke='#d5dde8' stroke-width='1.5'/>")
        parts.append(f"<circle cx='{doc_x}' cy='{y}' r='24' fill='#22c55e' opacity='.9'/><text x='{doc_x+38}' y='{y+5}' fill='#334155' font-size='12'>{html.escape(str(doc.get('title') or '')[:28])}</text>")
    parts.append("</svg>")
    return "<div class='svg-wrap'>" + "".join(parts) + "</div>"


def main():
    parser = argparse.ArgumentParser(description="生成文献地图。")
    parser.add_argument("topic", nargs="?")
    parser.add_argument("--topic-file")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    topic = read_text_arg(args.topic, args.topic_file, "文献地图")
    run_dir = make_run_dir("literature-map-generator", topic, args.output_dir)
    pack = evidence_pack(topic, limit=args.limit)
    save_evidence_outputs(run_dir, pack, title="文献地图证据包")
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
    stats = corpus_stats(pack["items"])
    map_data = {"topic": topic, "nodes": nodes, "links": links, "stats": stats}
    write_json(run_dir / "literature_map.json", map_data)
    top_topics = [n.get("label") for n in nodes if n.get("type") == "topic"]
    node_html = "".join(f"<span class='node'>{html.escape(str(n.get('label') or n.get('id')))}</span>" for n in nodes[:80])
    preview = run_dir / "previews" / "literature_map.html"
    body = (
        f"<section class='hero'><div class='eyebrow'>LITERATURE MAP</div><h1>{html.escape(topic)}：文献地图</h1><p class='subtitle'>从真实检索证据中提取主题词、文献节点和年份/期刊分布，形成可浏览的专题地图。</p></section>"
        + metric_cards([("文献节点", len(pack["items"]), "检索候选"), ("主题节点", len(top_topics), "关键词/主题线索"), ("关系边", len(links), "主题到文献"), ("时间跨度", f"{min(stats['years']) if stats['years'] else '-'} - {max(stats['years']) if stats['years'] else '-'}", "按发表年份")])
        + map_svg(topic, top_topics, pack["items"])
        + "<h2>主题节点</h2><div class='card'>" + node_html + "</div>"
        + bar_table("年份时间线", stats["years"])
        + bar_table("期刊分布", stats["journals"])
        + "<h2>代表文献</h2>" + evidence_cards(pack["items"], limit=8)
    )
    write_html(preview, "文献地图生成器", body)
    print_json({"run_dir": str(run_dir), "map_json": str(run_dir / "literature_map.json"), "evidence_json": str(run_dir / "evidence.json"), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
