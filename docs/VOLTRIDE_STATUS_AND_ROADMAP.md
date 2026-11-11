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

**Status (2026-11-10):** PR #41 was merged as `a0bccd0fbc03226385c43944d6dc13b10caacc37`. The merge passed Ride Match, consent, SEO metadata, generated-file, internal-link, sitemap, and accessibility checks, and the post-deploy live-site workflow succeeded. Production-only GA gating, affiliate click tracking, Ride Match budget removal, catalog alignment, accessory-page cleanup, and blog discovery improvements are therefore in production.

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

**Next checkpoint:** complete the current manufacturer-source audit and verify GA4 event receipt on the production host after explicit consent; then address Search Console discovery/indexing for priority URLs. Keep administrative GA4 key-event configuration separate from code changes.

## 7. Global scope correction for generated model pages

The model-page generator previously described the 25 km/h estimate benchmark as Moroccan law, used Morocco-specific wording in all 30 model titles/FAQs, and marked generated pages with the `ar_MA` locale. This contradicted the global positioning.

Branch `fix/globalize-generated-model-pages` changes `LEGAL_LIMIT` to `REFERENCE_SPEED` (a calculation benchmark, not a universal legal limit), makes road-use guidance jurisdiction-neutral, changes model-page titles and Open Graph locale, and labels the Morocco legal article as relevant only to riders in Morocco. It also updates the model-specific copy and regenerates all 30 model pages.

This change must pass the generated-files check before merge. The 25 km/h benchmark remains in range calculations for consistent comparison; it must not be presented as a universal legal rule. Model specifications remain unverified against manufacturers until a source-verification project is completed.

## 8. Metadata and sitemap refresh

PR #44 shortens the 13 previously flagged page titles, the eight long meta descriptions, and the four generated model titles that exceeded the 60-character target. It also removes the Morocco-only positioning from the Arabic blog index and refreshes sitemap `lastmod` values for the updated model and content URLs. These changes are covered by regression tests. Heading-order observations remain informational and should be reviewed in a separate semantic-accessibility pass rather than changed mechanically.

Generated model pages now shorten only titles that would exceed 60 characters; the H1 is generated from the same title string to prevent metadata/content drift.

PR #45 consolidates the metadata cleanup on a fresh review branch so CI can validate the final generated-page and sitemap state before merge.

## 9. Global currency and locale behavior

The default display currency is now selected from the browser's regional locale, not the UI language: Morocco (MA) defaults to MAD (with an Africa/Casablanca timezone fallback when the browser omits its region), supported euro-area regions default to EUR, and the United States defaults to USD. Unsupported regions fall back to USD because the app currently offers only MAD, USD and EUR. A manually selected currency remains stored and takes precedence over automatic detection. Global Arabic utility/editorial pages no longer advertise the country-specific Open Graph locale `ar_MA`; articles whose subject is specifically Moroccan law, local prices or local market context retain `ar_MA`. Regression tests cover region selection and global Arabic locale metadata. This does not yet provide automatic FX updates or full local-currency coverage; those require a separate product decision and reliable rate source.


## 10. Latest release verification and remaining work (2026-11-10)

### Completed release state
- PR #41 (global Ride Match, analytics host gating, consent-gated affiliate events, accessory cleanup, multilingual blog discovery, one homepage H1, service-worker v18) merged successfully.
- PR #43 (globalized generated model pages and jurisdiction-neutral legal copy) merged successfully.
- PR #45 (metadata cleanup and sitemap dates) merged successfully.
- PR #49 (browser-region currency defaults and global Arabic metadata) merged successfully.
- Latest verified main commit: `26c1d53d18a23b7ba311d6772112480a53cb9036`; Cloudflare deployment and post-deploy live-site checks succeeded. CI reported 81 pages with zero blocking accessibility violations and zero warnings.
- Current production SEO crawl: 50 pages; no missing titles/descriptions, overlong titles/descriptions, noindex issues, or canonicalized-page issues. Thin-content observations remain for Contact and Ride Match; 13 heading-order observations are informational and need semantic review, not mechanical edits.

### Measurement and search findings
- GA4 property is connected and the production stream uses `G-M4CWL77NBK`; measurement-health API reported one web stream, three configured key events, and no Admin API configuration errors.
- Current key events are `purchase`, `close_convert_lead`, and `qualify_lead`. They do not match the site's custom events (`calculator_use`, `ride_match_complete`, `affiliate_click`, `marketplace_search_click`). No key-event counts were recorded in the latest 28-day report. Do not mark marketplace searches as purchases. GA4 Admin event configuration requires a manual owner decision; it was not changed by this repository work.
- GA4's 2026-10-13 to 2026-11-09 acquisition report recorded 18 organic-search sessions, 15 engaged sessions, and zero key events. It also contains legacy Netlify and Cloudflare preview hostnames, so historical totals are not yet a clean production-only baseline. The current code excludes preview hosts going forward; historic rows remain unchanged.
- Search Console is connected to the Pages property. Homepage is indexed with matching user/Google canonical. Ride Match, Accessories, Arabic/English/French blog indexes and sampled Article 8 variants were unknown to Google at inspection time. Re-submit priority URLs after confirming the deployed sitemap and monitor recrawl; unknown is not a permanent exclusion verdict.
- Last 3 months of Search Console page data is extremely sparse (three rows, two clicks total), so avoid over-interpreting ranking/CTR conclusions.

### Product-source audit
- See [MODEL_SOURCE_AUDIT_2026-11-10.md](MODEL_SOURCE_AUDIT_2026-11-10.md). Four iScooter affiliate-only model specifications were checked against manufacturer sources and corrected where necessary. W6 has regional battery variants and is excluded from recommendation scoring until its affiliate SKU is matched. Ecoxtrem Bison GT and M41 are also excluded from Ride Match recommendations until the exact model/region variants are resolved.
- All five AliExpress short-link destinations remain unverified. The canonical 30-model catalog still needs a full manufacturer-source audit; presence in project data is not proof of manufacturer accuracy.

### Remaining phases, in order
1. Verify affiliate redirect destinations and exact regional SKUs; keep uncertain links/specs out of trusted recommendation paths.
2. Complete manufacturer source records for the canonical 30 models, prioritizing models with the most recommendation exposure.
3. Complete GA4 production event smoke test with explicit consent, then decide manually which meaningful events become key events. Keep purchase reserved for actual purchases.
4. Re-submit priority URLs in Search Console and track index status/canonical consistency after Google recrawls.
5. Review heading hierarchy and thin content page-by-page; improve content only where it helps users and search intent.
6. Re-baseline GA4 after enough post-host-gating production data accumulates; do not use old preview-host traffic as current production performance.


## 2026-11-11 — canonical V2 identity audit update

- The staged `model_data_v2.json` now represents all 30 identities in the legacy `models.json` catalog, with 37 market/generation-specific variant records.
- Current staged status: 22 high-confidence `verified_variant` records and 15 unresolved/non-projectable records. Twenty model identities have at least one high-confidence verified variant; ten do not yet have one.
- Models without a high-confidence verified variant: `kaabo-wolf-king`, `navee-g5`, `segway-max-g30`, `teverun-fighter-11`, `vsett-10-plus`, `vsett-8-plus`, `xiaomi-4-pro`, `dualtron-mini`, `dualtron-victor`, `nami-burn-e2-max`.
- The audit matrix now records primary-source findings and explicit evidence limits for every legacy model identity. A variant is not projectable merely because a source record exists; the adapter still requires exact model ID, variant ID, market, complete battery fields, and rated motor power.
- PR #61 (Ecoxtrem Bison GT and M41 exact variants) was merged to main as `edc720f55159fd1ee3342c7713c35067c4c39c95`. Main-branch Site checks and Live site check both passed after deployment.
- PR #62 stages the full 30-identity V2 inventory, adds Xiaomi Essential and Segway E2 Plus evidence, records the remaining Dualtron/NAMI findings, and adds adapter regression tests. No production consumer or legacy catalog change is included. Full CI is required before merge.

### Migration gate — unchanged

Production consumers (`build_models.py`, static model pages, homepage catalog and Ride Match) still use legacy `models.json`. Do not switch them wholesale to V2. Next, implement an explicit market/variant selection contract and a compatibility projection for high-confidence records, retain a safe and clearly marked fallback for unresolved legacy entries only where product behavior requires it, and test each consumer independently. Review generated output before any generator run; `build_models.py` rewrites model pages, homepage catalog sections and service-worker precache data. Keep all consumer migration in separate PRs with CI and preview verification.


## 2026-11-11 — calculator V2 selector implementation (review branch)

- Branch `feat/calculator-v2-market-variant-selector` adds a market/variant picker to the calculator using only high-confidence `verified_variant` records that pass `project_verified_variant`.
- The generated selector exposes 23 market choices across 20 model identities (22 verified variant records; the M41 variant is selectable for both MA and EU).
- Model deep links and the catalog “Use” action no longer auto-fill the legacy catalog specifications. They open the explicit variant selector; models without a projectable V2 variant require manual entry instead of silently falling back to legacy values.
- When a variant is selected, the calculator uses its combined rated motor power and preserves manufacturer-published Wh versus calculated Wh basis. Manual edits clear the selected-variant provenance and recalculate energy from the entered voltage and Ah.
- Unresolved V2 records are excluded from the selector. The catalog card display, comparison table, generated model-page specifications and Ride Match still require their own staged migration; they are not switched by this calculator-only phase.
- No production merge or deployment has been made for this phase; CI and preview review are required.

## 2026-11-11 — post-merge update: staged V2 rollout and Segway US variant

This section supersedes earlier roadmap statements above that said the calculator, catalog, comparison, Ride Match and generated model pages had not yet migrated to V2. Those statements describe the pre-PR #63–#66 state and are retained only as historical context.

### Merged implementation
- PR #63: calculator uses explicit market/variant selection from projectable V2 records.
- PR #64: catalog and comparison consume documented V2 specifications.
- PR #65: Ride Match uses documented market variants.
- PR #66: generated model pages consume V2 variant data.
- PR #67: added the separately verified US Segway Ninebot E2 Plus model 051402U. The French E2 Plus E II remains unresolved; US battery capacity is not copied to the French variant.
- PR #67 merged to `main` as `3ca4030e02aba34598e57546ff5c3d9ca1897eb2`. Its pre-merge CI passed all nine checks, including generated-file reproducibility and axe-core accessibility (81 pages, zero blocking violations and zero warnings). Cloudflare preview deployment succeeded.
- PR #69 added a Playwright live-browser smoke workflow for the calculator and Ride Match. It passed against `https://voltride-4qj.pages.dev` before merge and was squash-merged as `5375b8967d7cc82a2a9c37789f0ceb00523077bf`.

### Current V2 inventory on main
- 30 model identities, 37 market/generation-specific variant records.
- 22 `verified_variant` records across 20 model identities.
- 15 `variant_unresolved` records remain non-projectable.
- 10 model identities still have no high-confidence verified variant. This includes the unresolved French E2 Plus E II; the new US 051402U variant is verified.
- The calculator exposes 23 market choices across 20 identities; the Ecoxtrem M41 verified variant is offered in both MA and EU markets.
- The V2 migration is staged, not a claim that every legacy catalog specification is manufacturer-verified. Keep unresolved variants excluded from trusted recommendation/scoring paths. `models.json` remains part of the legacy identity/catalog compatibility layer; do not delete it or assume every legacy value is verified.

### Post-merge verification status
- The PR #67 branch passed all required checks and Cloudflare preview deployment.
- Main-branch post-merge Site checks and the post-deploy live-site workflow were still running at the time of this update. Do not call the production release fully verified until both workflows finish successfully.
- Production URL remains https://voltride-4qj.pages.dev/.

### Next work
1. Finish main-branch post-merge CI, Cloudflare deployment and live-site verification for commit `3ca4030`.
2. Continue source audit for the 10 identities without a high-confidence verified variant and the 15 unresolved variant records; correct only against exact manufacturer generation/SKU/market evidence.
3. Verify the five AliExpress short-link destinations and exact regional SKUs before enabling any affiliate destination; keep unverified destinations out of direct purchase flows.
4. Run live functional smoke tests for calculator variant selection, catalog, comparison, Ride Match, model pages, language switching, consent/analytics and PWA update/offline behavior.
5. Verify GA4 custom event receipt on production after explicit consent and review Search Console indexing/canonical status. Historical preview-host analytics must remain untouched.


## 2026-11-11 — live browser smoke coverage and post-merge verification

### PR #69 merged
- Added `tools/live-smoke.mjs` and `.github/workflows/live-functional-smoke.yml`.
- The Playwright test ran against the production Pages URL before merge and passed:
  - Calculator returned a positive range estimate (32.1 km) and battery energy (461 Wh) for the default test state.
  - Ride Match completed an EU-market flow and rendered three recommendations.
  - Language switch to English preserved the recommendation results and document direction.
  - Recommendation links used ordinary AliExpress marketplace search URLs; no unverified `s.click.aliexpress.com` URL was emitted.
  - No uncaught browser page errors were observed.
- PR #69 was merged to `main` as `5375b8967d7cc82a2a9c37789f0ceb00523077bf`. It adds tests/workflow only; no production application specifications, affiliate destinations, analytics settings or ad code were changed.

### Current canonical V2 inventory (recounted from main)
- 30 model identities; 37 variant records.
- 22 high-confidence `verified_variant` records across 20 identities.
- 15 unresolved/non-projectable variant records.
- 10 identities still have no high-confidence verified variant: `kaabo-wolf-king`, `navee-g5`, `segway-max-g30`, `teverun-fighter-11`, `vsett-10-plus`, `vsett-8-plus`, `xiaomi-4-pro`, `dualtron-mini`, `dualtron-victor`, `nami-burn-e2-max`.
- The French E2 Plus E II remains unresolved, but the separate US E2 Plus SKU `051402U` is verified; therefore the E2 Plus identity is no longer in the list of identities without a verified variant.

### Post-merge checks
- PR #69 pre-merge Site checks: all nine jobs passed; axe-core checked 81 pages with zero blocking violations and zero warnings.
- PR #69 pre-merge Live functional smoke: passed.
- Main post-merge Site checks (run `43017674045`) and Live site check (run `43017673696`) for commit `5375b8967d7cc82a2a9c37789f0ceb00523077bf` both completed successfully. All nine Site checks passed; the live check confirmed key routes and every sitemap URL returned HTTP 200, and axe-core checked 81 live pages with zero blocking violations and zero warnings.

### Remaining audit boundaries
- Manufacturer-source findings for unresolved variants remain documented in `CANONICAL_MODEL_SOURCE_AUDIT_MATRIX_2026-11-10.md`. No uncertain specification was promoted during this pass.
- NAVEE G5's official page confirms 36V/275.4Wh, 400W rated/800W peak, 32km/h US and 25km/h EU, and a 45km claim at 15km/h; it does not publish Ah, so the two regional V2 records remain non-projectable.
- Segway's official MAX page distinguishes G30 (25km/h) from G30P (30km/h), with 36V/551Wh and 350W nominal motor; the family catalog identity still lacks the suffix and battery Ah, so it remains unresolved.
- Teverun's official Fighter 11 page distinguishes the 60V/26Ah Fighter 11 from the 60V/35Ah 11+, with 85km/h unrestricted specification, 80km/120km range claims and a 25km/h factory road-use limit. Rated motor power and the exact interpretation of the 4900W peak figure remain unresolved.
- VSETT 10+ still has multiple battery options and a 70–80km/h speed range; VSETT 8+ lists "48V 16A" rather than unambiguous Ah and does not clarify rated-vs-peak motor basis. Both remain non-projectable.
- Dualtron Mini and Victor source pages identify battery options and maximum motor output, but do not publish rated motor power; the records remain blocked from projection.
- Five AliExpress short-link destinations remain unverified and continue to fall back to ordinary marketplace search.

### Next work
1. Continue exact-SKU source verification for the unresolved variants; the main post-merge CI and live-site checks are now complete and passed.
2. Continue exact-SKU source verification for the 10 identities and 15 unresolved variant records; only change canonical values where primary evidence resolves generation, market and power basis.
3. Perform a separate production measurement check for GA4 custom event receipt after explicit consent, and a fresh Search Console indexing/canonical review. Existing CI proves consent code behavior, not receipt of live GA4 events.
4. Complete live PWA install/update/offline verification and a broader mobile/responsive navigation review. The browser smoke now covers calculator, catalog, comparison, app language selection, a generated model page and Ride Match.
5. Produce the final readiness report before any advertising strategy or implementation is discussed.


## 2026-11-11 — expanded production browser smoke (PR #71)

- Extended `tools/live-smoke.mjs` to exercise the main app's Settings language selector, catalog variant picker, comparison modal and a generated Xiaomi 3 Lite detail page in addition to the calculator and Ride Match.
- The test explicitly declines the analytics-consent banner in its isolated browser context. This avoids granting consent on behalf of a real visitor and avoids sending synthetic CI traffic to GA4.
- Production smoke result on `https://voltride-4qj.pages.dev`:
  - Calculator: 32.1 km estimated range and 461 Wh energy for the default test state.
  - Catalog: selected the documented Global variant `dualtron-thunder-3-ed2301-72v40ah-global` for Dualtron Thunder 3.
  - Comparison modal rendered the selected model and battery energy.
  - Settings language changed the app document to English/LTR.
  - Generated `/xiaomi-3-lite` detail page returned successfully and declared its own canonical URL.
  - Ride Match selected EU, rendered three recommendations, and retained results after language switching.
  - No uncaught browser page errors.
- The first expanded run exposed a test-harness issue: the consent dialog correctly intercepted the comparison button. The test was corrected to explicitly decline consent; the next production run passed. No application code change was required.
- PR #71 Site checks passed all nine jobs; axe-core checked 81 pages with zero blocking violations and zero warnings. The live functional smoke also passed.
- PR #71 is test/documentation-only. It does not change production application behavior, model specifications, affiliate destinations, analytics configuration or advertising.

### Remaining release checks
- PR #71 merged to `main` as `17985e82756567400eef700e247e2913dc0a171f`. Main Site checks (run `43019541897`) and Live site check (run `43019541987`) both completed successfully. All nine Site jobs passed; the live check confirmed key routes and every sitemap URL returned HTTP 200, and axe-core checked 81 live pages with zero blocking violations and zero warnings.
- GA4 event receipt still requires a separate production measurement verification after an actual explicit consent flow; CI consent tests do not prove GA4 event ingestion.
- Search Console index/canonical status still requires a fresh property-level review; sitemap and canonical CI checks are not a substitute for Google recrawl status.
- Five AliExpress short-link destinations remain unresolved and disabled; do not enable until final product URL, SKU and market are verified.
