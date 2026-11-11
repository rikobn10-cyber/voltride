# Canonical 30-model source audit matrix — started 2026-11-10; updated 2026-11-11

## Purpose and decision rule

This document tracks manufacturer-source verification for the 30 records in `models.json`. It is an audit record, not a declaration that every row is verified. A model is only safe to normalize when the exact generation, battery pack, motor configuration, and destination-market variant are identified. Rated motor power, peak power, battery nominal voltage, cell/pack capacity, and regional speed limits must remain distinct fields where the manufacturer distinguishes them.

**No legacy production `models.json` values or generated model pages were changed.** Evidence-backed records were added to the staged V2 dataset; the generated Ride Match data and service-worker precache were updated only for affiliate-link and PWA safety. The findings below identify where the current catalog is supported, variant-dependent, or materially inconsistent. Manufacturer-claimed range and speed are not independent real-world test results.

## Newly rechecked records

| Catalog ID | Current catalog values (V / Ah / motor W / km/h) | Manufacturer evidence found | Audit disposition |
|---|---|---|---|
| `xiaomi-pro-2` | 36 / 12.8 / 300 / 25 | Xiaomi Hong Kong lists model DDHBC11NEB, 37V nominal, 12.8Ah / 474Wh, 300W rated / 600W max, 25 km/h. | **Flag battery semantics/capacity.** Legacy 36V nominal conflicts with the manufacturer-published 37V nominal. Retain rated motor as 300W; do not conflate with 600W peak. |
| `xiaomi-essential` | 36 / 5.2 / 250 / 20 | Xiaomi Spain lists DDHBC05NEB, 36V, 5.1Ah / 183Wh, 250W rated / 500W max, 20 km/h. | **Minor capacity mismatch.** Confirm whether catalog 5.2Ah is a rounded or alternate pack; official published capacity is 5.1Ah. |
| `segway-e2-plus` | 21.6 / 10.2 / 300 / 25 | Segway E2 Plus E II regional product/manual data lists 21.6V, 220Wh / 10.2Ah, 300W rated / 500W max, 25 km/h. | **Core values align for E2 Plus E II.** Add explicit generation/market identity; do not assume all E2 Plus generations share this exact pack. |
| `apollo-city-pro` | 52 / 20 / 1000 / 51 | Apollo's City Pro 2023 specification page identifies dual motors at 500W nominal each / 1000W peak each, 51 km/h. Apollo's battery replacement listing identifies 48V 20Ah for City/City Pro 2023–24. | **Legacy catalog mismatch.** The 2023 Pro V2 record uses the documented 48V/20Ah pack and two 500W rated / 1000W peak motors; 960Wh is explicitly calculated. No range claim is inferred. |
| `gotrax-g4` | 36 / 10.4 / 350 / 32 | GOTRAX official G4 listing specifies 36V 10.4Ah, 500W motor, 20mph / 32km/h. | **Material motor mismatch.** Catalog's 350W is not supported by the current official G4 listing; update only after confirming exact G4/G4 Pro generation. |
| `inokim-oxo` | 60 / 25.6 / 2000 / 65 | INOKIM's current global page lists OXO at 60V 26Ah, 2600W peak and 65km/h. An older OXO manual lists 60V 25.6Ah and dual 800W motors (1300W peak each). | **Generation/configuration-dependent.** Current and older manufacturer/distributor materials differ. Do not replace 25.6Ah or 2000W until the catalog's OXO generation and whether motor power is nominal or peak are identified. |
| `teverun-fighter-11` | 60 / 26 / 5000 / 85 | Teverun Europe lists Fighter Eleven (60V 26Ah, dual 1600W motors, 5000W peak, up to 80km/h); Teverun's global Fighter 11/11+ page lists 4900W peak and 85km/h, with 60V 26Ah for 11 and 35Ah for 11+. | **Variant/source discrepancy.** The catalog's 26Ah matches Eleven, while 85km/h matches another official regional/product page. Confirm exact SKU/market before normalizing speed. |

## Earlier source sample — retained findings, not re-certified in this pass

| Catalog ID | Manufacturer evidence / concern | Current disposition |
|---|---|---|
| `xiaomi-3-lite` | Xiaomi 3 Lite: 36V 5.2Ah, 300W rated, 25km/h. | Core values align. |
| `xiaomi-4-pro` | Original 4 Pro: 36V 12.4Ah, 350W rated / 700W max, 25km/h. Do not mix with 2nd Gen. | Core values align for original generation; label generation explicitly. |
| `segway-max-g30` | Segway distinguishes G30 (25km/h) from G30P (30km/h); 36V pack, 551Wh, 350W nominal. | Current name G30 with 30km/h appears to conflate G30P. |
| `segway-max-g2` | Segway support lists 36V 15.3Ah, 450W nominal / 1000W max; 35km/h is enabled higher-speed configuration, while factory default is 32km/h. | Variant/configuration-dependent; do not present 35km/h as universal. |
| `navee-n40` | NAVEE manual lists 37V nominal, 10Ah, 350W, 25km/h, range under specified test conditions. | Catalog 36V may be rounding/field semantics; reconcile against 37V before changing. |
| `navee-g5` | NAVEE official G5 page: 36V, 275.4Wh (7.65Ah), 400W rated / 800W max, US 32km/h / EU 25km/h, range up to 45km at 15km/h. | **Material mismatch:** catalog 48V / 10.4Ah / 350W. Correct variant and rated-vs-peak schema first. |
| `niu-kqi3-max` | NIU official US listing: 48V 13Ah / 608.4Wh, 450W rated / 900W max, 32km/h. EU listing: same pack/power, 25km/h. | **Material mismatch:** catalog 12.7Ah and 38km/h. Correct capacity; speed must be market-specific (not 38). |
| `kukirin-g2-pro` | Official listings vary by generation/market; 48V 15–15.6Ah and 600W rated are reported. | Variant label/source SKU required. |
| `kukirin-g2-max` | KuKirin official listing: 48V 20.8Ah, 1000W rated / 1200W peak, 55km/h. | **Capacity mismatch:** catalog says 20Ah; use 20.8Ah only after matching generation. |
| `kukirin-g3-pro` | Official listings show 52V 23–23.4Ah, dual 1200W rated motors (2400W total), 65km/h. | Exact pack SKU needed; 23.2Ah is not a universal figure. |
| `kukirin-g4` | Official listing in the prior sample: 60V 20Ah, 2000W rated, 70km/h. | Catalog 75km/h needs exact variant/source confirmation. |
| `vsett-8-plus` | 48V 16Ah, dual 600W motors (1200W total), approx. 40–45km/h. | Core values align for documented version. |
| `vsett-9-plus` | 48V 21Ah, dual 650W motors (1300W total), up to 53km/h. | Core values align for 21Ah version. |
| `vsett-10-plus` | 60V 20.8/25.6/28Ah variants, dual 1400W motors; speed varies by configuration. | Catalog 28Ah/2800W is one configuration, not universal. |
| `dualtron-mini` | Multiple Mini generations and battery/motor configurations exist. | Not verifiable as a single generic model; generation required. |
| `dualtron-victor` | Prior source sample supports a 60V 24Ah, 4000W max, 80km/h version. | Version-specific; retain provisional variant label. |
| `dualtron-thunder-3` | Prior source sample lists 72V 40Ah, 10,800W max, 100km/h. | Catalog 11,000W differs; verify exact manufacturer spec before correction. |
| `ecoxtrem-bison-gt` | EcoXtrem has a Bison GT 1000W product and a separate Bison 800W product. | Current 800W GT row may mix products; excluded from recommendations pending SKU resolution. |
| `ecoxtrem-bison-m41` | Multiple M41 battery/motor configurations exist (including 52V 20Ah single/dual variants). | Current 48V 18Ah / 1000W / 50km/h not tied to exact SKU; excluded pending resolution. |

## Additional source checks and remaining unverified records

GOTRAX's official GXL V2 product page and battery parts listing support 36V, 5.2Ah, 250W average motor power, and 15.5mph (about 25km/h). This matches the current `gotrax-gxl-v2` catalog row. The official product page currently advertises up to 12.5 miles of range, while older GOTRAX product/editorial material states 9–12 miles; range is therefore retained as a manufacturer claim, not a guaranteed real-world value.

The following records have not yet been matched to a sufficiently specific primary manufacturer source and exact generation/SKU in this pass. Their current values must remain **provisional**, not “manufacturer verified”:

- `kaabo-wolf-king` — Kaabo's official global overview identifies the Wolf King GT family, but rated-vs-peak motor basis and exact speed ceiling remain unresolved; its V2 record keeps those fields null.
- `kaabo-wolf-king` — the official Kaabo USA result found is for King GT Pro, not sufficient proof for the catalog's Wolf King GT row; do not substitute one model's figures for the other.
- `nami-burn-e2-max` — exact primary manufacturer evidence for the catalog's specific Burn-E 2 Max configuration remains outstanding.

INOKIM OXO and the remaining variant-sensitive models still need SKU-level resolution. Apollo City Pro 2023 and Apollo Ghost now have dedicated market-specific V2 records; Teverun Fighter 11 has an unresolved V2 evidence record pending rated-power basis.

## Primary source links

- Xiaomi Pro 2: https://www.mi.com/hk/mi-electric-scooter-Pro2/specs/
- Xiaomi Essential: https://www.mi.com/es/mi-electric-scooter-essential/specs/
- Segway E2 Plus E II: https://ma-fr.segway.com/ekickscooter/products/e2-plus-e-ii.html
- Segway E2 Plus E II manual: https://store-ca.segway.com/media/wysiwyg/e2_plus_ii/Product_Manual.pdf
- Apollo City Pro 2023: https://apolloscooters.ca/pages/tech-specs-apollo-city-2023-pro
- Apollo City 2023–24 battery: https://apolloscooters.co/products/apollo-city-city-pro-2023-battery-assembly
- GOTRAX G4: https://gotrax.com/products/g4-electric-scooter-for-adults
- GOTRAX GXL V2: https://gotrax.com/products/gxl-commuter-scooter-hand-brake-edition
- GOTRAX GXL V2 battery: https://gotrax.com/products/36v-5-4ah-escooter-battery
- Apollo Ghost legacy article: https://apolloscooters.co/blogs/news/apollo-ghost-best-adult-electric-scooter
- INOKIM current global range: https://inokim.com/
- INOKIM OXO older specification reference: https://www.manualslib.com/manual/1580367/Inokim-Oxo.html?page=4
- Teverun Fighter Eleven: https://teverun-europe.com/product/fighter-eleven-2/
- Teverun Fighter 11 / 11+: https://teverun.com/product/fighter-eleven-plus/
- NAVEE G5: https://www.naveetech.com/navee-g5/
- NIU KQi3 Max US: https://shopca.niu.com/collections/kqi3-series/products/niu-kqi3-max-electric-kick-scooter-for-adults
- NIU KQi3 Max EU: https://shopeu.niu.com/en-fr/collections/kick-scooter/products/niu-kqi3-max-electric-kick-scooter-for-adults-eu-version
- Segway MAX G30/G30P: https://arab.segway.com/product-info/kickscooter-max.html
- Segway MAX G2: https://support.segway.com/support_product.php?segcatid=80
- KuKirin G2 Max: https://kukirinmobility.com/products/kukirin-g2-max-electric-scooter

## Next implementation gate

Before changing `models.json`, the data schema and generator must be reviewed together. At minimum, the canonical model record needs to distinguish:

1. nominal battery voltage and Ah/Wh (without silently deriving one from rounded values);
2. rated motor power and peak motor power, including motor count and whether a value is per motor or combined;
3. top speed by regional SKU/configuration, not one unqualified global number;
4. manufacturer source URL, exact variant/SKU, market, verification date, and confidence/status.

Only after exact variants are resolved should the canonical records be changed and the full generated diff reviewed. Any change must regenerate model pages and dependent model presets, then pass model scoring, generated-file, SEO, internal-link, accessibility, and live-site checks. Until then, flagged and unresolved records should not be presented as fully verified.


## 2026-11-11 source recheck and first V2 migration batch

The following first-party pages were rechecked on 2026-11-11. Findings are recorded here; legacy `models.json` values remain unchanged until the compatibility adapter and consumer migration are complete.

| Catalog ID | First-party evidence rechecked | Decision |
|---|---|---|
| `xiaomi-3-lite` | Xiaomi UK specs identify SKU MJDDHBC03ZM, 36V nominal, 5.2Ah, 187Wh, 300W rated, 25km/h, and up to 20km range. | **Migrated as one verified V2 variant** (`xiaomi-3-lite-mjddhbc03zm-global`). Peak motor power remains null/unresolved because the cited page does not publish it. |
| `xiaomi-pro-2` | Xiaomi Hong Kong identifies DDHBC11NEB, 37V nominal, 12.8Ah/474Wh, 300W rated/600W max, 25km/h. | Legacy 36V nominal is materially inconsistent. V2 uses the exact 37V/12.8Ah/474Wh manufacturer values. |
| `xiaomi-essential` | Xiaomi Spain identifies DDHBC05NEB, 36V, 5.1Ah/183Wh, 250W rated/500W max, 20km/h. | Legacy 5.2Ah mismatch. Hold until regional model code is confirmed. |
| `segway-e2-plus` | Segway France E2 Plus E II page lists 21.6V, 220Wh, 300W rated/500W max, 25km/h, up to 25km at 15km/h. | Exact E II generation is identifiable; Ah is not stated on this page. Keep V2 battery capacity null rather than deriving it. Eligible for a future variant record once SKU identity is attached. |
| `navee-g5` | NAVEE official page lists 36V/275.4Wh, 400W rated/800W max, US 32km/h and EU 25km/h, up to 45km at 15km/h. | Legacy 48V/10.4Ah/350W is materially inconsistent. Keep US/EU speed as separate market variants. |
| `niu-kqi3-max` | NIU US and EU official listings both list 48V, 13Ah/608.4Wh and 450W rated/900W max; US 32km/h, EU 25km/h. | Legacy 12.7Ah/38km/h is not supported. Create separate US and EU variants; do not select a global speed. |
| `gotrax-g4` | GOTRAX official G4 page lists 36V/10.4Ah and 500W, with 20mph/32km/h top speed; page includes G4 Original and G4 Pro selections. | Legacy 350W is not supported by this page. Keep G4/G4 Pro SKU distinction unresolved until the selected variant is identified. |
| `segway-max-g30` | Segway official regional MAX page distinguishes G30 at 25km/h from G30P at 30km/h; 36V, 551Wh and 350W nominal. | Catalog name G30 with 30km/h is an identity/market conflation. Hold until the intended model is selected. |
| `kukirin-g2-max` | KuKirin official page lists 48V/20.8Ah, 1000W rated/1200W peak and up to 55km/h. | Legacy 20Ah needs correction only after generation/market SKU is pinned. |

### Migration boundary

Only the exact Xiaomi 3 Lite SKU above is currently in `model_data_v2.json`. This is a staged evidence-backed record, not a switch of production authority: `build_models.py` and all current UI consumers still read the legacy catalog. No legacy values, model pages, or recommendations were changed by this V2 record. The remaining 10 model identities stay out of V2 until their own variant evidence is complete.


### Additional exact variants migrated on 2026-11-11

- `xiaomi-pro-2-ddhbc11neb-hk`: Xiaomi Hong Kong identifies product code DDHBC11NEB, 37V, 12.8Ah/474Wh, 300W rated/600W peak, 25km/h and 45km manufacturer range claim. The staged V2 record uses the manufacturer-published Wh value and keeps the legacy 36V/12.8Ah discrepancy visible rather than carrying it forward.
- `niu-kqi3-max-us`: NIU's official US listing identifies 48V, 13Ah/608.4Wh, 450W rated/900W max, 20mph top speed and 40-mile range. The dataset stores the metric conversions (32.2km/h and 64.4km) and records the original imperial units in conditions.
- `niu-kqi3-max-eu`: NIU's official EU listing identifies the same pack and motor values, but 25km/h top speed and 65km range. This is a separate variant; no global speed is inferred.

The staged V2 dataset now contains 20 model identities and 23 variants (16 verified, 7 unresolved). The adapter still requires an explicit variant ID and market; none of these records has been switched into production consumers.


### KuKirin G-series exact variant evidence — 2026-11-11

- `kukirin-g2-pro-eu-current`: the KuKirin EU official listing identifies 48V/15.6Ah, 600W rated rear motor, up to 1000W peak, 45km/h and up to 58km range. The legacy catalog's 15Ah is not carried forward. V2 calculates 748.8Wh from the published nominal V × Ah and labels the value as calculated.
- `kukirin-g3-pro-eu-open-current`: the official listing identifies 52V/23.4Ah, two 1200W rated motors, up to 65km/h in dual-motor mode and up to 80km range. The page explicitly distinguishes this open configuration from German ABE and Spain VMP versions. V2 uses market code `EU-OPEN` and calculates 1216.8Wh from the published nominal V × Ah.

The staged V2 dataset now contains 20 model identities and 23 variants (16 verified, 7 unresolved). The two KuKirin records do not alter legacy production data until consumer migration is completed.


### Apollo City Pro 2023 variant evidence — 2026-11-11

- `apollo-city-pro-2023-ca`: Apollo's 2023 Pro technical page identifies the dual-motor configuration, 500W nominal and 1000W peak per motor, and 51km/h top speed. Apollo's official battery assembly page identifies a 48V/20Ah pack and confirms compatibility with City Pro 2023-24. The V2 record keeps rated and peak power per motor separate, records 960Wh as calculated (not manufacturer-published), and leaves range claim null because the cited City Pro spec page did not establish a specific range figure.



### GOTRAX GXL V2 US variant evidence — 2026-11-11

- `gotrax-gxl-v2-us-current`: GOTRAX's official GXL V2 product page identifies 250W average motor power, 15.5mph maximum speed and up to 12.5 miles range. Its official replacement battery page explicitly lists GXL V2 compatibility and 36V/5.2Ah. V2 stores 24.9km/h and 20.1km as conversions from the original US units, and 187.2Wh as a calculated value (36V × 5.2Ah), not a manufacturer-published Wh figure. Peak motor power remains unresolved.


### Xiaomi Electric Scooter 4 Pro original-generation record — 2026-11-11

- `xiaomi-4-pro-ddhbc20neb-global`: Xiaomi's official global page identifies model code DDHBC20NEB, 12.4Ah/446Wh, 350W rated/700W max, 25km/h and up to 55km after the specified firmware update. The page does **not** state nominal battery voltage. The V2 record is therefore intentionally `variant_unresolved` (medium confidence), with voltage null; no 36V value is inferred from Wh/Ah. Do not conflate this original model code with 4 Pro 2nd Gen.


### NAVEE G5 regional evidence records — 2026-11-11

- `navee-g5-us-current` and `navee-g5-eu-current`: NAVEE's official G5 page publishes 36V/275.4Wh, 400W rated/800W peak, up to 45km range at 15km/h, and separate US (32km/h) and EU (25km/h) maximum speeds. It does not publish battery Ah. Both records are therefore `variant_unresolved` (medium confidence), with `capacityAh: null`; the adapter must reject them until Ah is established. This keeps regional speeds separate without inferring battery capacity from Wh/V.


### Segway MAX G30 family evidence record — 2026-11-11

- `segway-max-g30-family-unresolved`: Segway's official page identifies G30 at 25km/h and G30P at 30km/h, with 36V nominal battery, 551Wh, 350W nominal motor power and a typical 65km range under stated test conditions. It does not publish Ah, and the current catalog ID omits the G30/G30P suffix. The V2 record is therefore `variant_unresolved`: Ah and speed remain null; do not promote the catalog's 30km/h value to a universal G30 specification.


### VSETT 9+ 48V/21Ah variant evidence — 2026-11-11

- `vsett-9-plus-48v-21ah-global`: VSETT's official product page lists the 48V/21Ah battery option, dual 650W brushless motors, 53km/h maximum speed and up to 100km dual-motor mileage for that battery variant. The V2 record calculates 1008Wh from 48V × 21Ah and labels it calculated; peak power is left null because the cited page does not publish it.


### Segway MAX G2 US/EU variants — 2026-11-11

- segway-max-g2-us-051501u: Segway's official support page identifies US model 051501U, 36V/15.3Ah/551Wh, 450W nominal/1000W max, 32km/h factory default and up to 35km/h after app enablement. The V2 maximum speed is 35km/h, with the default and enablement condition explicitly stated; 70km is the theoretical range at the manufacturer's stated test speed.
- segway-max-g2-e-051501e: Segway's official EU product page and manual identify EU model 051501E, 36V/15.3Ah/551Wh, 450W nominal/900W max, 25km/h and up to 70km theoretical range. The 900W EU maximum is not conflated with the 1000W US maximum.

The current legacy segway-max-g2 row matches the US maximum only when higher speed is enabled; V2 preserves both US and EU variants separately.


### Additional official variants — 2026-11-11

- navee-n40-nkp21111-a25-global: NAVEE's official N40 manual identifies model NKP21111-A25, 37V/10Ah/370Wh, 350W rated motor, 25km/h maximum speed and approx. 40km range under its stated 75kg/25°C/15km/h test. Peak power is not published.
- kukirin-g2-max-eu-open-current: KuKirin's official G2 Max page identifies 48V/20.8Ah, 1000W rated/1200W peak, 55km/h and up to 70km. It explicitly excludes German ABE and Spain VMP variants; Wh is calculated from nominal V × Ah.
- kukirin-g4-eu-open-current: KuKirin's official G4 page identifies 60V/20Ah, 2000W rated rear motor, up to 70km/h and up to 75km. It says peak output is at least 2400W, not an exact figure, so peak power remains null; Wh is calculated from nominal V × Ah. Both KuKirin records are tagged EU-OPEN, not treated as universal legal configurations.


### Apollo Ghost, Kaabo Wolf King GT and Teverun Fighter 11 evidence — 2026-11-11

- apollo-ghost-us-2020: Apollo's official article identifies dual 800W rated motors with 1000W peak per motor, 52V/18.2Ah/947Wh, 55km/h, and up to 62km in the lowest speed setting. The V2 record separates rated and peak power; range conditions explicitly distinguish the 62km low-speed claim from the 40km average and max-speed range.
- kaabo-wolf-king-gt-global-unresolved: Kaabo's official global site lists 72V/35Ah, dual 2000W motors, up to 180km range and 100+km/h. It does not specify rated-vs-peak motor basis or an exact speed ceiling; both remain null and the record is unresolved. Do not substitute the separate King GT Pro values.
- teverun-fighter-11-60v26ah-global-unresolved: Teverun's official page distinguishes Fighter 11 (60V/26Ah, 85km/h, 80km) from Fighter 11+ (60V/35Ah, 85km/h, 120km). The 4900W figure is labelled peak but its motor basis is unclear and rated power is absent; power remains unresolved. The factory road-use speed limit of 25km/h is documented separately from the unrestricted 85km/h specification.


### GOTRAX G4 Original and VSETT 10+ evidence — 2026-11-11

- gotrax-g4-us-original-42015315951731: GOTRAX's official product page identifies the exact G4 Original variant, 36V/10.4Ah/approximately 374.4Wh, 500W average motor, 20mph top speed and up to 25 miles in Gear 1. It separately lists up to 15 miles in Gear 2 at 20mph. The record does not conflate G4 Original with G4 Pro's suspension/tire differences.
- vsett-10-plus-60v28ah-global-unresolved: VSETT's official page lists 60V 20.8/25.6/28Ah options, dual 1400W motors and a 70–80km/h range. It does not specify rated-vs-peak basis or exact speed for the 28Ah option, and the 65/80/90km range values are not explicitly paired to battery variants. The V2 record keeps speed, power and range null and remains ineligible for projection.


### INOKIM OXO 2026 and VSETT 8+ evidence — 2026-11-11

- inokim-oxo-2026-us: INOKIM's official 2026 OXO page lists 57.6V/26Ah, 2×1000W rated / 2×1300W peak motors, 40.3mph top speed and 68-mile top range. V2 keeps this 2026 configuration separate from older 60V OXO variants; Wh and metric units are explicitly converted.
- vsett-8-plus-global-unresolved: VSETT's official page lists 48V 16A (LG), dual 600W motors, 40–45km/h and 90km single / 50km dual range. The capacity unit is ambiguous ('16A' rather than Ah) and the motor power basis is not explicit; capacity/Wh and motor power remain null, so the adapter rejects this record.
