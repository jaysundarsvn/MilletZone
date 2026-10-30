# Millet Zone website

A responsive, static informational website for **https://milletszone.com**. The supplied Millet Zone archive is the factual source; the Framer reference informs the visual design only. The website has no shopping, checkout, account system, database, or runtime framework dependency.

## Run locally

Open this `website` folder in Visual Studio Code. Use Python 3.10 or later. In its terminal, run:

```powershell
python build.py
python scripts/validate.py
python -m http.server 4173 --bind 127.0.0.1 --directory dist
```

Visit **http://127.0.0.1:4173/**. Press `Ctrl+C` in the terminal to stop the server. If your Windows installation exposes Python as `py`, use `py` in place of `python`.

Run the build again after editing source files, then refresh the browser. The build and validator use Python's standard library. All pages, styles, scripts, and images are served as static files.

## Edit the website

- [build.py](./build.py) generates the shared header and footer, home page, millet guide, recipe index and recipe pages, knowledge pages, about page, contact page, and FAQs.
- [content.json](./content.json) contains the prepared source content. Preserve valid JSON when editing it.
- [CONTENT-NOTES.md](./CONTENT-NOTES.md) records the page-by-page migration, exclusions, and incomplete or inconsistent source material.
- [styles.css](./styles.css) defines the yellow, red, green, and white design, page layouts, and responsive styling.
- [app.js](./app.js) provides browser interactions.
- [carousel.css](./carousel.css) styles the responsive recipe carousel. It supports native touch scrolling, navigation arrows, and keyboard controls without autoplay.
- [refinements.css](./refinements.css) contains the logo, compact grain layouts, reading sections, and book inquiry styles.
- [content_rendering.py](./content_rendering.py) groups the original source blocks into complete grain, FAQ, community, plant, and learning-resource entries.
- [assets/millet-zone-logo.png](./assets/millet-zone-logo.png) is the user-supplied logo, used unchanged in the header and footer.
- [assets/images](./assets/images/) contains the restored, optimized images from the supplied archive.
- [assets/asset-map.json](./assets/asset-map.json) records image provenance and local image paths.
- [scripts/validate.py](./scripts/validate.py) checks generated HTML for broken local links, assets and anchor targets, duplicate IDs, a single main heading, image alt attributes, canonical URLs, unresolved placeholders, and excluded purchase routes and controls.
- [dist](./dist/) is the generated deployment output. Make permanent changes in source files and rebuild, rather than editing this output directly.

The supplied [content archive](../millet_zone_vscode/) is retained separately for source comparison. The optional [image restoration script](./scripts/restore_assets.py) downloads only image URLs recorded in that archive and requires Pillow; it is not needed for normal builds or deployment because the restored images are already included.

## Content and source notes

Use only the supplied archive for factual additions or corrections. Do not add statistics, nutritional or medical claims, testimonials, contact information, recipes, or product details from the design reference or from assumptions. Grammar, structure, and navigation wording may be improved without changing factual meaning.

The original archive includes health and treatment claims. Source attribution preserves what the original website says; it does not establish independent medical verification. Keep the published attribution and context with that material. Preserve any existing third-party resource links and their source labels when reorganizing content.

The original Buy/order page and purchase-related sections are deliberately excluded. Keep purchase links, prices, ordering instructions, shopping carts, checkout controls, and other commerce flows out of future changes. Educational millet descriptions and recipes can remain when supported by the supplied content.

Review [the content migration notes](./CONTENT-NOTES.md) for the full list of source limitations. In particular, the cookie recipe lacks quantities and a method; the bread recipe has conflicting grain and flour information; nutrition figures have no stated serving basis; and contact listings include inactive or proposed locations. These gaps need source clarification before anyone fills them in.

The validator checks local references offline. It does not verify external website availability, factual accuracy, medical claims, or image rights. Review content against the source and check layouts in a browser before publishing. Test the navigation, recipe filters or search, accordions, and other visible controls using both a pointer and the keyboard; review narrow mobile, tablet, and desktop widths.

## Deploy to milletszone.com

1. Build and validate the site using the commands above.
2. Choose a static website host and upload **the contents of [dist](./dist/)** as the site's public root. Its `index.html` must be at that root. Do not upload the archive, Python sources, or the whole project as the public website.
3. Add `milletszone.com` as the host's custom domain. In your domain registrar's DNS settings, enter the exact records provided by that host. Record names and values depend on the chosen service; no generic DNS values can be substituted safely.
4. Enable the host's managed HTTPS certificate. If you also use `www.milletszone.com`, configure it to redirect to `https://milletszone.com` so the published domain agrees with the generated canonical URLs.
5. Once DNS and HTTPS are active, open the live home page and several detail pages directly. Verify images, internal links, navigation, and mobile layout. Each generated `.html` page must be available at its original path.

For a host with build automation, select this `website` directory as the build root, use `python build.py` as the build command, and `dist` as the publish directory. Otherwise, build locally and upload the output. No server-side application process is required in production.
