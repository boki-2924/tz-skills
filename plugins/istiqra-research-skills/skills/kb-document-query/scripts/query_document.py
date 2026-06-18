#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


FIELDS = [
    "document_id", "title", "author", "journal_name", "publish_year", "publish_time",
    "file_abstract", "file_keyword", "clc_label_paths", "minio_bucket",
    "pdf_path_in_minio", "md_path_in_minio", "chunk_json_path_in_minio",
    "layout_json_path_in_minio", "object_prefix_in_minio", "parser_version",
    "chunking_version", "status", "created_at", "updated_at",
]


def quote_literal(value):
    return "'" + value.replace("'", "''") + "'"


def post_sql(base_url, sql, timeout):
    url = base_url.rstrip("/") + "/datonos-istiqra/api/doris/iceberg/execute"
    data = json.dumps({"sql": sql}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {raw}") from exc


def main():
    parser = argparse.ArgumentParser(description="查询 tz.kb_document 文档元数据。")
    parser.add_argument("--document-id")
    parser.add_argument("--title-like")
    parser.add_argument("--publish-year")
    parser.add_argument("--journal-like")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--base-url", default=os.getenv("ISTIQRA_BASE_URL", "http://172.16.0.55:8975"))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    conditions = ["deleted_at IS NULL"]
    if args.document_id:
        conditions.append(f"document_id = {quote_literal(args.document_id)}")
    if args.title_like:
        conditions.append(f"title LIKE {quote_literal('%' + args.title_like + '%')}")
    if args.publish_year:
        conditions.append(f"publish_year = {quote_literal(args.publish_year)}")
    if args.journal_like:
        conditions.append(f"journal_name LIKE {quote_literal('%' + args.journal_like + '%')}")
    if len(conditions) == 1:
        print(json.dumps({"success": False, "error": "至少提供一个过滤条件"}, ensure_ascii=False, indent=2))
        return 2

    limit = max(1, min(args.limit, 100))
    sql = (
        f"SELECT {', '.join(FIELDS)} FROM tz.kb_document "
        f"WHERE {' AND '.join(conditions)} "
        "ORDER BY updated_at DESC "
        f"LIMIT {limit}"
    )
    result = post_sql(args.base_url, sql, args.timeout)
    print(json.dumps({"sql": sql, "result": result}, ensure_ascii=False, indent=2))
    return 0 if result.get("code") == 200000 else 1


if __name__ == "__main__":
    sys.exit(main())
