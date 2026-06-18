#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request


ALLOWED_PREFIXES = ("select", "show", "desc", "describe", "explain")
DENIED_WORDS = {
    "insert", "update", "delete", "drop", "alter", "create", "truncate",
    "merge", "call", "grant", "revoke", "replace", "load", "copy",
}


def validate_readonly(sql):
    compact = sql.strip().strip(";").strip()
    if not compact:
        raise ValueError("SQL 不能为空")
    first = compact.split(None, 1)[0].lower()
    if first not in ALLOWED_PREFIXES:
        raise ValueError(f"只允许只读 SQL，当前开头是 {first!r}")
    tokens = set(re.findall(r"[a-zA-Z_]+", compact.lower()))
    denied = sorted(tokens & DENIED_WORDS)
    if denied:
        raise ValueError(f"SQL 包含禁止词: {', '.join(denied)}")
    return compact


def post_json(url, payload, timeout):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {raw}") from exc


def main():
    parser = argparse.ArgumentParser(description="执行 Doris/Iceberg 只读 SQL。")
    parser.add_argument("sql", help="只读 SQL")
    parser.add_argument("--base-url", default=os.getenv("ISTIQRA_BASE_URL", "http://172.16.0.55:8975"))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    try:
        sql = validate_readonly(args.sql)
    except ValueError as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    url = args.base_url.rstrip("/") + "/datonos-istiqra/api/doris/iceberg/execute"
    result = post_json(url, {"sql": sql}, args.timeout)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("code") == 200000 else 1


if __name__ == "__main__":
    sys.exit(main())
