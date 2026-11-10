# VoltRide canonical model data schema v2 — migration plan

**Status:** design proposal only  
**Date:** 2026-11-10  
**Scope:** canonical scooter records, generator, calculator presets, catalog and Ride Match compatibility  
**Non-goal:** this document does not change any model specifications, recommendations, prices, affiliate links or generated pages.

## 1. Why a schema migration is required

The current `models.json` record has one unqualified value for each of `voltage`, `ah`, `motor` and `speed`. The current generator and browser app then assume:

- battery energy is always `voltage × ah`;
- `motor` means one comparable motor-power figure;
- `speed` is one global maximum;
- each model name identifies one stable configuration.

Those assumptions are not valid for every scooter family. Manufacturer sources may publish nominal voltage, rated capacity, watt-hours, rated motor power, peak motor power, per-motor values, combined values and region-specific speed limits separately. A generic model name may span several generations and SKUs.

The migration must preserve the existing site while preventing unsupported values from being represented as verified facts.

## 2. Proposed canonical structure

Use a stable model identity with one or more explicit variants. Do not put a guessed default variant on a global model.

```json
{
  "schemaVersion": 2,
  "id": "example-model",
  "name": "Example Model",
  "manufacturer": "Example",
  "category": "commuter",
  "variants": [
    {
      "variantId": "example-model-eu-2025",
      "generation": "2025",
      "sku": "manufacturer SKU when known",
      "market": ["EU"],
      "battery": {
        "nominalVoltageV": 36,
        "capacityAh": 10,
        "energyWh": 360,
        "energyWhBasis": "manufacturer_published",
        "sourceUrl": "https://manufacturer.example/specs"
      },
      "motors": {
        "count": 1,
        "ratedPowerW": 350,
        "ratedPowerBasis": "combined",
        "peakPowerW": 700,
        "peakPowerBasis": "combined"
      },
      "speed": {
        "maxKmh": 25,
        "market": "EU",
        "conditions": "factory configuration"
      },
      "rangeClaim": {
        "maxKm": 40,
        "basis": "manufacturer_claim",
        "conditions": "manufacturer test conditions"
      },
      "sources": [
        {
          "url": "https://manufacturer.example/specs",
          "publisher": "Manufacturer",
          "sourceType": "official_product_page",
          "supports": ["battery", "motors", "speed"],
          "checkedAt": "2026-11-10"
        }
      ],
      "verification": {
        "status": "verified_variant",
        "confidence": "high",
        "checkedAt": "2026-11-10",
        "notes": []
      }
    }
  ]
}
```

The example values above are illustrative only and are not specifications for a real product.

### Required semantics

- `battery.nominalVoltageV`: manufacturer-stated nominal pack voltage. Do not silently replace it with charger voltage or a rounded marketing label.
- `battery.capacityAh`: manufacturer-stated capacity for this exact pack.
- `battery.energyWh`: prefer an explicitly manufacturer-published Wh value. If calculated, mark `energyWhBasis: "calculated_from_nominal_values"` and retain the inputs. Do not silently calculate when source semantics conflict.
- `motors.count`: number of motors.
- `ratedPowerW` and `peakPowerW`: separate fields. Every power value must identify whether it is per motor or combined.
- `speed.maxKmh`: tied to the variant and market. Store factory/unlocked or firmware conditions explicitly when sources distinguish them.
- `rangeClaim`: a manufacturer claim with test conditions, not a real-world guarantee or the VoltRide estimate.
- `sources`: evidence is attached to the exact variant and to the fields it supports.
- `verification.status`: use controlled values such as `verified_variant`, `provisional`, `variant_unresolved`, `source_conflict`, and `excluded`.
- `verification.checkedAt`: date the evidence was checked, not page publication date.

## 3. Legacy compatibility contract

The current production code and tests depend on the legacy fields. Do not remove them in the first migration.

A single adapter in the generator should derive a clearly marked legacy projection only when the variant is sufficiently identified:

| Legacy field | v2 source | Rule |
|---|---|---|
| `voltage` | `battery.nominalVoltageV` | Only for the selected exact variant |
| `ah` | `battery.capacityAh` | Only for the selected exact variant |
| `motor` / catalog `power` | `motors.ratedPowerW` | Only when basis is explicitly combined; do not substitute peak |
| `speed` | `speed.maxKmh` | Only for the selected market/configuration |
| estimated Wh | `battery.energyWh` | Use the published value or explicitly labelled calculated value |

Do not generate a legacy preset for an unresolved model variant. Do not silently fall back to today's ambiguous values. Where a legacy consumer requires a complete preset, the model must either have a verified selected variant or remain unavailable to that preset until resolved.

The adapter must expose the provenance/status alongside projected values so UI code can label provisional data and Ride Match can exclude ineligible variants.

## 4. Consumer behavior and migration order

1. **Inventory consumers:** `build_models.py`, `index.html` calculator presets/catalog, `ride-match.html`, saved scooter profiles, comparison, range estimates, generated model pages, blog cards and service-worker precache.
2. **Add schema validation:** validate required keys, units, controlled enums, unique model/variant IDs, source URLs, dates and power basis. Reject impossible or ambiguous projections rather than guessing.
3. **Add an adapter:** generate the legacy fields for the existing UI and Ride Match while preserving provenance. Keep one source of truth; never hand-edit generated blocks.
4. **Update calculations:** use explicit `energyWh` when supported; otherwise use a documented calculation only when nominal voltage and capacity semantics are compatible. Keep calculator estimates separate from manufacturer range claims.
5. **Update UI labels:** distinguish rated vs peak power, market-specific speed, and manufacturer claims vs VoltRide estimates. Never label an unqualified speed or power value as universal.
6. **Update Ride Match:** require a usable, sufficiently verified variant for scored recommendations. Preserve current exclusion behavior for unresolved variants such as W6 and the unresolved EcoXtrem records.
7. **Migrate records in batches:** only add exact variants supported by primary sources. Do not bulk-correct all 30 models from approximate or secondary evidence.
8. **Regenerate and inspect:** run the generator, inspect every generated diff, and ensure sitemap/canonical/hreflang files remain curated and untouched unless deliberately changed.
9. **Remove legacy fields only in a later migration:** only after all consumers, tests and stored-profile migration paths use v2 directly.

## 5. Test requirements

Add dedicated tests for:

- schema version and validation failures;
- model and variant ID uniqueness;
- battery Wh published vs calculated basis;
- rated vs peak and per-motor vs combined power;
- regional speed variants and no implicit global default;
- unresolved/conflicting sources never becoming verified recommendations;
- adapter output matching the existing legacy contract for verified variants;
- no preset generated for unresolved variants;
- generated model pages accurately distinguish claims, estimates and verification status;
- saved scooter profiles and existing query-string model presets remain backward-compatible;
- Ride Match uniqueness, eligibility and scoring;
- generated files, internal links, canonicals, hreflang, sitemap, accessibility and live-site checks.

## 6. Initial record dispositions

Use the source audit matrix in `docs/CANONICAL_MODEL_SOURCE_AUDIT_MATRIX_2026-11-10.md` as the evidence ledger. Initial priorities:

- **Material mismatch:** NAVEE G5, NIU KQi3 Max, GOTRAX G4, Segway MAX G30/G30P identity, Apollo City Pro battery semantics.
- **Variant unresolved:** INOKIM OXO, Teverun Fighter 11, Dualtron Mini, VSETT 10+, KuKirin variants, Segway MAX G2 speed configuration.
- **Primary source/SKU unresolved:** Apollo Ghost, Kaabo Wolf King GT, Nami Burn-E 2 Max, EcoXtrem Bison GT/M41.
- **Core values provisionally align for a named variant:** GOTRAX GXL V2, Xiaomi 3 Lite, Xiaomi 4 Pro original generation, Segway E2 Plus E II, and selected VSETT versions. These still need explicit variant records and sources before the legacy adapter treats them as verified.

These are work queues, not permission to overwrite current production values without the variant and source being matched.

## 7. Release gates

- No production model values change in the schema-design PR.
- No schema migration PR merges with failing CI.
- No change to recommendations until adapter output and eligibility tests prove that unresolved models are excluded.
- No generated files are committed unless produced by the updated generator and reviewed as a complete diff.
- Deploy only after all CI checks pass; then verify the production catalog, calculator presets, Ride Match, model pages and analytics consent behavior.

## 8. Explicitly out of scope

- Reintroducing static catalog prices or price-based ranking.
- Treating affiliate links as proof of a model SKU or manufacturer specification.
- Treating manufacturer range claims as measured range.
- Applying Morocco-specific legal assumptions to the global model dataset.
