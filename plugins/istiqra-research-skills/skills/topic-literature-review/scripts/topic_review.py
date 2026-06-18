#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, evidence_pack, save_evidence_outputs, corpus_stats, write_json, write_html, bar_table, print_json, metric_cards, evidence_cards, read_text_arg


def main():
    parser = argparse.ArgumentParser(description="生成专题文献综述材料。")
    parser.add_argument("topic", nargs="?")
    parser.add_argument("--topic-file")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    topic = read_text_arg(args.topic, args.topic_file, "专题文献综述")
    run_dir = make_run_dir("topic-literature-review", topic, args.output_dir)
    pack = evidence_pack(topic, limit=args.limit)
    save_evidence_outputs(run_dir, pack, title="专题文献综述证据包")
    stats = corpus_stats(pack["items"])
    themes = list(stats["keywords"].keys())[:8]
    review = {
        "topic": topic,
        "suggested_title": f"{topic}专题文献综述",
        "outline": ["研究背景与问题提出", "既有研究主题分布", "关键证据与代表性文献", "研究不足与后续方向"],
        "themes": themes,
        "evidence_count": len(pack["items"]),
        "writing_note": "本综述材料为基于检索证据的结构化初稿，正式写作前应逐条核验引用。",
    }
    write_json(run_dir / "literature_review.json", review)
    theme_tags = "".join(f"<span class='tag'>{html.escape(t)}</span>" for t in themes)
    outline_html = "".join(f"<li>{html.escape(x)}</li>" for x in review["outline"])
    recall = pack.get("recallStats") or {}
    body = (
        f"<section class='hero'><div class='eyebrow'>TOPIC LITERATURE REVIEW</div><h1>{html.escape(review['suggested_title'])}</h1>"
        f"<p class='subtitle'>基于 Istiqra 真实检索结果生成。页面包含证据候选、主题词、年份与期刊分布，供后续人工写作和引用核验使用。</p></section>"
        + metric_cards([
            ("证据条目", len(pack["items"]), "进入综述材料的候选文献片段"),
            ("总召回", pack.get("total"), "检索接口返回总量"),
            ("向量召回", recall.get("vectorCount", 0), "vectorCount"),
            ("全文召回", recall.get("fullTextCount", 0), "fullTextCount"),
        ])
        + f"<div class='grid'><section class='card'><h2>主题线索</h2>{theme_tags}</section><section class='card'><h2>建议综述结构</h2><ol>{outline_html}</ol></section></div>"
        + bar_table("年份分布", stats["years"])
        + bar_table("期刊分布", stats["journals"])
        + "<h2>核心证据卡片</h2>"
        + evidence_cards(pack["items"], limit=12)
    )
    preview = run_dir / "previews" / "index.html"
    write_html(preview, "专题文献综述", body)
    print_json({"run_dir": str(run_dir), "review_json": str(run_dir / "literature_review.json"), "evidence_json": str(run_dir / "evidence.json"), "answer_context": str(run_dir / "answer_context.md"), "preview_html": str(preview)})


if __name__ == "__main__":
    main()
