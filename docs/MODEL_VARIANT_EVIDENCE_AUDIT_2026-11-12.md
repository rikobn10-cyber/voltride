# Model Variant Evidence Audit — 2026-11-13 (status refresh)

## Scope and safety

This is a research and evidence audit of the 16 records currently marked `variant_unresolved` after PR #96 in `model_data_v2.json`.

- No production model data, compatibility rules, UI, affiliate destinations, analytics, consent, advertising, or deployment settings are changed by this audit.
- A manufacturer page that describes a model family is not sufficient to certify a specific generation, SKU, market, or battery option.
- Do not infer nominal voltage from Wh/Ah, rated power from peak power, or one market's specifications from another.
- Keep unresolved records excluded wherever the compatibility adapter requires a fully verified variant.

## Findings

| Model / variant | Evidence reviewed | Remaining blocker | Decision |
|---|---|---|---|
| Kaabo Wolf King GT | [Kaabo official site](https://www.kaabo.com/) and the referenced model manual | The global overview uses 100+ km/h wording; the exact unlocked maximum and rated-vs-peak motor basis are not sufficiently pinned to this exact listing. Do not confuse GT with GTR or King GT Pro. | Keep unresolved. |
| NAVEE G5 US | [NAVEE US product page](https://www.naveetech.com/navee-g5/) | The US page gives 36V / 275.4Wh, 400W rated / 800W maximum, 32 km/h and up to 45 km at 15 km/h, but does not publish Ah. Do not calculate Ah from Wh/V. | Keep unresolved. |
| NAVEE G5 EU | [NAVEE France G5 page](https://naveetech.fr/en/products/navee-g5) | The regional page identifies certified model G5 EU and publishes 36V, 275.4Wh, 10s3p, 7.65Ah cell capacity, 400W rated / 800W maximum, and factory speed settings up to 25 km/h. It reports 37 km at 20 km/h and 29 km at 25 km/h; the separate 45 km claim is at 15 km/h. Exact retail SKU matching is still not established. | Battery evidence is now strong; keep unresolved pending SKU / adapter identity check. Do not treat the three range figures as contradictory: their test speeds differ. |
| Segway MAX G30 / G30P | [Segway ME product page](https://arab.segway.com/product-info/kickscooter-max.html) | PR #96 now represents G30 (25 km/h) and G30P (30 km/h) as separate variant identities. The official page publishes 36V, 551Wh and 350W nominal motor power, but not Ah; exact retail SKU mapping and battery capacity remain unavailable. | Split completed in PR #96; both variants remain unresolved and excluded from projection. Do not infer Ah. |
| Teverun Fighter 11 | [Teverun official Fighter Eleven Plus page](https://teverun.com/product/fighter-eleven-plus/) and [Teverun Europe Fighter Eleven page](https://teverun-europe.com/fighter-eleven/) | Sources distinguish Fighter 11 (60V / 26Ah / 80 km) from 11+ (60V / 35Ah / 120 km). Official regional material also differs on speed and peak-power presentation (80 vs 85 km/h; 4,900 vs 5,000W peak). The current record must remain tied to exact generation and regional configuration. | Keep unresolved; do not merge 11 and 11+. |
| VSETT 10+ | [VSETT official page](https://vsettscooters.com/pages/vsett-10-plus) | Page lists 60V 20.8 / 25.6 / 28Ah options, dual 1,400W motors, 70–80 km/h and range figures 65 / 80 / 90 km, but does not unambiguously pair every range and speed with the 28Ah option or label motor rating basis. | Keep unresolved. |
| VSETT 8+ | [VSETT official page](https://vsettscooters.com/pages/vsett-8-plus-electric-scooter) | Page prints battery as “48V 16A (LG)” rather than explicitly Ah; lists 48V 600W×2, 40–45 km/h and 90 km single / 50 km dual range. Capacity unit and motor power basis need clarification. | Keep unresolved; do not infer Ah. |
| Xiaomi Electric Scooter 4 Pro (DDHBC20NEB) | [Xiaomi official specifications](https://www.mi.com/global/product/xiaomi-electric-scooter-4-pro/specs/) | Exact model code, 12.4Ah / 446Wh, 350W rated / 700W maximum, 25 km/h and 55 km range are published. Nominal battery voltage is not published on the cited specification page. | Keep unresolved; do not infer nominal voltage from Wh/Ah. Do not conflate 4 Pro with 2nd Gen. |
| Segway E2 Plus E II (FR) | [Segway France product page](https://ma-fr.segway.com/ekickscooter/products/e2-plus-e-ii.html) | Exact generation and 21.6V / 220Wh, 300W rated / 500W maximum, 25 km/h are documented; battery Ah and exact SKU are not published on the cited page. | Keep unresolved. |
| Dualtron Mini — 52V 21Ah | [Minimotors Mini Special manual](https://www.minimotors.fr/wp-content/uploads/2024/01/Notice-Dualtron-mini-dual.pdf) | Official manual lists 52V 21Ah LG, 65 km for the single-motor option, 450W nominal single motor / 450W×2 dual motor and 25 km/h, but the current catalog identity does not establish which generation / drive configuration its record represents. | Keep unresolved pending exact generation and drive configuration. |
| Dualtron Mini — 52V 19.2Ah | [Minimotors product detail](https://www.minimotors.com/product_detail.html?code=1990363951451971586) | The referenced product detail page does not establish the precise legacy Mini generation / SKU for this battery option. The more recent official Mini Special manual lists other capacity options and must not be silently substituted. | Keep unresolved. |
| Dualtron Mini — 52V 17.5Ah | [Minimotors Mini Special manual](https://www.minimotors.fr/wp-content/uploads/2024/01/Notice-Dualtron-mini-dual.pdf) | The manual lists 52V 17.5Ah LG, but generation and single/dual-motor configuration must match the record before certification. | Keep unresolved. |
| Dualtron Mini — 52V 13Ah | [Minimotors Mini Special manual](https://www.minimotors.fr/wp-content/uploads/2024/01/Notice-Dualtron-mini-dual.pdf) | The manual lists 52V 13Ah LG, but generation and single/dual-motor configuration must match the record before certification. | Keep unresolved. |
| Dualtron Victor — 60V 24Ah | [Minimotors official product detail](https://www.minimotors.com/product_detail.html?code=1990363951451971586) | Official page lists 60V 24Ah and 30Ah options, 4,000W maximum dual-hub motor, 80 km/h and 85 km / 100 km mileage. Rated motor power is not published; preserve the distinction between maximum and rated output. | Keep unresolved until rated-power requirement / adapter handling is resolved; do not store 4,000W as rated. |
| NAMI BURN-E 2 Max legacy record | [NAMI official manual](https://nami-electric.com/wp-content/uploads/2022/03/USER-MANUAL-BURNE-3-1.pdf) | Manual documents a BURN-E MAX 72V / 40Ah / 2.88kWh configuration and 2 × 1.5kW motors, but does not prove it is the exact legacy BURN-E 2 Max generation in the catalog. | Keep unresolved; generation match is mandatory. |

## Confirmed conclusions

1. The unresolved statuses are not merely missing research flags: most are deliberate safeguards against mixing generations, markets, battery configurations, or rated and peak motor power.
2. NAVEE G5 EU now has direct regional manufacturer evidence for its 36V / 275.4Wh / 7.65Ah cell-capacity pack and the distinct range test points (37 km at 20 km/h; 29 km at 25 km/h; separate up-to-45 km claim at 15 km/h). Exact retail SKU / adapter identity remains the outstanding check.
3. Segway MAX G30 and G30P must not share one universal speed value: the official regional page specifies 25 km/h for G30 and 30 km/h for G30P.
4. Teverun Fighter 11 and Fighter 11+ are distinct battery/range configurations and must not be combined.
5. Xiaomi 4 Pro nominal voltage, Segway E2 Plus E II Ah, NAVEE G5 US Ah, and VSETT 8+ Ah are not to be derived from incomplete manufacturer data.
6. Dualtron Victor's 4,000W figure is explicitly maximum output on the cited manufacturer page, not a published rated-power figure.

## Recommended next implementation sequence

1. The compatibility adapter requires an explicitly selected, high-confidence `verified_variant`, source coverage for identity/battery/motors/speed, complete positive battery voltage/Ah/Wh, and rated motor power; peak power cannot substitute for rated power.
2. PR #96 completed the G30/G30P split and added regression coverage. The two identities remain unresolved because official Ah and exact retail SKU mapping are still absent.
3. NAVEE France now explicitly identifies the certified model as G5 EU and publishes 36V, 275.4Wh, 10s3p, 7.65Ah cell capacity, 400W rated / 800W maximum, and separate range figures at 20/25/15 km/h. This confirms the certified model identity and specification evidence, but not a distinct retail SKU-to-catalog mapping. Keep unresolved until that mapping is established.
4. Xiaomi 4 Pro is tied to exact product code DDHBC20NEB and battery model BCTA+71420-1701, with 12.4Ah / 446Wh and 350W rated / 700W maximum. Xiaomi still does not publish nominal voltage on the cited spec pages; do not infer it.
5. Segway E2 Plus E II manual model code 051402UU and France-market retail SKU are not yet demonstrably the same identifier. Keep Ah null until an official cross-reference connects them.
6. VSETT 8+ still prints `48V 16A (LG)` without an unambiguous Ah unit; do not normalize it to 16Ah.
7. Keep all remaining records unresolved until exact generation / SKU evidence or missing manufacturer fields are obtained. Do not weaken adapter checks to increase the verified count.

## Status refresh — 2026-11-13

- PR #96 is merged into `main` at `6f5c668811cd5f7bbfd2b74385d319969c5f5495`.
- The unresolved inventory is now 16 variant records (up from the 15-record pre-PR #96 audit because G30 was split into G30 and G30P).
- The official NAVEE France page confirms the certified model label `G5 EU` and its published specification set, but no exact retail SKU / catalog mapping was found in this refresh. No status promotion is justified.
- A fresh manufacturer-source search did not establish the missing Xiaomi nominal voltage, Segway France SKU-to-manual model-code mapping, or VSETT 8+ battery-capacity unit.
- No production data, adapter behavior, generated pages, calculator output, compatibility results, deployment settings, analytics, or advertising settings were changed in this refresh.

## Validation boundary

This audit is documentation-only. It does not change production model values or compatibility behavior. Any subsequent data correction must be proposed separately, tested, reviewed, and merged through the normal pull-request process.
