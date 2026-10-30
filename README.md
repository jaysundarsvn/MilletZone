# Millet Zone website

This repository contains the Millet Zone informational website and the source
archive used to prepare its content. The website is a static site generated with
Python; it does not need Node.js, npm, a database, or a web framework.

## Run the website on Windows

1. Install Python 3.10 or newer.
2. Open this repository folder in Visual Studio Code.
3. Open **Terminal → New Terminal** and run:

   ```powershell
   cd website
   python build.py
   python scripts\validate.py
   python -m http.server 4173 --bind 127.0.0.1 --directory dist
   ```

   If `python` is not recognized, use `py` instead.
4. Open [http://127.0.0.1:4173/](http://127.0.0.1:4173/) in your browser.
5. Press **Ctrl+C** in the terminal to stop the local server.

The build and validation commands use Python's standard library. Rebuild with
`python build.py` after changing the website source, then refresh the browser.

## Website files

- `website/build.py` generates the static site.
- `website/content.json` contains the prepared page content.
- `website/styles.css` and `website/app.js` provide the styles and browser interactions.
- `website/assets/` contains the images and asset metadata.
- `website/scripts/validate.py` checks generated pages and local references.
- `website/dist/` is generated output. It is created by the build command and
  is intentionally not tracked in Git.

For more detail on editing, content limitations, and deployment, see
[website/README.md](website/README.md) and
[website/CONTENT-NOTES.md](website/CONTENT-NOTES.md).

## Source archive

`millet_zone_vscode/` contains the downloaded source archive and extraction
tools. Its optional extraction script can be rerun with internet access after
installing the dependencies listed in `millet_zone_vscode/requirements.txt`.
This is not required to build or run the website.
