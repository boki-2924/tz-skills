#!/usr/bin/env python3
import argparse
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from istiqra_common import make_run_dir, execute_sql, rows, fetch_embedding_summary, stat_minio, write_json, write_html, print_json, metric_cards


def main():
    parser = argparse.ArgumentParser(description="运行知识库健康巡检。")
    parser.add_argument("--sample", type=int, default=5)
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    run_dir = make_run_dir("knowledge-base-health-audit", "health", args.output_dir)
    table_counts = {}
    for table in ["kb_document", "kb_chunk", "kb_chunk_qa", "kb_embedding_mapping"]:
        table_counts[table] = rows(execute_sql(f"SELECT COUNT(*) AS cnt FROM tz.{table}"))[0]["cnt"]
    embedding_summary = fetch_embedding_summary()
    sample_rows = rows(execute_sql(f"SELECT document_id, md_path_in_minio, pdf_path_in_minio FROM tz.kb_document WHERE deleted_at IS NULL AND md_path_in_minio IS NOT NULL LIMIT {max(1, min(args.sample, 20))}"))
    minio_checks = []
    for row in sample_rows:
        for field in ["md_path_in_minio", "pdf_path_in_minio"]:
            try:
                minio_checks.append({"document_id": row.get("document_id"), "field": field, "ok": True, "stat": stat_minio(row.get(field))})
            except Exception as exc:
                minio_checks.append({"document_id": row.get("document_id"), "field": field, "ok": False, "error": str(exc)})
    score = max(0, 100 - sum(1 for x in minio_checks if not x.get("ok")) * 5)
    health = {"score": score, "table_counts": table_counts, "embedding_summary": embedding_summary, "minio_checks": minio_checks}
    write_json(run_dir / "health.json", health)
    count_rows = "".join(f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>" for k, v in table_counts.items())
    emb_rows = "".join(
        f"<tr><td>{html.escape(str(x.get('embedding_model')))}</td><td>{x.get('embedding_dim')}</td><td>{html.escape(str(x.get('milvus_collection')))}</td><td>{html.escape(str(x.get('status')))}</td><td>{x.get('cnt')}</td></tr>"
        for x in embedding_summary[:20]
    )
    minio_rows = "".join(
        f"<tr><td>{html.escape(str(x.get('document_id'))[:18])}</td><td>{html.escape(str(x.get('field')))}</td><td>{'正常' if x.get('ok') else '异常'}</td><td>{html.escape(str((x.get('stat') or {}).get('size') or x.get('error') or ''))}</td></tr>"
        for x in minio_checks
    )
    preview = run_dir / "previews" / "health.html"
    body = (
        "<section class='hero'><div class='eyebrow'>KNOWLEDGE BASE HEALTH</div><h1>知识库运维巡检</h1><p class='subtitle'>对 Doris 表规模、embedding 映射、Milvus collection、MinIO 对象可达性进行真实巡检。</p></section>"
        + metric_cards([
            ("健康评分", score, "满分 100，MinIO 缺失样本会扣分"),
            ("文档数", table_counts.get("kb_document"), "tz.kb_document"),
            ("Chunk 数", table_counts.get("kb_chunk"), "tz.kb_chunk"),
            ("Embedding 映射", table_counts.get("kb_embedding_mapping"), "tz.kb_embedding_mapping"),
        ])
        + f"<h2>核心表规模</h2><table><tr><th>表</th><th>记录数</th></tr>{count_rows}</table>"
        + f"<h2>Embedding / Milvus 状态</h2><table><tr><th>模型</th><th>维度</th><th>Collection</th><th>状态</th><th>数量</th></tr>{emb_rows}</table>"
        + f"<h2>MinIO 样本对象检查</h2><table><tr><th>文档</th><th>字段</th><th>结果</th><th>大小/错误</th></tr>{minio_rows}</table>"
    )
    write_html(preview, "知识库运维巡检", body)
    print_json({"run_dir": str(run_dir), "health_json": str(run_dir / "health.json"), "preview_html": str(preview), "score": score})


if __name__ == "__main__":
    main()
