from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "http://172.16.0.55:8975"
DEFAULT_BUCKET = "tongzhan"


def slugify(value: str, fallback: str = "run", max_len: int = 80) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", str(value), flags=re.UNICODE).strip("._")
    text = re.sub(r"_+", "_", text)
    return (text or fallback)[:max_len]


def make_run_dir(kind: str, title: str, base_dir: str | None = None) -> Path:
    root = Path(base_dir) if base_dir else PLUGIN_ROOT / "runs" / kind
    path = root / f"{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}_{slugify(title, kind, 48)}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def quote_literal(value: Any) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def post_json(url: str, payload: dict[str, Any], timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {raw}") from exc


def base_url() -> str:
    return os.getenv("ISTIQRA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def search(query: str, timeout: int = 30) -> dict[str, Any]:
    url = base_url() + "/datonos-istiqra/api/v1/retrieval/search"
    return post_json(url, {"query": query}, timeout=timeout)


def execute_sql(sql: str, timeout: int = 30) -> dict[str, Any]:
    url = base_url() + "/datonos-istiqra/api/doris/iceberg/execute"
    return post_json(url, {"sql": sql}, timeout=timeout)


def rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    data = result.get("data")
    return data if isinstance(data, list) else []


def normalize_items(search_result: dict[str, Any], limit: int = 20) -> list[dict[str, Any]]:
    data = search_result.get("data") or {}
    raw_items = data.get("items") or []
    items: list[dict[str, Any]] = []
    for index, item in enumerate(raw_items[:limit], 1):
        chunk = item.get("chunk") or {}
        items.append({
            "rank": index,
            "documentId": item.get("documentId") or chunk.get("documentId"),
            "title": item.get("title") or "",
            "authors": item.get("authors") or [],
            "journalName": item.get("journalName"),
            "publishYear": item.get("publishYear"),
            "publishTime": item.get("publishTime"),
            "chunkId": chunk.get("chunkId"),
            "chunkIndex": chunk.get("chunkIndex"),
            "pageNum": chunk.get("pageNum"),
            "chunkContent": chunk.get("chunkContent") or "",
            "abstractText": chunk.get("abstractText") or "",
            "bboxList": chunk.get("bboxList"),
            "extraMeta": chunk.get("extraMeta"),
            "pdfUrl": item.get("pdfUrl"),
            "markdownUrl": item.get("markdownUrl"),
            "recallType": item.get("recallType"),
            "score": item.get("score"),
        })
    return items


def evidence_pack(query: str, limit: int = 10) -> dict[str, Any]:
    raw = search(query)
    items = normalize_items(raw, limit=limit)
    return {
        "query": query,
        "total": (raw.get("data") or {}).get("total"),
        "recallStats": (raw.get("data") or {}).get("recallStats"),
        "items": items,
    }


def fetch_documents(document_ids: list[str]) -> list[dict[str, Any]]:
    ids = [doc for doc in dict.fromkeys(document_ids) if doc]
    if not ids:
        return []
    sql = (
        "SELECT document_id, title, author, author_org, journal_name, publish_year, "
        "clc_label_paths, file_keyword, minio_bucket, pdf_path_in_minio, md_path_in_minio, "
        "parser_version, chunking_version, status "
        "FROM tz.kb_document WHERE deleted_at IS NULL AND document_id IN "
        + "(" + ", ".join(quote_literal(x) for x in ids) + ")"
    )
    return rows(execute_sql(sql))


def fetch_chunks(document_id: str, limit: int = 20) -> list[dict[str, Any]]:
    sql = (
        "SELECT chunk_id, document_id, chunk_index, page_num, chunk_content, abstract, "
        "char_count, language, bbox_list, extra_meta FROM tz.kb_chunk "
        f"WHERE deleted_at IS NULL AND document_id = {quote_literal(document_id)} "
        f"ORDER BY chunk_index ASC LIMIT {max(1, min(limit, 100))}"
    )
    return rows(execute_sql(sql))


def fetch_embedding_summary() -> list[dict[str, Any]]:
    sql = (
        "SELECT embedding_model, embedding_dim, milvus_collection, status, COUNT(*) AS cnt "
        "FROM tz.kb_embedding_mapping WHERE deleted_at IS NULL "
        "GROUP BY embedding_model, embedding_dim, milvus_collection, status "
        "ORDER BY cnt DESC LIMIT 100"
    )
    return rows(execute_sql(sql))


def parse_jsonish(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except Exception:
        return value


def split_people(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        raw = value
    else:
        parsed = parse_jsonish(value)
        raw = parsed if isinstance(parsed, list) else re.split(r"[,，;；、\s]+", str(value))
    people: list[str] = []
    for item in raw:
        text = str(item).strip().strip("{}[]\"' ")
        if text and text.lower() not in {"null", "none"}:
            people.append(text)
    return people


def extract_keywords(*values: Any, limit: int = 20) -> list[str]:
    counter: Counter[str] = Counter()
    for value in values:
        parsed = parse_jsonish(value)
        if isinstance(parsed, dict):
            candidates = parsed.get("keywords") or parsed.get("keyword") or parsed.values()
        elif isinstance(parsed, list):
            candidates = parsed
        else:
            candidates = re.split(r"[,，;；、\s]+", str(value or ""))
        for item in candidates:
            text = str(item).strip().strip("{}[]\"' ")
            if 2 <= len(text) <= 30:
                counter[text] += 1
    return [x for x, _ in counter.most_common(limit)]


def corpus_stats(items: list[dict[str, Any]]) -> dict[str, Any]:
    years = Counter(str(x.get("publishYear") or "未知") for x in items)
    journals = Counter(str(x.get("journalName") or "未知") for x in items)
    authors: Counter[str] = Counter()
    keywords: Counter[str] = Counter()
    for item in items:
        for author in split_people(item.get("authors")):
            authors[author] += 1
        for keyword in extract_keywords(item.get("extraMeta"), item.get("title"), limit=8):
            keywords[keyword] += 1
    return {
        "years": dict(years.most_common()),
        "journals": dict(journals.most_common(20)),
        "authors": dict(authors.most_common(30)),
        "keywords": dict(keywords.most_common(30)),
    }


def html_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#eef3f8;color:#182230;font:14px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif}}
main{{max-width:1220px;margin:0 auto;padding:28px 28px 56px}}
h1{{font-size:30px;line-height:1.2;margin:0}} h2{{font-size:20px;margin:30px 0 14px}} h3{{font-size:16px;margin:0 0 8px}} a{{color:#2563eb}}
.hero{{display:grid;gap:14px;margin-bottom:18px;padding:26px 28px;border-radius:8px;background:#fff;border:1px solid #dce6f2;box-shadow:0 18px 48px rgba(15,23,42,.08)}}
.eyebrow{{font-size:12px;font-weight:800;letter-spacing:.14em;color:#426086;text-transform:uppercase}} .subtitle{{max-width:860px;color:#5f6f85;font-size:15px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}} .grid.tight{{grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}}
.card{{background:#fff;border:1px solid #dbe5f2;border-radius:8px;padding:16px;box-shadow:0 12px 32px rgba(15,23,42,.06)}}
.metric{{display:grid;gap:4px}} .metric b{{font-size:26px;line-height:1.1}} .metric span{{color:#667085}}
.muted{{color:#667085}} .tag{{display:inline-block;margin:3px 6px 3px 0;padding:3px 10px;border-radius:999px;background:#eef5ff;color:#1d4ed8;border:1px solid #d7e7ff}}
table{{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid #dbe5f2;border-radius:8px;overflow:hidden}} th,td{{border-bottom:1px solid #e8eef6;padding:10px;vertical-align:top}} tr:last-child td{{border-bottom:0}} th{{background:#f4f7fb;color:#334155;font-weight:750}}
.bar-track{{height:10px;background:#e8eef6;border-radius:999px;overflow:hidden}} .bar{{height:10px;background:linear-gradient(90deg,#2563eb,#22c55e);border-radius:999px}}
.node{{display:inline-flex;align-items:center;gap:4px;margin:5px;padding:7px 10px;border:1px solid #bfdbfe;border-radius:999px;background:#fff;color:#1f3b64}}
.evidence-card{{display:grid;gap:8px;border-left:4px solid #2563eb}} .evidence-id{{font-weight:800;color:#2563eb}} .snippet{{background:#f8fafc;border:1px solid #e5eaf2;border-radius:8px;padding:10px;color:#334155}}
.svg-wrap{{background:#fff;border:1px solid #dbe5f2;border-radius:8px;padding:12px;overflow:auto;box-shadow:0 12px 32px rgba(15,23,42,.05)}} svg text{{font-family:"Microsoft YaHei",Arial,sans-serif}}
pre{{white-space:pre-wrap;background:#111827;color:#f9fafb;padding:12px;border-radius:8px;overflow:auto}}
@media (max-width:760px){{main{{padding:18px}} .hero{{padding:20px}} h1{{font-size:24px}}}}
</style></head><body><main>{body}</main></body></html>"""


def write_html(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_page(title, body), encoding="utf-8")


def bar_table(title: str, values: dict[str, Any], limit: int = 20) -> str:
    pairs = list(values.items())[:limit]
    max_value = max([int(v) for _, v in pairs] or [1])
    rows_html = []
    for key, value in pairs:
        width = max(4, int(int(value) / max_value * 100))
        rows_html.append(f"<tr><td>{html.escape(str(key))}</td><td>{value}</td><td><div class='bar-track'><div class='bar' style='width:{width}%'></div></div></td></tr>")
    return f"<h2>{html.escape(title)}</h2><table><tr><th>名称</th><th>数量</th><th>分布</th></tr>{''.join(rows_html)}</table>"


def metric_cards(metrics: list[tuple[str, Any, str]]) -> str:
    return "<div class='grid tight'>" + "".join(
        f"<div class='card metric'><span>{html.escape(label)}</span><b>{html.escape(str(value))}</b><small class='muted'>{html.escape(note)}</small></div>"
        for label, value, note in metrics
    ) + "</div>"


def evidence_cards(items: list[dict[str, Any]], limit: int = 8) -> str:
    cards = []
    for item in items[:limit]:
        rank = int(item.get("rank") or 0)
        title = html.escape(str(item.get("title") or "未命名文献"))
        meta = " / ".join(str(x) for x in [item.get("journalName"), item.get("publishYear"), item.get("recallType")] if x)
        snippet = html.escape(str(item.get("chunkContent") or item.get("abstractText") or "")[:420])
        cards.append(
            f"<article class='card evidence-card'><div><span class='evidence-id'>E{rank:02d}</span> <strong>{title}</strong></div>"
            f"<div class='muted'>{html.escape(meta)}</div><div class='snippet'>{snippet}</div></article>"
        )
    return "<div class='grid'>" + "".join(cards) + "</div>"


def read_text_arg(value: str | None, file_value: str | None, fallback: str = "") -> str:
    if file_value:
        return Path(file_value).read_text(encoding="utf-8").strip()
    return (value or fallback).strip()


def evidence_table(items: list[dict[str, Any]]) -> str:
    rows_html = []
    for item in items:
        rows_html.append(
            "<tr>"
            f"<td>E{int(item.get('rank') or 0):02d}</td>"
            f"<td>{html.escape(str(item.get('title') or ''))}</td>"
            f"<td>{html.escape(str(item.get('journalName') or ''))}</td>"
            f"<td>{html.escape(str(item.get('publishYear') or ''))}</td>"
            f"<td>{html.escape(str(item.get('chunkContent') or item.get('abstractText') or ''))[:260]}</td>"
            "</tr>"
        )
    return "<table><tr><th>编号</th><th>题名</th><th>期刊</th><th>年份</th><th>证据片段</th></tr>" + "".join(rows_html) + "</table>"


def write_answer_context(path: Path, query: str, items: list[dict[str, Any]]) -> None:
    lines = [f"# 证据上下文\n\n问题：{query}\n\n"]
    for item in items:
        lines.append(
            f"## [E{int(item.get('rank') or 0):02d}] {item.get('title')}\n"
            f"- 文档ID：`{item.get('documentId')}`\n"
            f"- ChunkID：`{item.get('chunkId')}`\n"
            f"- 年份：{item.get('publishYear')}\n"
            f"- 期刊：{item.get('journalName')}\n"
            f"- Markdown：`{item.get('markdownUrl')}`\n"
            f"- PDF：`{item.get('pdfUrl')}`\n\n"
            f"{item.get('chunkContent') or item.get('abstractText') or ''}\n\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def save_evidence_outputs(run_dir: Path, pack: dict[str, Any], title: str = "证据包") -> dict[str, str]:
    items = pack.get("items") or []
    write_json(run_dir / "evidence.json", pack)
    write_answer_context(run_dir / "answer_context.md", pack.get("query") or "", items)
    stats = corpus_stats(items)
    body = (
        f"<h1>{html.escape(title)}</h1><p class='muted'>问题：{html.escape(str(pack.get('query') or ''))}</p>"
        f"<div class='grid'><div class='card'>总数：{pack.get('total')}</div><div class='card'>召回统计：<pre>{html.escape(json.dumps(pack.get('recallStats'), ensure_ascii=False, indent=2))}</pre></div></div>"
        + bar_table("年份分布", stats["years"])
        + bar_table("期刊分布", stats["journals"])
        + bar_table("关键词", stats["keywords"])
        + "<h2>证据列表</h2>"
        + evidence_table(items)
    )
    preview = run_dir / "previews" / "index.html"
    write_html(preview, title, body)
    return {
        "run_dir": str(run_dir),
        "evidence_json": str(run_dir / "evidence.json"),
        "answer_context": str(run_dir / "answer_context.md"),
        "preview_html": str(preview),
    }


def minio_client():
    try:
        from minio import Minio
    except ImportError as exc:
        raise RuntimeError("缺少 minio 包，请安装 minio") from exc
    endpoint = os.getenv("MINIO_ENDPOINT", "192.168.0.171:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY") or os.getenv("RETRIEVAL_MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY") or os.getenv("RETRIEVAL_MINIO_SECRET_KEY")
    if not access_key or not secret_key:
        raise RuntimeError("请先设置 MINIO_ACCESS_KEY 和 MINIO_SECRET_KEY")
    secure = str(os.getenv("MINIO_SECURE", "false")).lower() in {"1", "true", "yes"}
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def stat_minio(key: str, bucket: str | None = None) -> dict[str, Any]:
    client = minio_client()
    target_bucket = bucket or os.getenv("MINIO_BUCKET", DEFAULT_BUCKET)
    st = client.stat_object(target_bucket, key)
    return {"bucket": target_bucket, "key": key, "size": st.size, "content_type": st.content_type}


def render_citation_preview(query: str, run_dir: Path, top_k: int = 3) -> dict[str, Any]:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("缺少 PyMuPDF/fitz，无法渲染 PDF bbox 预览") from exc
    client = minio_client()
    pack = evidence_pack(query, limit=max(1, top_k))
    selected = []
    for item in pack["items"][:top_k]:
        key = item.get("pdfUrl")
        if not key:
            continue
        pdf_path = run_dir / "pdfs" / f"E{int(item['rank']):02d}.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        obj = client.get_object(os.getenv("MINIO_BUCKET", DEFAULT_BUCKET), key)
        try:
            pdf_path.write_bytes(obj.read())
        finally:
            obj.close()
            obj.release_conn()
        page_no = 1
        page_nums = item.get("pageNum")
        if isinstance(page_nums, list) and page_nums:
            try:
                page_no = max(1, int(page_nums[0]))
            except Exception:
                page_no = 1
        image_path = run_dir / "previews" / "images" / f"E{int(item['rank']):02d}_page_{page_no}.png"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        doc = fitz.open(str(pdf_path))
        try:
            page = doc.load_page(page_no - 1)
            pix = page.get_pixmap(dpi=160, alpha=False)
            pix.save(str(image_path))
            coord_w, coord_h = pix.width, pix.height
        finally:
            doc.close()
        bboxes = parse_jsonish(item.get("bboxList")) or []
        rects = []
        if isinstance(bboxes, list):
            for box in bboxes:
                raw = box.get("bbox") if isinstance(box, dict) else box
                if isinstance(raw, list) and len(raw) >= 4:
                    x0, y0, x1, y1 = [float(x) for x in raw[:4]]
                    rects.append((x0, y0, max(1, x1 - x0), max(1, y1 - y0)))
        rect_html = "".join(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='3'></rect>" for x, y, w, h in rects)
        body = (
            f"<h1>[E{int(item['rank']):02d}] {html.escape(str(item.get('title') or ''))}</h1>"
            f"<p class='muted'>Document: {html.escape(str(item.get('documentId')))} | Chunk: {html.escape(str(item.get('chunkId')))}</p>"
            f"<div style='position:relative;max-width:100%;width:{coord_w}px;aspect-ratio:{coord_w}/{coord_h};background:white;box-shadow:0 10px 30px rgba(0,0,0,.12)'>"
            f"<img src='images/{image_path.name}' style='position:absolute;inset:0;width:100%;height:100%'>"
            f"<svg viewBox='0 0 {coord_w} {coord_h}' preserveAspectRatio='none' style='position:absolute;inset:0;width:100%;height:100%'>{rect_html}</svg></div>"
            f"<pre>{html.escape(str(item.get('chunkContent') or item.get('abstractText') or ''))}</pre>"
        )
        html_path = run_dir / "previews" / f"E{int(item['rank']):02d}.html"
        write_html(html_path, str(item.get("title") or "证据预览"), body)
        item["html_preview"] = str(html_path)
        item["page_image"] = str(image_path)
        selected.append(item)
    index_body = "<h1>引用预览</h1><ol>" + "".join(
        f"<li><a href='E{int(item['rank']):02d}.html'>E{int(item['rank']):02d} {html.escape(str(item.get('title') or ''))}</a></li>"
        for item in selected
    ) + "</ol>"
    index = run_dir / "previews" / "preview.html"
    write_html(index, "引用预览", index_body)
    write_json(run_dir / "citation_preview.json", {"query": query, "evidence": selected})
    return {"preview_index": str(index), "count": len(selected)}


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-dir", help="输出目录，默认写入插件 runs/ 下")
    parser.add_argument("--limit", type=int, default=10)
