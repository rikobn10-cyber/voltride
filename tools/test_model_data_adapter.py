import json
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from model_data_adapter import VariantProjectionError, project_verified_variant

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


if __name__ == "__main__":
    unittest.main()
