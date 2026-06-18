#!/usr/bin/env python3
import argparse
import json
import os
import sys


def bool_env(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def main():
    parser = argparse.ArgumentParser(description="读取 MinIO 对象。")
    parser.add_argument("--key", required=True, help="bucket 内对象路径")
    parser.add_argument("--output", help="保存到本地文件；不设置时只打印预览")
    parser.add_argument("--stat-only", action="store_true", help="只查看对象元数据")
    parser.add_argument("--preview-bytes", type=int, default=1000)
    args = parser.parse_args()

    try:
        from minio import Minio
    except ImportError:
        print(json.dumps({"success": False, "error": "缺少 minio 包，请先安装: pip install minio"}, ensure_ascii=False, indent=2))
        return 2

    endpoint = os.getenv("MINIO_ENDPOINT", "192.168.0.171:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    bucket = os.getenv("MINIO_BUCKET", "tongzhan")
    secure = bool_env(os.getenv("MINIO_SECURE", "false"))

    if not access_key or not secret_key:
        print(json.dumps({"success": False, "error": "请设置 MINIO_ACCESS_KEY 和 MINIO_SECRET_KEY"}, ensure_ascii=False, indent=2))
        return 2

    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
    stat = client.stat_object(bucket, args.key)
    stat_payload = {
        "bucket": bucket,
        "key": args.key,
        "size": stat.size,
        "content_type": stat.content_type,
        "last_modified": stat.last_modified.isoformat() if stat.last_modified else None,
    }

    if args.stat_only:
        print(json.dumps({"success": True, "stat": stat_payload}, ensure_ascii=False, indent=2))
        return 0

    response = client.get_object(bucket, args.key)
    try:
        if args.output:
            with open(args.output, "wb") as f:
                for chunk in response.stream(1024 * 1024):
                    f.write(chunk)
            print(json.dumps({"success": True, "stat": stat_payload, "saved_to": args.output}, ensure_ascii=False, indent=2))
        else:
            data = response.read(max(1, args.preview_bytes))
            preview = data.decode("utf-8", errors="replace")
            print(json.dumps({"success": True, "stat": stat_payload, "preview": preview}, ensure_ascii=False, indent=2))
    finally:
        response.close()
        response.release_conn()
    return 0


if __name__ == "__main__":
    sys.exit(main())
