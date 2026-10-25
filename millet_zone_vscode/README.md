# Millet Zone — VS Code Content Archive

This is a **downloadable, editable content export** of https://mymilletzone.wixsite.com/siridhanya.
It includes 26 public pages, 151 downloaded images, markdown, original HTML, and structured JSON/CSV.

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
