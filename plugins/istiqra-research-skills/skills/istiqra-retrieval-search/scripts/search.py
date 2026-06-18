#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def post_json(url, payload, timeout):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {raw}") from exc


def main():
    parser = argparse.ArgumentParser(description="调用 Istiqra 检索接口。")
    parser.add_argument("query", help="自然语言检索问题或关键词")
    parser.add_argument("--base-url", default=os.getenv("ISTIQRA_BASE_URL", "http://172.16.0.55:8975"))
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-items", type=int, default=10, help="仅在本地截断打印数量，不影响接口召回")
    parser.add_argument("--full", action="store_true", help="打印接口返回的完整 items")
    args = parser.parse_args()

    url = args.base_url.rstrip("/") + "/datonos-istiqra/api/v1/retrieval/search"
    payload = {"query": args.query}
    result = post_json(url, payload, args.timeout)

    if result.get("code") != 200000:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    data = result.get("data") or {}
    items = data.get("items") or []
    if not args.full:
        items = items[: args.max_items]
    output = {
        "query": args.query,
        "total": data.get("total"),
        "recallStats": data.get("recallStats"),
        "items": items,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
