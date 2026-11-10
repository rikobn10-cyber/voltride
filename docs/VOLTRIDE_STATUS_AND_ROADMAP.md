# VoltRide — Product Status and Roadmap

**Audit date:** 2026-11-10  
**Production URL:** https://voltride-4qj.pages.dev/  
**Repository:** https://github.com/rikobn10-cyber/voltride  
**Primary goal:** A global, multilingual electric-scooter reference and utility site. Arabic, English and French are supported; Morocco-specific material must be explicitly labelled as local context, not treated as the site's global scope.

## 1. Architecture map

- **Cloudflare Pages:** static production hosting and preview deployments.
- **index.html:** main app shell and screens — range/charging calculator, return check, scooter catalog, compare, safety, diagnostics and settings.
- **site.js:** shared privacy/analytics consent logic and service-worker registration.
- **ride-match.html:** standalone guided scooter recommender with AR/FR/EN translations.
- **models.json:** canonical catalog model data.
- **model_texts.json:** editorial model descriptions.
- **build_models.py:** generates model pages and refreshes the model preset block and service-worker precache list. Do not run it casually; inspect its full diff because it can rewrite generated files.
- **build_guides.py:** guide-page generator. Inspect its scope and output before running.
- **sw.js:** PWA cache and offline behaviour. Keep its version in sync with build_models.py.
- **sitemap.xml:** manually maintained. Preserve canonical URLs, language alternates and lastmod discipline.
- **GitHub Actions:** generated-file, SEO, internal-link/canonical/hreflang/sitemap, accessibility, Ride Match and analytics-consent checks.

## 2. Confirmed baseline before the current improvement branch

- PR #40 merged to main as commit `137912e685fcb3918300c7ebfc91088c2309d93e`.
- Post-merge GitHub checks completed successfully, including Cloudflare Pages, live-site accessibility and live-site checks.
- OpenSEO crawl sampled 50 URLs: all 50 returned HTTP 200; all had titles and meta descriptions; no missing image alt text was reported. Mean response time was 22 ms in that crawl.
- GitHub axe-core workflow checked 79 pages on the local build and live site: 0 blocking issues and 0 warnings in that run.
- OpenSEO technical audit reported 43 observations: 6 warnings (3 thin-content, 2 duplicate-title, 1 multiple-H1) and 37 informational observations (15 long titles, 13 heading-order skips, 9 long meta descriptions).
- Catalog source contains 30 models. Ride Match contains those same 30 with matching names/specifications plus 5 extra models. Those 5 extra records need an explicit source/verification policy before being treated as fully trusted catalog items.

## 3. Current improvement branch

Branch: `fix/global-ride-match-analytics-cleanup`

Changes prepared for review:
1. Remove the MAD-denominated budget question and budget scoring from Ride Match. Recommendations now use estimated range and rider preference, without embedded prices.
2. Keep all 30 canonical catalog model records aligned with Ride Match; add regression assertions for names, speed, motor power, voltage, battery capacity and category.
3. Replace Arabic-button-text click detection with a stable `data-action` attribute so Ride Match purchase-click tracking works in AR/FR/EN.
4. Restrict GA4 loading, consent UI and product events to the production hostname. Preview deployments and local development should not pollute production analytics.
5. Track sponsored affiliate-link clicks on content pages after explicit analytics consent.
6. Remove the duplicate service-worker registration from the main app; shared `site.js` owns registration. Bump service-worker cache version and generator version together to `voltride-v18`.
7. Reduce the homepage to one primary H1.
8. Give English and French contact pages distinct titles.
9. Expand English and French blog indexes to list existing translated articles only.
10. Remove unrelated tool-charger and children's e-moto listings from the accessories page; add Arabic, English and French accessories guidance and sitemap entries.
11. Extend regression tests for these behaviours and content-discovery rules.

**Important:** This branch has not been merged. Wait for all CI checks to finish and pass. Do not claim production has these changes until the merge commit has a successful Cloudflare production deployment and live-site verification.

## 4. Findings and priorities

### P0 — Release safety
- Complete CI on the current branch.
- Verify Cloudflare production deployment after merge.
- Test calculator, catalog, compare, Ride Match, consent, affiliate click tracking and mobile layout on the live site.
- Confirm service-worker cache refresh on an existing installed PWA.

### P1 — Measurement integrity
- GA4 property: `properties/558433417`; measurement ID: `G-M4CWL77NBK`.
- GA4 data for 2026-10-13 through 2026-11-09 showed 18 organic sessions, 15 engaged sessions, one active user and no key events. These are sparse data, not enough to establish a growth trend.
- Historical GA4 data included preview/legacy hosts. The current branch adds a production-host gate to prevent future preview pollution.
- GA4 currently has key events configured with names that do not match the site's product events. Review GA4 Admin manually and decide whether `calculator_use`, `ride_match_complete` and `affiliate_click` should be key events. Do not label marketplace searches as purchases.
- Verify real-time/debug event receipt after production deploy and explicit consent; do not infer success from code alone.

### P1 — Search visibility
- Search Console property is connected. A sample URL inspection found the homepage and `/guides/not-charging` indexed with matching declared/Google canonical URLs.
- Several sampled URLs, including Ride Match, accessories, blog indexes and selected translated articles, were reported as unknown to Google at inspection time. This does not prove they are excluded permanently; request indexing for priority pages and monitor coverage.
- Domain/backlink research for the Pages hostname returned no usable domain data. Do not treat this as proof of zero demand or zero links.
- Keep country-specific law, prices and tariff examples clearly labelled by country. Build global guides around universally useful scooter topics.

### P2 — Editorial quality
- The accessories page previously listed a tool charger and a children's electric moto as scooter accessories. Those unrelated listings have been removed on the improvement branch.
- English and French blog indexes previously surfaced only a small subset of already translated content. The branch expands these indexes using existing translated pages; do not link to translations that do not exist.
- The homepage's five H1 headings and duplicate translated contact titles are addressed on the improvement branch.
- Remaining informational audit findings (long titles/descriptions and heading-order skips) should be reviewed page by page. Do not shorten titles mechanically if doing so removes useful search intent; do not pad utility pages just to hit a word count.

### P2 — Product/data quality
- Keep `models.json` as the canonical catalog source. Ride Match has 5 extra entries beyond the 30 catalog models; audit their manufacturer/specification sources and affiliate status before promoting them as catalog-backed recommendations.
- Model prices may remain in internal data for future uses, but should not appear as universal reference prices unless a country, currency, date and source are explicitly provided.
- Preserve the calculator's honesty notes: estimates are not laboratory measurements and depend on rider, terrain, temperature, tires, speed and battery condition.

## 5. Operating rules

1. Plan before code; state the affected files and expected side effects.
2. Read-only audit first. Separate confirmed defects from hypotheses and optional improvements.
3. Use a focused feature/fix branch. Never edit main directly.
4. Keep diffs small. Do not regenerate the entire model/guide catalog without reviewing all generated changes.
5. Do not change canonical, hreflang, sitemap, service-worker or model-source files outside the task scope.
6. Never bypass failing CI or weaken workflows to make a change pass.
7. Merge only after all required checks pass; then verify the production deployment and live site.
8. Maintain this document when a meaningful phase is completed. Avoid reopening already verified areas without new evidence.

## 6. Definition of done

VoltRide is ready to shift from repair mode to measured growth when:
- core calculator, catalog, compare and Ride Match flows pass regression tests and live checks;
- AR/FR/EN language switching is consistent across all published language variants;
- catalog model data is source-backed and consistent;
- privacy consent gates all analytics and preview hosts are excluded;
- GA4 key events are intentionally configured and verified;
- Search Console shows priority pages crawled/indexed with correct canonicals;
- no high-severity accessibility, broken-link, SEO or deployment issues remain;
- performance and editorial work is prioritized using actual user/search data rather than guesswork.

**Next checkpoint:** finish CI on `fix/global-ride-match-analytics-cleanup`, merge only on full success, verify production, then perform a final post-deploy crawl and analytics smoke test.

## 7. Global scope correction for generated model pages

The model-page generator previously described the 25 km/h estimate benchmark as Moroccan law, used Morocco-specific wording in all 30 model titles/FAQs, and marked generated pages with the `ar_MA` locale. This contradicted the global positioning.

Branch `fix/globalize-generated-model-pages` changes `LEGAL_LIMIT` to `REFERENCE_SPEED` (a calculation benchmark, not a universal legal limit), makes road-use guidance jurisdiction-neutral, changes model-page titles and Open Graph locale, and labels the Morocco legal article as relevant only to riders in Morocco. It also updates the model-specific copy and regenerates all 30 model pages.

This change must pass the generated-files check before merge. The 25 km/h benchmark remains in range calculations for consistent comparison; it must not be presented as a universal legal rule. Model specifications remain unverified against manufacturers until a source-verification project is completed.

## 8. Metadata and sitemap refresh

PR #44 shortens the 13 previously flagged page titles, the eight long meta descriptions, and the four generated model titles that exceeded the 60-character target. It also removes the Morocco-only positioning from the Arabic blog index and refreshes sitemap `lastmod` values for the updated model and content URLs. These changes are covered by regression tests. Heading-order observations remain informational and should be reviewed in a separate semantic-accessibility pass rather than changed mechanically.

Generated model pages now shorten only titles that would exceed 60 characters; the H1 is generated from the same title string to prevent metadata/content drift.
