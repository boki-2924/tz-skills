#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


FIELDS = [
    "chunk_id", "document_id", "chunk_index", "page_num", "chunk_content",
    "abstract", "char_count", "language", "bbox_list", "extra_meta",
    "created_at", "updated_at",
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
    parser = argparse.ArgumentParser(description="查询 tz.kb_chunk 分块内容。")
    parser.add_argument("--document-id")
    parser.add_argument("--chunk-id")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--base-url", default=os.getenv("ISTIQRA_BASE_URL", "http://172.16.0.55:8975"))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    conditions = ["deleted_at IS NULL"]
    if args.document_id:
        conditions.append(f"document_id = {quote_literal(args.document_id)}")
    if args.chunk_id:
        conditions.append(f"chunk_id = {quote_literal(args.chunk_id)}")
    if len(conditions) == 1:
        print(json.dumps({"success": False, "error": "至少提供 document-id 或 chunk-id"}, ensure_ascii=False, indent=2))
        return 2

    limit = max(1, min(args.limit, 100))
    sql = (
        f"SELECT {', '.join(FIELDS)} FROM tz.kb_chunk "
        f"WHERE {' AND '.join(conditions)} "
        "ORDER BY chunk_index ASC "
        f"LIMIT {limit}"
    )
    result = post_sql(args.base_url, sql, args.timeout)
    print(json.dumps({"sql": sql, "result": result}, ensure_ascii=False, indent=2))
    return 0 if result.get("code") == 200000 else 1


if __name__ == "__main__":
    sys.exit(main())
