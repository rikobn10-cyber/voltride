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
            DATA, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-global", "Global"
        )
        self.assertEqual(result["legacy_fields"], {
            "id": "xiaomi-3-lite",
            "name": "Xiaomi Scooter 3 Lite",
            "category": "budget",
            "voltage": 36,
            "ah": 5.2,
            "motor": 300,
            "speed": 25,
        })
        self.assertEqual(result["range_claim"]["max_km"], 20)
        self.assertEqual(result["provenance"]["battery_energy_wh"], 187)
        self.assertEqual(result["provenance"]["variant_id"], "xiaomi-3-lite-mjddhbc03zm-global")

    def test_requires_explicit_market(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-global", "")

    def test_rejects_wrong_market(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-global", "US")

    def test_selects_market_specific_niu_speed(self):
        us = project_verified_variant(DATA, "niu-kqi3-max", "niu-kqi3-max-us", "US")
        eu = project_verified_variant(DATA, "niu-kqi3-max", "niu-kqi3-max-eu", "EU")
        self.assertEqual(us["legacy_fields"]["speed"], 32.2)
        self.assertEqual(eu["legacy_fields"]["speed"], 25)
        self.assertEqual(us["legacy_fields"]["motor"], 450)
        self.assertEqual(eu["legacy_fields"]["motor"], 450)

    def test_rejects_niu_market_variant_mismatch(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "niu-kqi3-max", "niu-kqi3-max-eu", "US")

    def test_rejects_unknown_variant(self):
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(DATA, "xiaomi-3-lite", "not-a-real-variant", "Global")

    def test_rejects_non_verified_variant(self):
        fixture = json.loads(json.dumps(DATA))
        next(m for m in fixture["models"] if m["id"] == "xiaomi-3-lite")["variants"][0]["verification"]["status"] = "provisional"
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(fixture, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-global", "Global")

    def test_never_substitutes_peak_power_for_missing_rated_power(self):
        fixture = json.loads(json.dumps(DATA))
        motors = next(m for m in fixture["models"] if m["id"] == "xiaomi-3-lite")["variants"][0]["motors"]
        motors["ratedPowerW"] = None
        motors["ratedPowerBasis"] = "unresolved"
        motors["peakPowerW"] = 600
        motors["peakPowerBasis"] = "combined"
        with self.assertRaises(VariantProjectionError):
            project_verified_variant(fixture, "xiaomi-3-lite", "xiaomi-3-lite-mjddhbc03zm-global", "Global")


if __name__ == "__main__":
    unittest.main()
