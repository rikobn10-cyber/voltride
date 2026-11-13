# Model Variant Evidence Audit — 2026-11-13 (reconciled after PR #98)

## Scope and source of truth

This is a documentation-only audit of the canonical `model_data_v2.json` on `main` at commit `42aa72de9e4aa080e5f4b8b1e4a0ef8cbec026af`.

- Canonical inventory: 30 model records, 38 variant records, 22 high-confidence verified variants, and 16 `variant_unresolved` records.
- The count is derived from each variant's `verification.status`, not from this document's prose or an earlier audit.
- PR #98 added manufacturer evidence and regression coverage but deliberately retained the NAVEE G5 EU and Segway E2 Plus E II FR records as unresolved because the exact retail-SKU/catalog identity mapping is not established.
- No production data, adapter logic, generated pages, calculator behavior, analytics, consent, advertising, or deployment settings are changed by this audit.

A manufacturer family page, regional specification page, or manual alone is not sufficient to certify a catalog record unless it establishes the exact generation, market, SKU/model identity, and required specification fields. Do not infer nominal voltage from Wh/Ah, rated power from peak power, or one market's specifications from another.

## Current unresolved inventory (16 records)

| Model | Variant ID | Confidence | Remaining evidence gap / handling |
|---|---|---:|---|
| Kaabo Wolf King GT | `kaabo-wolf-king-gt-global-unresolved` | medium | Exact generation/listing, unlocked maximum speed, and rated-vs-peak motor basis are not pinned. Do not confuse GT with GTR or King GT Pro. |
| NAVEE G5 US | `navee-g5-us-current` | medium | US page publishes 36V / 275.4Wh and rated/maximum power but not Ah. Do not calculate or infer Ah. |
| NAVEE G5 EU | `navee-g5-eu-current` | medium | NAVEE France page identifies certified G5 EU and publishes 36V / 275.4Wh / 7.65Ah cell capacity, 400W rated / 800W maximum, and market-specific range/speed test points. Exact retail SKU-to-catalog mapping remains unproven; keep unresolved. |
| Segway MAX G30 | `segway-max-g30-global` | medium | G30 and G30P are separate identities after PR #96. Official page gives 36V / 551Wh / 350W nominal but not Ah or exact retail SKU mapping. Keep unresolved. |
| Segway MAX G30P | `segway-max-g30p-global` | medium | Same evidence boundary as G30; retain distinct 30 km/h variant identity, but do not infer Ah or SKU equivalence. |
| Teverun Fighter 11 | `teverun-fighter-11-60v26ah-global-unresolved` | medium | Keep Fighter 11 distinct from 11+; regional speed/peak-power presentation and exact generation/configuration need resolution. |
| VSETT 10+ | `vsett-10-plus-60v28ah-global-unresolved` | medium | Official page lists multiple battery options and dual motors, but does not unambiguously pair all range/speed claims with the exact 28Ah configuration or label rated-power basis. |
| VSETT 8+ | `vsett-8-plus-global-unresolved` | medium | Manufacturer prints “48V 16A (LG)” without an unambiguous Ah unit; do not normalize to 16Ah. Motor-power basis also needs clarification. |
| Xiaomi Electric Scooter 4 Pro | `xiaomi-4-pro-ddhbc20neb-global` | medium | Exact product/battery codes and 12.4Ah / 446Wh, 350W rated / 700W maximum are published, but cited Xiaomi specification material does not publish nominal voltage. Do not infer it or conflate with 2nd Gen. |
| Segway E2 Plus E II (FR) | `segway-e2-plus-e-ii-fr` | high | France page links official manual with model code 051402UU and 21.6V / 10.2Ah / 220Wh, 300W nominal / 500W maximum. Exact link between the manual model code and France-market retail SKU is still not established; keep unresolved and distinct from US model 051402U. |
| Dualtron Mini — 52V 21Ah | `dualtron-mini-52v-lg-21ah-global` | high | Manual lists this capacity, but catalog record's exact generation and single/dual-motor configuration are not established. |
| Dualtron Mini — 52V 19.2Ah | `dualtron-mini-52v-cn-19-2ah-global` | high | Referenced product detail does not establish the precise legacy Mini generation/SKU; do not substitute Mini Special evidence silently. |
| Dualtron Mini — 52V 17.5Ah | `dualtron-mini-52v-lg-17-5ah-global` | high | Exact generation and single/dual-motor configuration must match the catalog record before verification. |
| Dualtron Mini — 52V 13Ah | `dualtron-mini-52v-cn-13ah-global` | high | Exact generation and single/dual-motor configuration must match the catalog record before verification. |
| Dualtron Victor — 60V 24Ah | `dualtron-victor-60v24ah-global-unresolved` | high | Manufacturer lists 4,000W maximum output, not rated power. Do not store peak/maximum as rated power; rated-power evidence or an explicitly reviewed adapter policy is required. |
| NAMI BURN-E 2 Max legacy record | `nami-burn-e-max-legacy-generation-unresolved` | medium | Available manual documents BURN-E MAX configuration but does not prove it is the exact legacy BURN-E 2 Max generation in the catalog. |

## Evidence updates retained by PR #98

- **NAVEE G5 EU:** the regional manufacturer page is useful evidence for the certified EU model and its published specification set. The record remains unresolved solely because the exact retail SKU-to-catalog identity mapping is not demonstrated. The range figures must remain associated with their stated test speeds; they are not interchangeable.
- **Segway E2 Plus E II FR:** the official France page and linked manual strengthen the evidence for model code 051402UU and the published battery/motor/speed values. The code-to-France-retail-SKU cross-reference is still missing, so the record remains unresolved.
- Neither evidence update authorizes promoting either record to `verified_variant`.

## Projection and compatibility safeguards

The current `model_data_adapter.py` is an explicit projection boundary. A caller must select model ID, variant ID, and market. Projection is allowed only when:

1. The variant status is `verified_variant` with `high` confidence.
2. Source evidence covers identity, battery, motors, and speed.
3. Battery nominal voltage, Ah, and Wh are all positive and present; unresolved energy is rejected.
4. Rated motor power and motor count are present with an explicit rated-power basis. Peak power is never a substitute for rated power.
5. A market-specific maximum speed is present.

Do not weaken these checks to increase the verified count. Keep all 16 unresolved records out of compatibility projection.

## Next implementation sequence

1. Seek exact manufacturer/authorized-retailer cross-reference evidence for NAVEE G5 EU retail SKU and Segway E2 Plus E II FR model code 051402UU.
2. Resolve missing manufacturer fields for Xiaomi 4 Pro nominal voltage, NAVEE G5 US Ah, and VSETT 8+ capacity unit only from authoritative evidence.
3. Continue generation/configuration matching for the Dualtron Mini and NAMI legacy records; preserve rated-versus-peak distinctions for Kaabo, VSETT, and Dualtron Victor.
4. Any future status promotion must update canonical data and regression tests in a separate reviewed change; this audit alone does not change eligibility.

## Validation boundary

Inventory cross-check performed against `model_data_v2.json` on `main` at `42aa72de9e4aa080e5f4b8b1e4a0ef8cbec026af`: 30 models / 38 variants / 22 verified / 16 unresolved. This document is documentation-only and does not alter production behavior.
