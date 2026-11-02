# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Run these from the repository root. This is a static site with no package manifest, bundler, or separate lint/unit-test runner.

- Preview locally: `python3 -m http.server 8080` then open `http://localhost:8080`.
- Regenerate scooter pages and related data-driven sections: `python3 build_models.py`.
- Regenerate troubleshooting guides: `python3 build_guides.py .` (the argument is the site output directory).
- Check internal links, page metadata, canonicals, hreflang, and sitemap entries: `python3 tools/check_links.py`.
- Run the model-generator freshness check used in CI: `python3 build_models.py && git diff --stat --exit-code`. A diff means generated output needs updating/committing or the generator needs correction.
- Accessibility check (optional; needs Node 20+, Playwright, axe, and Chromium): install with `npm install --no-save --no-package-lock playwright@1.56.0 @axe-core/playwright@4`, install Chromium with `npx playwright install chromium`, start the local server, then run `node tools/a11y.mjs http://localhost:8080`. It checks every URL in `sitemap.xml`; there is no single-page test selector.

## Architecture

- Cloudflare Pages serves this repository as static files; there is no server-side application or compile step. Most content pages are hand-authored HTML, with Arabic pages at the root and translated pages under `fr/` and `en/`. Clean URLs omit `.html`; canonical URLs and sitemap entries must follow that form.
- `index.html` contains the calculator/PWA interface and its application logic, including three-language strings, scooter catalog, battery/range estimates, local preferences, trip learning, and calculator features. `site.css` is shared styling. `site.js` provides shared consent-gated analytics, consent UI, table keyboard accessibility, and service-worker registration.
- `models.json` is the source dataset for scooter specifications; `model_texts.json` overrides generated editorial text for selected models. `build_models.py` generates model HTML pages and updates marked regions in `index.html` and `blog.html`, plus `sitemap.xml` and the service-worker precache/version in `sw.js`. Keep the generator's range-estimation formula aligned with the calculator implementation in `index.html`. After changing model data or generator logic, run the generator and include its output changes.
- `build_guides.py` contains the guide content and HTML template, and writes the generated pages under the supplied output directory's `guides/` folder.
- `sw.js` implements offline navigation and asset caching. Its precache list and cache version are maintained by `build_models.py`; generated model pages and static assets need to remain consistent with that list.
- `tools/check_links.py` is the deterministic offline whole-site integrity check; external URLs are intentionally not fetched. `tools/a11y.mjs` runs axe-core against sitemap pages. These checks, plus generated-output freshness, are run by `.github/workflows/site-checks.yml`.
