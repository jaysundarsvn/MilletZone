#!/usr/bin/env python3
"""Create a VS Code-friendly, offline content archive of the public Millet Zone Wix site.

This exports publicly rendered content; it cannot export the proprietary Wix editor,
private CMS records, or private form/customer data.

Requires: pip install -r requirements.txt
"""

from __future__ import annotations

import csv
import hashlib
import html as html_lib
import io
import json
import re
import shutil
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree, html
from PIL import Image, ImageOps


BASE_URL = "https://mymilletzone.wixsite.com/siridhanya"
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "export"
MAX_IMAGE_BYTES = 25 * 1024 * 1024
USER_AGENT = "MilletZoneContentArchive/1.0 (public content owner export)"

RECIPE_SLUGS = {
    "rice-with-siri-dhanya", "biryani-and-pulav-with-siri-dhanya",
    "upma-and-pongal-with-siri", "roti-s-with-siri-dhanya",
    "lemon-rice-with-siri-dhanya", "poori-with-siri-dhanya",
    "dosa-with-siri-dhanya", "idly-with-siri-dhanya",
    "spicy-dishes-with-siri-dhanya", "sweets-with-siri-dhanya",
    "whole-grain-bread-with-siri-dhanya", "copy-of-whole-grain-bread-with-siri",
}
PROTOCOL_SLUGS = {"disease-protocols", "disease", "cancer", "kashya"}
HEALTH_SLUGS = PROTOCOL_SLUGS | {"natural-health-tips", "faqs"}


def fetch(url: str, *, timeout: int = 40) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Download failed: {url}: {last_error}")


def clean_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).replace("\u200b", "")
    return re.sub(r"\s+", " ", value).strip()


def page_slug(url: str) -> str:
    path = urllib.parse.urlparse(url).path.rstrip("/")
    return path.rsplit("/", 1)[-1] if path != "/siridhanya" else "home"


def category(slug: str) -> str:
    if slug == "recipes" or slug in RECIPE_SLUGS:
        return "Recipes"
    if slug in PROTOCOL_SLUGS:
        return "Disease protocols"
    return "Core pages"


def image_key(src: str) -> str | None:
    parsed = urllib.parse.urlparse(src)
    if parsed.scheme != "https" or parsed.netloc != "static.wixstatic.com":
        return None
    if not parsed.path.startswith("/media/"):
        return None
    return f"https://{parsed.netloc}{parsed.path.split('/v1/')[0]}"


def image_filename(source_url: str) -> str:
    original = urllib.parse.urlparse(source_url).path.rsplit("/", 1)[-1]
    original = urllib.parse.unquote(original)
    original = re.sub(r"[^a-zA-Z0-9._~-]", "_", original)[:90]
    if not re.search(r"\.(jpg|jpeg|png|gif|webp|svg)$", original, re.I):
        original += ".bin"
    return hashlib.sha256(source_url.encode()).hexdigest()[:10] + "_" + original


def main_content(tree: html.HtmlElement) -> html.HtmlElement:
    matches = tree.xpath('//main[@id="PAGES_CONTAINER"]')
    if not matches:
        raise RuntimeError("Expected Wix main content container not found")
    main = html.fromstring(html.tostring(matches[0]))
    etree.strip_elements(main, "script", "style", "noscript", with_tail=False)
    return main


def extract_blocks(main: html.HtmlElement) -> list[dict]:
    blocks = []
    tags = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "img", "iframe", "blockquote", "tr"}
    for el in main.iter():
        if not isinstance(el.tag, str) or el.tag.lower() not in tags:
            continue
        tag = el.tag.lower()
        ancestors = {a.tag.lower() for a in el.iterancestors() if isinstance(a.tag, str)}
        if tag in {"p", "li", "blockquote"} and (ancestors & {"li", "blockquote"}):
            continue
        if tag == "tr":
            cells = [clean_text(" ".join(c.itertext())) for c in el.xpath("./th|./td")]
            if cells:
                blocks.append({"type": "table-row", "cells": cells})
            continue
        if tag == "img":
            src = el.get("src", "")
            if src:
                blocks.append({"type": "image", "src": src, "asset_key": image_key(src), "alt": el.get("alt", "")})
            continue
        if tag == "iframe":
            src = el.get("src", "")
            if src:
                blocks.append({"type": "embed", "src": src})
            continue
        value = clean_text(" ".join(el.itertext()))
        if value:
            kind = "heading" if tag.startswith("h") else "list-item" if tag == "li" else "paragraph"
            blocks.append({"type": kind, "level": int(tag[1]) if tag.startswith("h") else None, "text": value})
    return blocks


def as_markdown(page: dict, assets: dict) -> str:
    output = [f"# {page['title']}", "", f"Source: {page['url']}", "", f"Captured: {page['captured_at']}", ""]
    for b in page["blocks"]:
        if b["type"] == "heading":
            output += ["#" * min(6, b["level"] + 1) + " " + b["text"], ""]
        elif b["type"] == "paragraph":
            output += [b["text"], ""]
        elif b["type"] == "list-item":
            output += ["- " + b["text"]]
        elif b["type"] == "table-row":
            output += [" | ".join(b["cells"]), ""]
        elif b["type"] == "image":
            key = b["asset_key"]
            path = assets.get(key, {}).get("local_path") if key else None
            target = "../" + path if path else b["src"]
            output += [f"![{b['alt'].replace(']', '')}]({target})", ""]
        elif b["type"] == "embed":
            output += ["Embedded video: " + b["src"], ""]
    if page["links"]:
        output += ["", "## Links found on this page", ""]
        for link in page["links"]:
            output.append(f"- {link['text'] or 'Link'}: {link['url']}")
    return "\n".join(output).strip() + "\n"


def as_offline_page(page: dict, assets: dict) -> str:
    body = []
    for b in page["blocks"]:
        t = b["type"]
        if t == "heading":
            level = min(6, b["level"] + 1)
            body.append(f"<h{level}>{html_lib.escape(b['text'])}</h{level}>")
        elif t == "paragraph":
            body.append(f"<p>{html_lib.escape(b['text'])}</p>")
        elif t == "list-item":
            body.append(f"<p class='list-item'>• {html_lib.escape(b['text'])}</p>")
        elif t == "table-row":
            body.append("<div class='data-row'>" + " · ".join(html_lib.escape(s) for s in b["cells"]) + "</div>")
        elif t == "image":
            key = b["asset_key"]
            path = assets.get(key, {}).get("local_path") if key else None
            if path:
                body.append(f"<figure><img loading='lazy' src='../{html_lib.escape(path, quote=True)}' alt='{html_lib.escape(b['alt'], quote=True)}'></figure>")
            else:
                body.append(f"<p class='missing-image'>Image unavailable in archive: <a href='{html_lib.escape(b['src'], quote=True)}'>original image link</a></p>")
        elif t == "embed":
            body.append(f"<p>Video: <a href='{html_lib.escape(b['src'], quote=True)}' target='_blank' rel='noopener'>Open video</a></p>")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html_lib.escape(page['title'])} | Millet Zone Archive</title>
<link rel="stylesheet" href="../site.css"></head>
<body><div class="shell"><nav><a href="../index.html">← All pages</a><span>Millet Zone · Public content archive</span></nav>
<main><div class="eyebrow">{html_lib.escape(page['category'])}</div><h1>{html_lib.escape(page['title'])}</h1>
<div class="source"><a href="{html_lib.escape(page['url'], quote=True)}">Original Wix page</a> · Snapshot {html_lib.escape(page['captured_at'])}</div>
<article>{''.join(body)}</article></main><footer>Extracted content is archival, not medical advice. Verify health claims and prices before reuse.</footer>
</div></body></html>"""


def csv_write(path: Path, fieldnames: list[str], data: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def write_json(path: Path, content: object) -> None:
    path.write_text(json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def download_image(item: tuple[str, dict]) -> tuple[str, dict]:
    key, details = item
    target = OUTPUT / "media" / details["filename"]
    if target.is_file() and target.stat().st_size:
        return key, {"local_path": f"media/{target.name}", "bytes": target.stat().st_size, "status": "downloaded"}
    errors = []
    for url in [key, details["sample_url"]]:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=45) as response:
                chunks, total = [], 0
                while True:
                    chunk = response.read(256 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_IMAGE_BYTES:
                        raise ValueError("file exceeds 25 MiB safety limit")
                    chunks.append(chunk)
            target.write_bytes(b"".join(chunks))
            return key, {"local_path": f"media/{target.name}", "bytes": total, "status": "downloaded"}
        except Exception as exc:
            errors.append(str(exc))
    return key, {"local_path": None, "bytes": 0, "status": "failed: " + " | ".join(errors)}


def optimize_media(assets: dict) -> None:
    """Shrink large photographs for a practical VS Code ZIP while keeping image IDs."""
    for info in assets.values():
        if info.get("status") != "downloaded":
            continue
        path = OUTPUT / info["local_path"]
        try:
            with Image.open(path) as im:
                if getattr(im, "is_animated", False):
                    continue
                width, height = im.size
                if max(width, height) <= 1800:
                    continue
                adjusted = ImageOps.exif_transpose(im)
                adjusted.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
                ext = path.suffix.lower()
                buffer = io.BytesIO()
                if ext in {".jpg", ".jpeg"}:
                    adjusted.convert("RGB").save(buffer, format="JPEG", quality=82, optimize=True)
                elif ext == ".png":
                    adjusted.save(buffer, format="PNG", optimize=True)
                elif ext == ".webp":
                    adjusted.save(buffer, format="WEBP", quality=82, method=5)
                else:
                    continue
                if buffer.tell() < path.stat().st_size:
                    path.write_bytes(buffer.getvalue())
                    info["bytes"] = path.stat().st_size
        except Exception as exc:
            print(f"  Could not optimize {path.name}: {exc}", flush=True)


CSS = """*{box-sizing:border-box}body{margin:0;background:#f7f8f2;color:#222e23;font:16px/1.7 system-ui,-apple-system,Segoe UI,sans-serif}.shell{max-width:1010px;padding:0 24px;margin:auto}nav{display:flex;justify-content:space-between;gap:16px;padding:24px 0;border-bottom:1px solid #d6dfd3;color:#657165;font-size:14px}a{color:#2d6b47}h1,h2,h3,h4{line-height:1.25;color:#1e442c}h1{font-size:clamp(30px,5vw,48px)}h2{font-size:27px;margin-top:37px}h3{font-size:22px;margin-top:25px}main{padding:35px 0 45px}.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:12px;font-weight:700;color:#55866a}.source{color:#647063;font-size:13px;margin:0 0 32px}article{padding:28px 35px;background:white;border:1px solid #dce3d7;border-radius:15px;overflow-wrap:anywhere}article p{margin:13px 0}article h2{margin-top:30px}article figure{margin:22px 0}article img{display:block;max-width:100%;height:auto;border-radius:8px}.list-item{padding-left:16px}.data-row{border-bottom:1px solid #e6e9e2;padding:8px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-bottom:30px}.card{display:block;text-decoration:none;background:white;padding:18px 20px;border:1px solid #dce3d7;border-radius:12px;color:#27452f}.card:hover{border-color:#6baa78;background:#f4fcf2}.card small{display:block;color:#728172}footer{padding:25px 0 45px;border-top:1px solid #d6dfd3;font-size:13px;color:#68756a}@media(max-width:600px){nav{flex-direction:column;gap:3px}article{padding:18px}.shell{padding:0 15px}}"""


def write_homepage(pages: list[dict]) -> None:
    groups = ["Core pages", "Recipes", "Disease protocols"]
    fragments = []
    for group in groups:
        selected = [p for p in pages if p["category"] == group]
        fragments.append(f"<h2>{group} ({len(selected)})</h2><div class='cards'>")
        for p in selected:
            fragments.append(f"<a class='card' href='pages/{p['slug']}.html'>{html_lib.escape(p['title'])}<small>{html_lib.escape(p['slug'])}</small></a>")
        fragments.append("</div>")
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Millet Zone – Content Archive</title><link rel="stylesheet" href="site.css"></head>
<body><div class="shell"><nav><strong>Millet Zone</strong><span>Offline Wix content archive</span></nav>
<main><div class="eyebrow">Extracted public content</div><h1>Millet Zone · Siridhanya</h1>
<p>Browse {len(pages)} recovered public pages, including products, recipes, and health-related historical website text.</p>
<p class="source">Original: <a href="{BASE_URL}">{BASE_URL}</a> · Open each page without a server.</p>
{''.join(fragments)}</main><footer>Not the original Wix website source code. Medical claims and product prices have not been independently validated.</footer>
</div></body></html>"""
    (OUTPUT / "index.html").write_text(page, encoding="utf-8")


def main() -> None:
    for folder in ["pages", "markdown", "original-html", "data", "media"]:
        (OUTPUT / folder).mkdir(parents=True, exist_ok=True)
    urls_xml = fetch(BASE_URL + "/pages-sitemap.xml")
    (OUTPUT / "original-sitemap.xml").write_bytes(urls_xml)
    sitemap = ET.fromstring(urls_xml)
    urls = [node.text for node in sitemap.findall(".//{*}loc") if node.text]
    print(f"Found {len(urls)} published pages", flush=True)
    assets: dict[str, dict] = {}
    pages: list[dict] = []
    link_rows: list[dict] = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for number, url in enumerate(urls, 1):
        slug = page_slug(url)
        raw = fetch(url)
        (OUTPUT / "original-html" / f"{slug}.html").write_bytes(raw)
        tree = html.fromstring(raw)
        title = clean_text(" ".join(tree.xpath("//title/text()"))) or slug
        description = clean_text(" ".join(tree.xpath('//meta[@name="description"]/@content')))
        main_el = main_content(tree)
        blocks = extract_blocks(main_el)
        all_main_text = "\n".join(clean_text(t) for t in main_el.itertext() if clean_text(t))
        (OUTPUT / "markdown" / f"{slug}.full-text.txt").write_text(all_main_text + "\n", encoding="utf-8")
        links = []
        for anchor in main_el.xpath('.//a[@href]'):
            href = urllib.parse.urljoin(url, anchor.get("href", ""))
            if href.startswith(("https://", "http://", "mailto:", "tel:")):
                label = clean_text(" ".join(anchor.itertext()))
                links.append({"text": label, "url": href})
                link_rows.append({"page": slug, "text": label, "url": href})
        for image in tree.xpath('//img[@src]'):
            src = image.get("src", "")
            key = image_key(src)
            if key:
                if key not in assets:
                    assets[key] = {"filename": image_filename(key), "sample_url": src, "pages": set(), "alt_texts": set()}
                assets[key]["pages"].add(slug)
                if image.get("alt"):
                    assets[key]["alt_texts"].add(clean_text(image.get("alt", "")))
        page = {"slug": slug, "url": url, "title": title, "description": description,
                "category": category(slug), "captured_at": now, "blocks": blocks,
                "full_text": all_main_text, "links": links,
                "images": sorted({b["asset_key"] for b in blocks if b["type"] == "image" and b["asset_key"]}),
                "embedded_videos": [b["src"] for b in blocks if b["type"] == "embed"]}
        pages.append(page)
        print(f"[{number:02}/{len(urls)}] {slug}: {len(all_main_text):,} text characters; {len(page['images'])} page images", flush=True)
        time.sleep(0.2)

    print(f"Downloading {len(assets)} unique Wix images ...", flush=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(download_image, item) for item in assets.items()]
        for index, future in enumerate(as_completed(futures), 1):
            key, result = future.result()
            assets[key].update(result)
            if index % 25 == 0 or index == len(futures):
                print(f"  Media: {index}/{len(futures)}", flush=True)

    print("Optimizing large images for offline use ...", flush=True)
    optimize_media(assets)

    image_manifest = []
    for key, details in sorted(assets.items()):
        image_manifest.append({"original_url": key, "local_path": details.get("local_path"),
                               "status": details.get("status"), "bytes": details.get("bytes", 0),
                               "page_slugs": "; ".join(sorted(details["pages"])),
                               "alt_text": "; ".join(sorted(details["alt_texts"]))})
    for page in pages:
        (OUTPUT / "markdown" / f"{page['slug']}.md").write_text(as_markdown(page, assets), encoding="utf-8")
        (OUTPUT / "pages" / f"{page['slug']}.html").write_text(as_offline_page(page, assets), encoding="utf-8")
    (OUTPUT / "site.css").write_text(CSS, encoding="utf-8")
    write_homepage(pages)
    write_json(OUTPUT / "data" / "pages.json", pages)
    write_json(OUTPUT / "data" / "recipes.json", [p for p in pages if p["slug"] in RECIPE_SLUGS])
    write_json(OUTPUT / "data" / "health-content.json", [p for p in pages if p["slug"] in HEALTH_SLUGS])
    write_json(OUTPUT / "data" / "products.json", next((p for p in pages if p["slug"] == "products"), {}))
    write_json(OUTPUT / "data" / "media-manifest.json", image_manifest)
    csv_write(OUTPUT / "data" / "page-metadata.csv",
              ["slug", "title", "url", "category", "description", "captured_at", "text_characters", "image_count"],
              [{"slug": p["slug"], "title": p["title"], "url": p["url"], "category": p["category"],
                "description": p["description"], "captured_at": p["captured_at"],
                "text_characters": len(p["full_text"]), "image_count": len(p["images"])} for p in pages])
    csv_write(OUTPUT / "data" / "links.csv", ["page", "text", "url"], link_rows)
    csv_write(OUTPUT / "data" / "images.csv", ["original_url", "local_path", "status", "bytes", "page_slugs", "alt_text"], image_manifest)

    successes = sum(asset.get("status") == "downloaded" for asset in assets.values())
    videos = sorted({u for p in pages for u in p["embedded_videos"]})
    report = f"""# Extraction report

Captured UTC: {now}
Site: {BASE_URL}

- Sitemap-listed pages: **{len(urls)}**
- Successfully fetched pages: **{len(pages)}**
- Unique Wix-hosted image URLs: **{len(assets)}**
- Downloaded images: **{successes}**
- Images not downloaded: **{len(assets)-successes}**
- Embedded videos: **{len(videos)}** (links only, not downloaded)
- Full original HTML snapshots included: **{len(pages)}**

## Video URLs

""" + "\n".join(f"- {u}" for u in videos) + "\n\n## Limitations\n\n" + """- The export captures publicly accessible Wix pages; it is not Wix's proprietary site code or database.
- Private CMS records, form submissions, customer data, and unpublished pages require separate authenticated export.
- Media filenames and original links are recorded in `data/images.csv`.
- Page preview is a clean, simple offline reader, not a pixel-identical Wix layout.
- Medical and therapeutic statements are copied from the source, **not verified**. Review before publishing.
- Listed prices are a point-in-time snapshot and may need updating.
"""
    (OUTPUT / "extraction-report.md").write_text(report, encoding="utf-8")
    readme = f"""# Millet Zone — VS Code Content Archive

This is a **downloadable, editable content export** of {BASE_URL}.
It includes {len(pages)} public pages, {successes} downloaded images, markdown, original HTML, and structured JSON/CSV.

## Open it in VS Code

1. Unzip the archive.
2. Open the `millet_zone_vscode` folder using **File → Open Folder** in VS Code.
3. Open `export/index.html` in your browser for a navigable offline preview.
   You can also use the VS Code **Live Server** extension if you already have it installed.
4. Edit `export/pages/*.html` and `export/site.css` for the simple offline presentation.
5. Edit text content in `export/markdown/*.md` or use `export/data/pages.json` in your own website project.

## Archive contents

- `export/index.html` — offline homepage linking to all 26 pages.
- `export/pages/` — simplified readable HTML for each page.
- `export/markdown/` — editable Markdown and full main-body text for each page.
- `export/data/pages.json` — every page's text, headings, images, links, and metadata.
- `export/data/recipes.json` — all 12 individual recipe pages.
- `export/data/products.json` — complete original product-page content in structured blocks.
- `export/data/health-content.json` — disease, FAQ, and health content (unverified source claims).
- `export/data/*.csv` — page, link, and image inventories.
- `export/media/` — successfully downloaded Wix images, resized to at most 1800 pixels on the longest side when beneficial.
- `export/original-html/` — complete original server-returned HTML snapshots.
- `export/extraction-report.md` — exact counts, limitations, and video URLs.

## Regenerate from the current live website

You can rerun the extraction later (requires internet access):

```bash
python -m pip install -r requirements.txt
python extract_wix.py
```

Only content from public pages is included. This is **not a complete export of Wix's proprietary editor,
hosting logic, business database, private forms, or account data**. Original HTML is for preservation,
not a standalone website: the offline preview in `export/` is the portable version.

**Health and copyright notice:** The original website includes health-related treatment claims;
these have not been medically substantiated in this export. Check them, prices, and third-party
media rights before public reuse.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"Complete: {len(pages)} pages, {successes}/{len(assets)} images downloaded", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted; already downloaded media is kept for a later retry.")
