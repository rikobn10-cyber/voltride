import json
import re
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from model_data_adapter import VariantProjectionError, project_verified_variant, sources_by_field

DATA = json.loads((ROOT / "model_data_v2.json").read_text(encoding="utf-8"))


class ModelDataAdapterTests(unittest.TestCase):
    def test_projects_only_explicit_verified_xiaomi_variant(self):
        result = project_verified_variant(
            DATA, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-uk", "UK"
        )
        self.assertEqual(result["legacy_fields"], {
            "id": "xiaomi-3-lite",
            "name": "Xiaomi Scooter 3 Lite",
            "category": "budget",
            "voltage": 36,
            "ah": 5.2,
            "motor": 300,
            "peakMotorPowerW": None,
            "energyWh": 187,
            "energyWhBasis": "manufacturer_published",
            "speed": 25,
        })
        self.assertEqual(result["range_claim"]["max_km"], 20)
        self.assertEqual(result["provenance"]["battery_energy_wh"], 187)
        self.assertEqual(result["provenance"]["variant_id"], "xiaomi-3-lite-mjddhbc03zm-uk")

    def test_selector_options_include_only_high_confidence_projectable_variants(self):
        from build_models import build_verified_variant_options
        options = build_verified_variant_options()
        expected = 0
        for model in DATA["models"]:
            for variant in model["variants"]:
                verification = variant.get("verification", {})
                if verification.get("status") == "verified_variant" and verification.get("confidence") == "high":
                    for market in variant["market"]:
                        expected += 1
                        self.assertIn(model["id"], options)
                        found = [item for item in options[model["id"]]
                                 if item["variantId"] == variant["variantId"] and item["market"] == market]
                        self.assertEqual(len(found), 1)
                        self.assertGreater(found[0]["voltage"], 0)
                        self.assertGreater(found[0]["ah"], 0)
                        self.assertGreater(found[0]["motor"], 0)
                        self.assertGreater(found[0]["energyWh"], 0)
        self.assertEqual(sum(len(items) for items in options.values()), expected)
        for model in DATA["models"]:
            for variant in model["variants"]:
                if variant.get("verification", {}).get("status") != "verified_variant":
                    self.assertFalse(any(item["variantId"] == variant["variantId"]
                                         for item in options.get(model["id"], [])))

    def test_generated_index_variant_options_match_adapter_projection(self):
        from build_models import build_verified_variant_options
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        match = re.search(r"const MODEL_VARIANTS = (.*);", html)
        self.assertIsNotNone(match, "index.html must contain generated V2 variant options")
        self.assertEqual(json.loads(match.group(1)), build_verified_variant_options())

    def test_model_deep_links_no_longer_autofill_legacy_specs(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("openModelVariantPicker(slug)", html)
        self.assertIn("function handleModelVariantChange()", html)
        self.assertNotIn("const p = slug && Object.prototype.hasOwnProperty.call(MODEL_PRESETS, slug)", html)

    def test_catalog_hides_legacy_specs_until_a_verified_v2_variant_is_selected(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("function renderCatalog(){")
        end = html.index("\nfunction toggleFavorite", start)
        catalog = html[start:end]
        self.assertIn("getCatalogVariantOptions(s.id)", catalog)
        self.assertIn("getSelectedCatalogVariant(s.id)", catalog)
        self.assertIn("data-catalog-variant", catalog)
        self.assertNotIn("s.voltage", catalog)
        self.assertNotIn("s.ah", catalog)
        self.assertNotIn("s.power", catalog)
        self.assertNotIn("s.speed", catalog)
        self.assertIn("catalogPending", catalog)

    def test_compare_uses_explicitly_selected_v2_variant_for_every_spec_row(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("function openCompare(){")
        end = html.index("\nfunction useScooter", start)
        compare = html[start:end]
        self.assertIn("getSelectedCatalogVariant(s.id)", compare)
        self.assertIn("data-compare-variant", compare)
        self.assertIn("const v = selectedFor(s)", compare)
        self.assertIn("compareVariant", compare)
        self.assertIn("compareEnergyBasis", compare)
        self.assertIn("compareSource", compare)
        self.assertNotIn("s.voltage", compare)
        self.assertNotIn("s.ah", compare)
        self.assertNotIn("s.power", compare)
        self.assertNotIn("s.speed", compare)

    def test_requires_explicit_market(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-uk", "")

    def test_rejects_wrong_market(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-uk", "US")

    def test_xiaomi_pro_2_uses_official_hk_battery_values(self):
        result = project_verified_variant(
            DATA, "xiaomi-pro-2", "xiaomi-pro-2-ddhbc11neb-hk", "HK"
        )
        self.assertEqual(result["legacy_fields"]["voltage"], 37)
        self.assertEqual(result["legacy_fields"]["ah"], 12.8)
        self.assertEqual(result["legacy_fields"]["energyWh"], 474)
        self.assertEqual(result["legacy_fields"]["motor"], 300)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], 600)

    def test_xiaomi_essential_uses_exact_spain_sku_and_published_battery(self):
        result = project_verified_variant(
            DATA, "xiaomi-essential", "xiaomi-essential-ddhbc05neb-es", "ES"
        )
        self.assertEqual(result["legacy_fields"]["voltage"], 36)
        self.assertEqual(result["legacy_fields"]["ah"], 5.1)
        self.assertEqual(result["legacy_fields"]["energyWh"], 183)
        self.assertEqual(result["legacy_fields"]["motor"], 250)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], 500)
        self.assertEqual(result["legacy_fields"]["speed"], 20)

    def test_rejects_segway_e2_plus_until_battery_capacity_is_confirmed(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "segway-e2-plus", "segway-e2-plus-e-ii-fr", "FR"
            )

    def test_selects_market_specific_niu_speed(self):
        us = project_verified_variant(DATA, "niu-kqi3-max", "niu-kqi3-max-us", "US")
        eu = project_verified_variant(DATA, "niu-kqi3-max", "niu-kqi3-max-eu", "EU")
        self.assertEqual(us["legacy_fields"]["speed"], 32.2)
        self.assertEqual(eu["legacy_fields"]["speed"], 25)
        self.assertEqual(us["legacy_fields"]["motor"], 450)
        self.assertEqual(eu["legacy_fields"]["motor"], 450)
        self.assertEqual(us["legacy_fields"]["energyWh"], 608.4)
        self.assertEqual(eu["legacy_fields"]["energyWh"], 608.4)
        self.assertEqual(us["legacy_fields"]["peakMotorPowerW"], 900)

    def test_gotrax_projection_preserves_calculated_energy_and_unknown_peak(self):
        result = project_verified_variant(
            DATA, "gotrax-gxl-v2", "gotrax-gxl-v2-us-current", "US"
        )
        self.assertEqual(result["legacy_fields"]["voltage"], 36)
        self.assertEqual(result["legacy_fields"]["ah"], 5.2)
        self.assertEqual(result["legacy_fields"]["energyWh"], 187.2)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], None)
        self.assertEqual(result["legacy_fields"]["speed"], 24.9)

    def test_apollo_dual_motor_projection_keeps_rated_and_peak_separate(self):
        result = project_verified_variant(
            DATA, "apollo-city-pro", "apollo-city-pro-2023-ca", "CA"
        )
        self.assertEqual(result["legacy_fields"]["motor"], 1000)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], 2000)
        self.assertEqual(result["legacy_fields"]["energyWh"], 960)
        self.assertEqual(result["range_claim"]["max_km"], None)

    def test_rejects_niu_market_variant_mismatch(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "niu-kqi3-max", "niu-kqi3-max-eu", "US")

    def test_rejects_unknown_variant(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "xiaomi-3-lite", "not-a-real-variant", "UK")

    def test_aggregates_explicit_per_motor_rated_and_peak_power(self):
        fixture = json.loads(json.dumps(DATA))
        variant = next(m for m in fixture["models"] if m["id"] == "xiaomi-3-lite")["variants"][0]
        variant["motors"] = {
            "count": 2,
            "ratedPowerW": 300,
            "ratedPowerBasis": "per_motor",
            "peakPowerW": 500,
            "peakPowerBasis": "per_motor",
        }
        result = project_verified_variant(
            fixture, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-uk", "UK"
        )
        self.assertEqual(result["legacy_fields"]["motor"], 600)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], 1000)

    def test_navee_n40_projects_official_manual_values(self):
        result = project_verified_variant(
            DATA, "navee-n40", "navee-n40-nkp21111-a25-global", "Global"
        )
        self.assertEqual(result["legacy_fields"]["voltage"], 37)
        self.assertEqual(result["legacy_fields"]["ah"], 10)
        self.assertEqual(result["legacy_fields"]["energyWh"], 370)
        self.assertEqual(result["legacy_fields"]["motor"], 350)
        self.assertEqual(result["legacy_fields"]["speed"], 25)
        self.assertEqual(result["range_claim"]["max_km"], 40)

    def test_kukirin_g2_max_and_g4_keep_eu_open_variants_explicit(self):
        g2 = project_verified_variant(
            DATA, "kukirin-g2-max", "kukirin-g2-max-eu-open-current", "EU-OPEN"
        )
        g4 = project_verified_variant(
            DATA, "kukirin-g4", "kukirin-g4-eu-open-current", "EU-OPEN"
        )
        self.assertEqual(g2["legacy_fields"]["ah"], 20.8)
        self.assertEqual(g2["legacy_fields"]["peakMotorPowerW"], 1200)
        self.assertEqual(g4["legacy_fields"]["speed"], 70)
        self.assertEqual(g4["legacy_fields"]["motor"], 2000)
        self.assertIsNone(g4["legacy_fields"]["peakMotorPowerW"])
        self.assertEqual(g4["legacy_fields"]["energyWh"], 1200)

    def test_inokim_oxo_2026_keeps_rated_and_peak_power_per_motor(self):
        result = project_verified_variant(
            DATA, "inokim-oxo", "inokim-oxo-2026-us", "US"
        )
        self.assertEqual(result["legacy_fields"]["voltage"], 57.6)
        self.assertEqual(result["legacy_fields"]["ah"], 26)
        self.assertEqual(result["legacy_fields"]["motor"], 2000)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], 2600)
        self.assertEqual(result["legacy_fields"]["speed"], 64.9)

    def test_rejects_vsett_8_plus_until_battery_and_power_basis_are_resolved(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "vsett-8-plus", "vsett-8-plus-global-unresolved", "Global"
            )

    def test_gotrax_g4_original_projects_exact_us_variant_and_gear_range(self):
        result = project_verified_variant(
            DATA, "gotrax-g4", "gotrax-g4-us-original-42015315951731", "US"
        )
        self.assertEqual(result["legacy_fields"]["voltage"], 36)
        self.assertEqual(result["legacy_fields"]["ah"], 10.4)
        self.assertEqual(result["legacy_fields"]["motor"], 500)
        self.assertEqual(result["legacy_fields"]["speed"], 32.2)
        self.assertEqual(result["range_claim"]["max_km"], 40.2)

    def test_rejects_vsett_10_plus_until_power_speed_and_range_variant_are_resolved(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "vsett-10-plus", "vsett-10-plus-60v28ah-global-unresolved", "Global"
            )

    def test_apollo_ghost_keeps_per_motor_rated_and_peak_values_separate(self):
        result = project_verified_variant(
            DATA, "apollo-ghost", "apollo-ghost-us-2020", "US"
        )
        self.assertEqual(result["legacy_fields"]["motor"], 1600)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], 2000)
        self.assertEqual(result["legacy_fields"]["energyWh"], 947)
        self.assertEqual(result["legacy_fields"]["speed"], 55)
        self.assertEqual(result["range_claim"]["max_km"], 62)

    def test_rejects_kaabo_wolf_king_gt_until_power_and_speed_are_resolved(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "kaabo-wolf-king", "kaabo-wolf-king-gt-global-unresolved", "Global"
            )

    def test_rejects_teverun_fighter_11_until_rated_power_basis_is_resolved(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "teverun-fighter-11", "teverun-fighter-11-60v26ah-global-unresolved", "Global"
            )

    def test_segway_max_g2_preserves_us_eu_speed_and_peak_power(self):
        us = project_verified_variant(
            DATA, "segway-max-g2", "segway-max-g2-us-051501u", "US"
        )
        eu = project_verified_variant(
            DATA, "segway-max-g2", "segway-max-g2-e-051501e", "EU"
        )
        self.assertEqual(us["legacy_fields"]["speed"], 35)
        self.assertEqual(us["legacy_fields"]["peakMotorPowerW"], 1000)
        self.assertEqual(eu["legacy_fields"]["speed"], 25)
        self.assertEqual(eu["legacy_fields"]["peakMotorPowerW"], 900)
        self.assertEqual(us["legacy_fields"]["energyWh"], 551)
        self.assertEqual(eu["legacy_fields"]["energyWh"], 551)

    def test_vsett_9_plus_aggregates_two_rated_motors_without_guessing_peak(self):
        result = project_verified_variant(
            DATA, "vsett-9-plus", "vsett-9-plus-48v-21ah-global", "Global"
        )
        self.assertEqual(result["legacy_fields"]["motor"], 1300)
        self.assertEqual(result["legacy_fields"]["peakMotorPowerW"], None)
        self.assertEqual(result["legacy_fields"]["energyWh"], 1008)
        self.assertEqual(result["legacy_fields"]["speed"], 53)
        self.assertEqual(result["range_claim"]["max_km"], 100)

    def test_rejects_segway_g30_family_until_suffix_and_capacity_are_resolved(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "segway-max-g30", "segway-max-g30-family-unresolved", "Global"
            )

    def test_rejects_navee_g5_until_battery_capacity_is_resolved(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "navee-g5", "navee-g5-us-current", "US"
            )

    def test_rejects_xiaomi_4_pro_until_nominal_voltage_is_resolved(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(
                DATA, "xiaomi-4-pro", "xiaomi-4-pro-ddhbc20neb-global", "Global"
            )

    def test_rejects_non_verified_variant(self):
        fixture = json.loads(json.dumps(DATA))
        next(m for m in fixture["models"] if m["id"] == "xiaomi-3-lite")["variants"][0]["verification"]["status"] = "provisional"
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(fixture, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-uk", "UK")

    def test_never_substitutes_peak_power_for_missing_rated_power(self):
        fixture = json.loads(json.dumps(DATA))
        motors = next(m for m in fixture["models"] if m["id"] == "xiaomi-3-lite")["variants"][0]["motors"]
        motors["ratedPowerW"] = None
        motors["ratedPowerBasis"] = "unresolved"
        motors["peakPowerW"] = 600
        motors["peakPowerBasis"] = "combined"
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(fixture, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-uk", "UK")


    def test_ride_match_requires_an_explicit_market_before_recommendations(self):
        html = (ROOT / "ride-match.html").read_text(encoding="utf-8")
        self.assertIn('id="rideMarket"', html)
        self.assertIn('answers.market = RIDE_MATCH_MARKETS.includes(event.target.value)', html)
        self.assertIn('if (!answers.market) return [];', html)
        self.assertIn('function getEligibleScooters()', html)

    def test_ride_match_uses_only_verified_v2_variants(self):
        html = (ROOT / "ride-match.html").read_text(encoding="utf-8")
        self.assertIn("RIDE_MATCH_MODELS.flatMap", html)
        self.assertIn("variant.energyWh", html)
        self.assertIn("variant.sourceUrl", html)
        self.assertNotIn("const uniqueScooters", html)
        self.assertNotIn("uniqueScooters.slice", html)
        self.assertNotIn("const eligibleScooters = uniqueScooters", html)

    def test_ride_match_generator_projects_only_verified_market_variants(self):
        generator = (ROOT / "build_models.py").read_text(encoding="utf-8")
        self.assertIn('variants = variant_options.get(model["id"], [])', generator)
        self.assertIn('ride_markets = sorted({variant["market"]', generator)
        self.assertIn('/*RIDE_VARIANTS:START*/', generator)
        self.assertIn('project_verified_variant(', generator)

    def test_ride_match_market_options_are_all_adapter_projectable(self):
        options = []
        for model in DATA["models"]:
            for variant in model.get("variants", []):
                if variant.get("verification", {}).get("status") != "verified_variant":
                    continue
                if variant.get("verification", {}).get("confidence") != "high":
                    continue
                for market in variant.get("market", []):
                    projected = project_verified_variant(DATA, model["id"], variant["variantId"], market)
                    fields = projected["legacy_fields"]
                    options.append((model["id"], variant["variantId"], market, fields["energyWh"]))
        self.assertGreater(len(options), 0)
        self.assertTrue(all(row[3] > 0 for row in options))
        self.assertEqual(len(options), len(set((row[0], row[1], row[2]) for row in options)))


    def test_generated_model_pages_show_only_verified_market_variants(self):
        for model in DATA["models"]:
            path = ROOT / (model["id"] + ".html")
            self.assertTrue(path.exists(), model["id"] + ": generated model page must exist")
            page = path.read_text(encoding="utf-8")
            verified = [
                variant for variant in model.get("variants", [])
                if variant.get("verification", {}).get("status") == "verified_variant"
                and variant.get("verification", {}).get("confidence") == "high"
            ]
            self.assertNotIn("مواصفات مرجعية لم نتحقق منها بعد", page, model["id"])
            self.assertNotIn('href="/?model=', page, model["id"])
            self.assertIn("مواصفات النسخ الموثقة حسب السوق", page, model["id"])
            if not verified:
                self.assertIn("لم يتم التحقق من نسخة هذا الموديل بعد", page, model["id"])
                self.assertNotIn("ثلاثة سيناريوهات للمدى (تقدير VoltRide)", page, model["id"])
                continue
            self.assertNotIn("لم يتم التحقق من نسخة هذا الموديل بعد", page, model["id"])
            for variant in verified:
                market = variant.get("market", [])
                self.assertTrue(any(m in page for m in market), model["id"] + ": market must be visible")
                sources = variant.get("sources", [])
                self.assertTrue(sources, model["id"] + ": verified variant must retain source evidence")
                visible_sources = sources if model["id"] in {"apollo-city-pro", "gotrax-gxl-v2"} else sources[:1]
                for source in visible_sources:
                    self.assertIn(source["url"], page, model["id"] + ": expected evidence source must be linked")
                if model["id"] in {"apollo-city-pro", "gotrax-gxl-v2"}:
                    self.assertIn("evidence-by-field", page, model["id"] + ": field-level source attribution must render")


    def test_sources_are_attributed_to_the_fields_they_support(self):
        apollo = next(m for m in DATA["models"] if m["id"] == "apollo-city-pro")["variants"][0]
        grouped = sources_by_field(apollo["sources"])
        self.assertIn("battery-assembly", grouped["battery"][0]["url"])
        self.assertIn("tech-specs", grouped["motors"][0]["url"])
        self.assertEqual(grouped["motors"], grouped["speed"])
        gotrax = next(m for m in DATA["models"] if m["id"] == "gotrax-gxl-v2")["variants"][0]
        gotrax_grouped = sources_by_field(gotrax["sources"])
        self.assertIn("36v-5-4ah", gotrax_grouped["battery"][0]["url"])
        self.assertIn("gxl-commuter", gotrax_grouped["motors"][0]["url"])
        self.assertEqual(gotrax_grouped["motors"], gotrax_grouped["speed"])
        self.assertEqual(gotrax_grouped["motors"], gotrax_grouped["rangeClaim"])

    def test_sources_by_field_deduplicates_urls_and_ignores_invalid_records(self):
        rows = [
            {"url": "https://example.com/spec", "publisher": "Example", "supports": ["battery", "motors"]},
            {"url": "https://example.com/spec", "publisher": "Example", "supports": ["battery"]},
            {"url": "http://insecure.example/spec", "publisher": "Bad", "supports": ["battery"]},
            {"url": "https://example.com/no-publisher", "supports": ["battery"]},
        ]
        grouped = sources_by_field(rows)
        self.assertEqual(len(grouped["battery"]), 1)
        self.assertEqual(len(grouped["motors"]), 1)

    def test_generated_model_index_does_not_publish_legacy_specs(self):
        blog = (ROOT / "blog.html").read_text(encoding="utf-8")
        start = blog.index("<!--MODELS:START-->")
        end = blog.index("<!--MODELS:END-->", start)
        section = blog[start:end]
        self.assertIn("مواصفات موديلات VoltRide حسب السوق", section)
        self.assertIn("النسخة والسوق قيد التحقق", section)
        self.assertNotIn("بطارية 36V 12.8Ah", section)
        self.assertNotIn("تقدير نحو", section)


    def test_every_unresolved_variant_is_rejected_for_every_declared_market(self):
        unresolved = []
        for model in DATA.get("models", []):
            for variant in model.get("variants", []):
                verification = variant.get("verification", {})
                if verification.get("status") != "verified_variant":
                    unresolved.append((model["id"], variant["variantId"], variant.get("market", [])))
        self.assertEqual(len(unresolved), 15, "Update the evidence audit when unresolved inventory changes")
        for model_id, variant_id, markets in unresolved:
            self.assertTrue(markets, f"{model_id}/{variant_id} must declare its intended market")
            for market in markets:
                with self.subTest(model=model_id, variant=variant_id, market=market):
                    with self.assertRaises(VariantProjectionError):
                        project_verified_variant(DATA, model_id, variant_id, market)

    def test_unresolved_variants_never_appear_in_generated_calculator_or_catalog_options(self):
        from build_models import build_verified_variant_options
        options = build_verified_variant_options()
        unresolved_ids = {
            variant["variantId"]
            for model in DATA.get("models", [])
            for variant in model.get("variants", [])
            if variant.get("verification", {}).get("status") != "verified_variant"
        }
        generated_ids = {
            item["variantId"]
            for model_options in options.values()
            for item in model_options
        }
        self.assertTrue(unresolved_ids.isdisjoint(generated_ids))


    def test_navee_g5_eu_official_certified_identity_is_recorded_but_not_projected(self):
        model = next(m for m in DATA["models"] if m["id"] == "navee-g5")
        variant = next(v for v in model["variants"] if v["variantId"] == "navee-g5-eu-current")
        self.assertEqual(variant["verification"]["status"], "variant_unresolved")
        self.assertEqual(variant["battery"]["capacityAh"], 7.65)
        self.assertTrue(any(
            source["url"] == "https://naveetech.fr/en/products/navee-g5"
            and "identity" in source["supports"]
            for source in variant["sources"]
        ))
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "navee-g5", "navee-g5-eu-current", "EU")

    def test_segway_e2_plus_fr_manual_evidence_does_not_assume_regional_sku_mapping(self):
        model = next(m for m in DATA["models"] if m["id"] == "segway-e2-plus")
        variant = next(v for v in model["variants"] if v["variantId"] == "segway-e2-plus-e-ii-fr")
        self.assertEqual(variant["verification"]["status"], "variant_unresolved")
        self.assertIsNone(variant["battery"]["capacityAh"])
        self.assertTrue(any(
            source["url"] == "https://store.segway.com/media/wysiwyg/e2_plus_ii/Product_Manual.pdf"
            and source["sourceType"] == "official_product_manual"
            for source in variant["sources"]
        ))
        self.assertTrue(any("051402UU" in note for note in variant["verification"]["notes"]))
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "segway-e2-plus", "segway-e2-plus-e-ii-fr", "FR")


if __name__ == "__main__":
    unittest.main()
