#!/usr/bin/env python3
import argparse
import html
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, evidence_pack, save_evidence_outputs, split_people, extract_keywords, write_json, write_html, print_json, metric_cards, evidence_cards, read_text_arg, fetch_documents


def graph_svg(topic, nodes, edges):
    width, height = 1120, 620
    buckets = {
        "author": [n for n in nodes if n.get("type") == "author"][:8],
        "institution": [n for n in nodes if n.get("type") == "institution"][:8],
        "journal": [n for n in nodes if n.get("type") == "journal"][:7],
        "keyword": [n for n in nodes if n.get("type") == "keyword"][:8],
    }
    parts = [f"<svg viewBox='0 0 {width} {height}' width='100%' height='620' role='img' aria-label='专家机构关系图谱'>"]
    parts.append(
        "<defs>"
        "<filter id='shadow'><feDropShadow dx='0' dy='8' stdDeviation='10' flood-opacity='.12'/></filter>"
        "<linearGradient id='hub' x1='0' x2='1'><stop stop-color='#2563eb'/><stop offset='1' stop-color='#06b6d4'/></linearGradient>"
        "</defs>"
    )
    parts.append("<rect x='405' y='36' width='310' height='72' rx='20' fill='url(#hub)' filter='url(#shadow)'/>")
    parts.append("<text x='560' y='68' text-anchor='middle' fill='white' font-size='18' font-weight='800'>研究主题</text>")
    parts.append("<text x='560' y='92' text-anchor='middle' fill='white' font-size='12'>Topic-centered evidence graph</text>")
    lanes = [
        ("author", 40, "#22c55e", "作者", "从 authors 字段抽取"),
        ("institution", 310, "#14b8a6", "机构", "从 author_org 补充"),
        ("journal", 580, "#f59e0b", "期刊", "来源期刊"),
        ("keyword", 850, "#8b5cf6", "关键词", "主题线索"),
    ]
    for kind, x, color, label, hint in lanes:
        col_w = 230
        parts.append(f"<path d='M560 108 C560 138 {x + col_w/2:.0f} 132 {x + col_w/2:.0f} 162' fill='none' stroke='{color}' stroke-opacity='.38' stroke-width='2.4'/>")
        parts.append(f"<rect x='{x}' y='154' width='{col_w}' height='398' rx='18' fill='white' stroke='#dbe7f3' filter='url(#shadow)'/>")
        parts.append(f"<circle cx='{x+28}' cy='186' r='9' fill='{color}'/><text x='{x+46}' y='191' fill='#0f172a' font-size='15' font-weight='800'>{label}</text>")
        parts.append(f"<text x='{x+46}' y='213' fill='#64748b' font-size='11'>{hint}</text>")
        arr = buckets[kind]
        for i, node in enumerate(arr):
            y = 240 + i * 36
            count = int(node.get("count") or 1)
            label_text = str(node["id"])[:18] if kind == "institution" else str(node["id"])[:20]
            parts.append(f"<rect x='{x+18}' y='{y-18}' width='{col_w-36}' height='28' rx='14' fill='#f8fafc' stroke='#e2e8f0'/>")
            parts.append(f"<circle cx='{x+34}' cy='{y-4}' r='{7 + min(5, count)}' fill='{color}' opacity='.88'/>")
            parts.append(f"<text x='{x+52}' y='{y}' fill='#334155' font-size='12'>{html.escape(label_text)}</text>")
            parts.append(f"<text x='{x+col_w-30}' y='{y}' text-anchor='end' fill='#94a3b8' font-size='11'>{count}</text>")
        if not arr:
            parts.append(f"<text x='{x+24}' y='250' fill='#94a3b8' font-size='12'>暂无可抽取实体</text>")
    parts.append("<text x='560' y='592' text-anchor='middle' fill='#64748b' font-size='12'>节点数字表示该实体在候选文献中的出现次数；详细边关系见下方 JSON/表格。</text>")
    parts.append("</svg>")
    return "<div class='svg-wrap'>" + "".join(parts) + "</div>"


def main():
    parser = argparse.ArgumentParser(description="生成专家/机构关系图谱。")
    parser.add_argument("topic", nargs="?")
    parser.add_argument("--topic-file")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    topic = read_text_arg(args.topic, args.topic_file, "专家机构图谱")
    run_dir = make_run_dir("expert-institution-graph", topic, args.output_dir)
    pack = evidence_pack(topic, limit=args.limit)
    save_evidence_outputs(run_dir, pack, title="专家机构图谱证据包")
    authors, institutions, journals, keywords, edges = Counter(), Counter(), Counter(), Counter(), []
    doc_meta = {row.get("document_id"): row for row in fetch_documents([x.get("documentId") for x in pack["items"] if x.get("documentId")])}
    for item in pack["items"]:
        doc = item.get("documentId")
        meta = doc_meta.get(doc) or {}
        for author in split_people(item.get("authors")):
            authors[author] += 1
            edges.append({"source": author, "target": doc, "type": "author-document"})
        for org in split_people(meta.get("author_org")):
            institutions[org] += 1
            edges.append({"source": org, "target": doc, "type": "institution-document"})
        if item.get("journalName"):
            journals[item["journalName"]] += 1
        for kw in extract_keywords(item.get("extraMeta"), item.get("title"), limit=5):
            keywords[kw] += 1
            edges.append({"source": kw, "target": doc, "type": "keyword-document"})
    entities = {"authors": dict(authors), "institutions": dict(institutions), "journals": dict(journals), "keywords": dict(keywords), "edges": edges}
    graph = {
        "topic": topic,
        "nodes": [{"id": k, "type": "author", "count": v} for k, v in authors.items()]
        + [{"id": k, "type": "institution", "count": v} for k, v in institutions.items()]
        + [{"id": k, "type": "journal", "count": v} for k, v in journals.items()]
        + [{"id": k, "type": "keyword", "count": v} for k, v in keywords.items()],
        "edges": edges,
    }
    write_json(run_dir / "entities.json", entities)
    write_json(run_dir / "graph.json", graph)
    nodes_html = "".join(f"<span class='node'>{html.escape(str(n['id']))} <small>{n['type']}:{n['count']}</small></span>" for n in graph["nodes"][:80])
    rows = "".join(f"<tr><td>{html.escape(str(e['source']))}</td><td>{html.escape(str(e['target']))}</td><td>{e['type']}</td></tr>" for e in edges[:400])
    preview = run_dir / "previews" / "graph.html"
    body = (
        f"<section class='hero'><div class='eyebrow'>EXPERT & INSTITUTION GRAPH</div><h1>{html.escape(topic)}：专家/机构关系图谱</h1><p class='subtitle'>从真实检索结果抽取作者、期刊和关键词实体，展示主题周边的知识网络。</p></section>"
        + metric_cards([("作者实体", len(authors), "从 authors 字段抽取"), ("机构实体", len(institutions), "从 author_org 补充"), ("期刊实体", len(journals), "来源期刊"), ("关系边", len(edges), "实体到文献")])
        + graph_svg(topic, graph["nodes"], edges)
        + "<h2>核心实体</h2><div class='card'>" + nodes_html + "</div><h2>关系边样例</h2>"
        + f"<table><tr><th>源</th><th>目标</th><th>关系</th></tr>{rows}</table>"
        + "<h2>证据文献</h2>" + evidence_cards(pack["items"], limit=8)
    )
    write_html(preview, "专家/机构关系图谱", body)
    print_json({"run_dir": str(run_dir), "entities_json": str(run_dir / "entities.json"), "graph_json": str(run_dir / "graph.json"), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
