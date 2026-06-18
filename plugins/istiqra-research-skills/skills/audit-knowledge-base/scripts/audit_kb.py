#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, execute_sql, rows, fetch_embedding_summary, stat_minio, write_json, write_html, print_json


def main():
    parser = argparse.ArgumentParser(description="巡检知识库。")
    parser.add_argument("--sample", type=int, default=5)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    tables = ["kb_document", "kb_chunk", "kb_chunk_qa", "kb_embedding_mapping"]
    counts = {}
    for table in tables:
        counts[table] = rows(execute_sql(f"SELECT COUNT(*) AS cnt FROM tz.{table}"))[0]["cnt"]
    embedding = fetch_embedding_summary()
    sample_sql = f"SELECT document_id, md_path_in_minio, pdf_path_in_minio FROM tz.kb_document WHERE deleted_at IS NULL AND md_path_in_minio IS NOT NULL LIMIT {max(1, min(args.sample, 20))}"
    samples = rows(execute_sql(sample_sql))
    minio_checks = []
    for row in samples:
        for field in ["md_path_in_minio", "pdf_path_in_minio"]:
            key = row.get(field)
            if not key:
                continue
            try:
                stat = stat_minio(key)
                minio_checks.append({"document_id": row.get("document_id"), "field": field, "ok": True, "stat": stat})
            except Exception as exc:
                minio_checks.append({"document_id": row.get("document_id"), "field": field, "ok": False, "error": str(exc)})
    score = 100
    score -= sum(1 for x in minio_checks if not x.get("ok")) * 5
    health = {"score": max(0, score), "table_counts": counts, "embedding_summary": embedding, "minio_checks": minio_checks}
    run_dir = make_run_dir("kb-audit", "health", args.output_dir)
    write_json(run_dir / "health.json", health)
    cards = "".join(f"<div class='card'><h2>{html.escape(str(k))}</h2><pre>{html.escape(str(v))}</pre></div>" for k, v in health.items())
    preview = run_dir / "previews" / "health.html"
    write_html(preview, "知识库巡检", f"<h1>知识库巡检</h1><div class='card'><h2>健康评分：{health['score']}</h2></div><div class='grid'>{cards}</div>")
    print_json({"run_dir": str(run_dir), "health_json": str(run_dir / "health.json"), "preview_html": str(preview), "score": health["score"]})


if __name__ == "__main__":
    main()
