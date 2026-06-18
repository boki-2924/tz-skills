#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request


def quote_literal(value):
    return "'" + value.replace("'", "''") + "'"


def validate_identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise ValueError(f"非法标识符: {value}")
    return value


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
    parser = argparse.ArgumentParser(description="查看 Doris/Iceberg 元数据。")
    parser.add_argument("mode", choices=["catalogs", "databases", "tables", "columns"])
    parser.add_argument("--database", default="tz")
    parser.add_argument("--table")
    parser.add_argument("--base-url", default=os.getenv("ISTIQRA_BASE_URL", "http://172.16.0.55:8975"))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    try:
        if args.mode == "catalogs":
            sql = "SHOW CATALOGS"
        elif args.mode == "databases":
            sql = "SHOW DATABASES"
        elif args.mode == "tables":
            db = validate_identifier(args.database)
            sql = f"SHOW TABLES FROM {db}"
        else:
            db_value = quote_literal(args.database)
            sql = (
                "SELECT table_schema, table_name, column_name, data_type "
                "FROM information_schema.columns "
                f"WHERE table_schema = {db_value}"
            )
            if args.table:
                sql += f" AND table_name = {quote_literal(args.table)}"
            sql += " ORDER BY table_name, ordinal_position"
    except ValueError as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    result = post_sql(args.base_url, sql, args.timeout)
    print(json.dumps({"sql": sql, "result": result}, ensure_ascii=False, indent=2))
    return 0 if result.get("code") == 200000 else 1


if __name__ == "__main__":
    sys.exit(main())
