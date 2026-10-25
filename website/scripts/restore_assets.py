"""Recover the archived site's recorded images without introducing new sources.

Usage: python website/scripts/restore_assets.py
Requires Pillow. Sources are used exactly as recorded in media-manifest.json.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
import hashlib
import json
import re
import urllib.request

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'millet_zone_vscode/export/data/media-manifest.json'
ASSETS = ROOT / 'website/assets/images'
MAP = ROOT / 'website/assets/asset-map.json'
ASSETS.mkdir(parents=True, exist_ok=True)
(ASSETS / 'thumbs').mkdir(exist_ok=True)


def thumbnail(image, filename, record):
    """Supply a light card image while keeping the larger image available."""
    if max(image.size) <= 640:
        record.update(thumbnail=record['file'], thumbnail_width=image.width,
                      thumbnail_height=image.height)
        return
    preview = image.copy()
    preview.thumbnail((640, 640), Image.Resampling.LANCZOS)
    preview.save(ASSETS / 'thumbs' / filename, 'WEBP', quality=80, method=6)
    record.update(thumbnail=f'assets/images/thumbs/{filename}',
                  thumbnail_width=preview.width, thumbnail_height=preview.height)


def recover(item):
    url = item['original_url']
    key = item.get('local_path') or url
    pages = [p.strip() for p in item['page_slugs'].split(';')]
    identifier = (Path(item['local_path']).name.split('_')[0]
                  if item.get('local_path') else hashlib.sha256(url.encode()).hexdigest()[:10])
    filename = f'{pages[0]}-{identifier}.webp'
    record = dict(file=f'assets/images/{filename}', original_url=url,
                  archive_path=item.get('local_path'), alt=item.get('alt_text', ''),
                  page_slugs=pages)
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=35) as response:
            data = response.read()
        with Image.open(BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source)
            original_width, original_height = image.size
            # Screenshot and medical reference charts retain their original
            # dimensions so text stays readable. Photography is capped at 1600px.
            chart = bool(re.search(r'screen\s*shot|cancer|chart|protocol|table',
                                   record['alt'], re.I))
            if not chart:
                image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGBA' if 'transparency' in image.info else 'RGB')
            image.save(ASSETS / filename, 'WEBP', quality=90 if chart else 84,
                       method=6, lossless=chart)
            record.update(width=image.width, height=image.height,
                          original_width=original_width, original_height=original_height,
                          bytes=(ASSETS / filename).stat().st_size, status='recovered')
            thumbnail(image, filename, record)
    except Exception as error:
        record.update(file=None, status='unavailable', error=str(error))
    return key, record


def main():
    items = json.loads(MANIFEST.read_text(encoding='utf-8'))
    excluded = re.compile(r'twitter|facebook|instagram|tripadvisor', re.I)
    items = [item for item in items
             if item['page_slugs'].strip() != 'order'
             and not excluded.search(item.get('alt_text', ''))
             and not (item['page_slugs'].strip() == 'links'
                      and '7103ae_' not in item['original_url'])]
    result = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(recover, item) for item in items]
        for future in as_completed(futures):
            key, record = future.result()
            result[key] = record
            print(record['status'], record['file'] or record['original_url'], flush=True)
    MAP.write_text(json.dumps(dict(sorted(result.items())), indent=2,
                              ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Recovered {sum(r["status"] == "recovered" for r in result.values())}/{len(result)} images')


if __name__ == '__main__':
    main()
