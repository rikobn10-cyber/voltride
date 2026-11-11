#!/usr/bin/env python3
"""Validate VoltRide's staged canonical model-data v2 dataset.

Uses only the Python standard library. The v2 dataset is a staged subset of exact variants
with adequate source evidence; legacy production consumers continue to read models.json
until the explicit-variant compatibility adapter and consumer tests are complete.
"""
import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "model_schema_v2.json"
DATA_PATH = ROOT / "model_data_v2.json"
STATUSES = {"verified_variant", "provisional", "variant_unresolved", "source_conflict", "excluded"}
CONFIDENCE = {"high", "medium", "low", "unrated"}
SOURCE_TYPES = {"official_product_page", "official_manual", "official_support_page",
                "official_regulatory_document", "authorized_retailer", "other"}
SOURCE_FIELDS = {"identity", "battery", "motors", "speed", "rangeClaim", "dimensions", "weight", "other"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(errors, path, message):
    errors.append(f"{path}: {message}")


def valid_date(value):
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def positive_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def validate_dataset(data):
    errors = []
    if not isinstance(data, dict) or set(data) != {"schemaVersion", "models"}:
        return ["$: expected exactly schemaVersion and models"]
    if data["schemaVersion"] != 2:
        fail(errors, "$.schemaVersion", "must equal 2")
    if not isinstance(data["models"], list):
        return errors + ["$.models: must be an array"]

    model_ids, variant_ids = set(), set()
    for mi, model in enumerate(data["models"]):
        p = f"$.models[{mi}]"
        if not isinstance(model, dict):
            fail(errors, p, "must be an object")
            continue
        required = {"id", "name", "manufacturer", "category", "variants"}
        if not required.issubset(model):
            fail(errors, p, f"missing keys: {sorted(required - set(model))}")
            continue
        if set(model) != required:
            fail(errors, p, f"unexpected keys: {sorted(set(model) - required)}")
        mid = model["id"]
        if not isinstance(mid, str) or not ID_RE.fullmatch(mid):
            fail(errors, p + ".id", "must be a lowercase kebab-case stable ID")
        elif mid in model_ids:
            fail(errors, p + ".id", "duplicate model ID")
        if isinstance(mid, str) and ID_RE.fullmatch(mid):
            model_ids.add(mid)
        for key in ("name", "manufacturer"):
            if not isinstance(model[key], str) or not model[key].strip():
                fail(errors, p + "." + key, "must be a non-empty string")
        if not isinstance(model["category"], str) or model["category"] not in {"budget", "commuter", "sport", "performance"}:
            fail(errors, p + ".category", "unsupported category")
        if not isinstance(model["variants"], list):
            fail(errors, p + ".variants", "must be an array")
            continue

        for vi, variant in enumerate(model["variants"]):
            q = f"{p}.variants[{vi}]"
            if not isinstance(variant, dict):
                fail(errors, q, "must be an object")
                continue
            keys = {"variantId", "market", "battery", "motors", "speed",
                    "rangeClaim", "sources", "verification"}
            if not keys.issubset(variant):
                fail(errors, q, f"missing keys: {sorted(keys - set(variant))}")
                continue
            allowed_variant_keys = keys | {"generation", "sku"}
            if not set(variant).issubset(allowed_variant_keys):
                fail(errors, q, f"unexpected keys: {sorted(set(variant) - allowed_variant_keys)}")
            vid = variant["variantId"]
            if not isinstance(vid, str) or not ID_RE.fullmatch(vid):
                fail(errors, q + ".variantId", "must be a lowercase kebab-case ID")
            elif vid in variant_ids:
                fail(errors, q + ".variantId", "duplicate variant ID")
            if isinstance(vid, str) and ID_RE.fullmatch(vid):
                variant_ids.add(vid)
            market = variant["market"]
            if not isinstance(market, list) or not market or any(not isinstance(x, str) or len(x) < 2 for x in market) or (all(isinstance(x, str) for x in market) and len(set(market)) != len(market)):
                fail(errors, q + ".market", "must be a non-empty array of unique market codes")

            battery = variant["battery"]
            if not isinstance(battery, dict):
                fail(errors, q + ".battery", "must be an object")
                battery = {}
            elif not set(battery).issubset({"nominalVoltageV", "capacityAh", "energyWh", "energyWhBasis", "energyWhSourceNote"}):
                fail(errors, q + ".battery", "contains unsupported keys")
            for key in ("nominalVoltageV", "capacityAh"):
                value = battery.get(key)
                if value is not None and not positive_number(value):
                    fail(errors, q + ".battery." + key, "must be null or a positive number")
            basis = battery.get("energyWhBasis")
            energy = battery.get("energyWh")
            if not isinstance(basis, str) or basis not in {"manufacturer_published", "calculated_from_nominal_values", "unresolved"}:
                fail(errors, q + ".battery.energyWhBasis", "unsupported basis")
            if basis == "unresolved" and energy is not None:
                fail(errors, q + ".battery.energyWh", "must be null when basis is unresolved")
            if basis in {"manufacturer_published", "calculated_from_nominal_values"} and not positive_number(energy):
                fail(errors, q + ".battery.energyWh", "must be positive for a resolved basis")
            if basis == "calculated_from_nominal_values":
                v, ah = battery.get("nominalVoltageV"), battery.get("capacityAh")
                if not positive_number(v) or not positive_number(ah):
                    fail(errors, q + ".battery.energyWhBasis", "calculated Wh requires known nominal voltage and capacity")
                elif positive_number(energy) and abs(energy - v * ah) / (v * ah) > 0.02:
                    fail(errors, q + ".battery.energyWh", "calculated Wh must match nominal voltage × Ah within 2%")

            motors = variant["motors"]
            if not isinstance(motors, dict):
                fail(errors, q + ".motors", "must be an object")
                motors = {}
            elif set(motors) != {"count", "ratedPowerW", "ratedPowerBasis", "peakPowerW", "peakPowerBasis"}:
                fail(errors, q + ".motors", "must contain exactly count and rated/peak power with explicit bases")
            motor_count = motors.get("count")
            if motor_count is not None and (not isinstance(motor_count, int) or isinstance(motor_count, bool) or motor_count < 1):
                fail(errors, q + ".motors.count", "must be null or a positive integer")
            for key, basis_key in (("ratedPowerW", "ratedPowerBasis"), ("peakPowerW", "peakPowerBasis")):
                value, power_basis = motors.get(key), motors.get(basis_key)
                if value is not None and not positive_number(value):
                    fail(errors, q + ".motors." + key, "must be null or a positive number")
                if not isinstance(power_basis, str) or power_basis not in {"per_motor", "combined", "unresolved"}:
                    fail(errors, q + ".motors." + basis_key, "unsupported power basis")
                if value is None and power_basis != "unresolved":
                    fail(errors, q + ".motors." + basis_key, "must be unresolved when power is unknown")
                if value is not None and power_basis == "unresolved":
                    fail(errors, q + ".motors." + basis_key, "must identify per_motor or combined when power is supplied")

            speed = variant["speed"]
            if not isinstance(speed, dict) or set(speed) != {"maxKmh", "conditions"}:
                fail(errors, q + ".speed", "must contain exactly maxKmh and conditions")
            else:
                if speed["maxKmh"] is not None and not positive_number(speed["maxKmh"]):
                    fail(errors, q + ".speed.maxKmh", "must be null or positive")
                if not isinstance(speed["conditions"], str) or not speed["conditions"].strip():
                    fail(errors, q + ".speed.conditions", "must state factory/unlocked or other conditions")

            claim = variant["rangeClaim"]
            if not isinstance(claim, dict) or set(claim) != {"maxKm", "basis", "conditions"}:
                fail(errors, q + ".rangeClaim", "must contain exactly maxKm, basis and conditions")
            else:
                if claim["maxKm"] is not None and not positive_number(claim["maxKm"]):
                    fail(errors, q + ".rangeClaim.maxKm", "must be null or positive")
                if claim["basis"] != "manufacturer_claim":
                    fail(errors, q + ".rangeClaim.basis", "must be manufacturer_claim")
                if not isinstance(claim["conditions"], str) or not claim["conditions"].strip():
                    fail(errors, q + ".rangeClaim.conditions", "must describe test conditions or state unknown")

            sources = variant["sources"]
            if not isinstance(sources, list) or not sources:
                fail(errors, q + ".sources", "must contain at least one evidence source")
                sources = []
            source_support = set()
            for si, source in enumerate(sources):
                z = f"{q}.sources[{si}]"
                if not isinstance(source, dict):
                    fail(errors, z, "must be an object")
                    continue
                expected = {"url", "publisher", "sourceType", "supports", "checkedAt"}
                if set(source) != expected:
                    fail(errors, z, "must contain exactly url, publisher, sourceType, supports and checkedAt")
                url = source.get("url", "")
                parsed = urlparse(url) if isinstance(url, str) else None
                if not parsed or parsed.scheme != "https" or not parsed.netloc:
                    fail(errors, z + ".url", "must be an absolute HTTPS URL")
                if not isinstance(source.get("publisher"), str) or not source["publisher"].strip():
                    fail(errors, z + ".publisher", "must be non-empty")
                if not isinstance(source.get("sourceType"), str) or source.get("sourceType") not in SOURCE_TYPES:
                    fail(errors, z + ".sourceType", "unsupported source type")
                supports = source.get("supports")
                if not isinstance(supports, list) or not supports or any(not isinstance(x, str) for x in supports) or (all(isinstance(x, str) for x in supports) and len(set(supports)) != len(supports)) or any(isinstance(x, str) and x not in SOURCE_FIELDS for x in supports):
                    fail(errors, z + ".supports", "must be a non-empty unique array of supported field names")
                else:
                    source_support.update(supports)
                if not valid_date(source.get("checkedAt")):
                    fail(errors, z + ".checkedAt", "must be an ISO date")

            verification = variant["verification"]
            if not isinstance(verification, dict) or set(verification) != {"status", "confidence", "checkedAt", "notes"}:
                fail(errors, q + ".verification", "must contain exactly status, confidence, checkedAt and notes")
            else:
                status = verification["status"]
                if not isinstance(status, str) or status not in STATUSES:
                    fail(errors, q + ".verification.status", "unsupported verification status")
                if not isinstance(verification["confidence"], str) or verification["confidence"] not in CONFIDENCE:
                    fail(errors, q + ".verification.confidence", "unsupported confidence")
                if not valid_date(verification["checkedAt"]):
                    fail(errors, q + ".verification.checkedAt", "must be an ISO date")
                if not isinstance(verification["notes"], list) or any(not isinstance(x, str) for x in verification["notes"]):
                    fail(errors, q + ".verification.notes", "must be an array of strings")
                if status == "verified_variant":
                    required_evidence = {"identity", "battery", "motors", "speed"}
                    if not required_evidence.issubset(source_support):
                        fail(errors, q + ".sources", "verified variants need source coverage for identity, battery, motors and speed")
                    if verification["confidence"] != "high":
                        fail(errors, q + ".verification.confidence", "verified_variant requires high confidence")
                    if (not positive_number(battery.get("nominalVoltageV")) or
                        not positive_number(battery.get("capacityAh")) or
                        battery.get("energyWhBasis") == "unresolved" or
                        motor_count is None or
                        not positive_number(motors.get("ratedPowerW")) or
                        motors.get("ratedPowerBasis") == "unresolved" or
                        not isinstance(speed, dict) or speed.get("maxKmh") is None):
                        fail(errors, q + ".verification", "verified variants require resolved battery, rated motor power/count, and speed")

    return errors


def self_test():
    valid = {
        "schemaVersion": 2,
        "models": [{
            "id": "test-model", "name": "Test Model", "manufacturer": "Test", "category": "commuter",
            "variants": [{
                "variantId": "test-model-eu-2026", "market": ["EU"],
                "battery": {"nominalVoltageV": 36, "capacityAh": 10, "energyWh": 360, "energyWhBasis": "calculated_from_nominal_values"},
                "motors": {"count": 1, "ratedPowerW": 350, "ratedPowerBasis": "combined", "peakPowerW": None, "peakPowerBasis": "unresolved"},
                "speed": {"maxKmh": 25, "conditions": "Factory EU configuration"},
                "rangeClaim": {"maxKm": 40, "basis": "manufacturer_claim", "conditions": "Manufacturer test conditions"},
                "sources": [{"url": "https://manufacturer.example/specs", "publisher": "Manufacturer", "sourceType": "official_product_page", "supports": ["identity", "battery", "motors", "speed", "rangeClaim"], "checkedAt": "2026-11-10"}],
                "verification": {"status": "verified_variant", "confidence": "high", "checkedAt": "2026-11-10", "notes": []}
            }]
        }]
    }
    assert validate_dataset(valid) == [], "valid exact-variant fixture should pass"
    bad = json.loads(json.dumps(valid))
    bad["models"][0]["variants"][0]["battery"]["energyWhBasis"] = "unresolved"
    assert validate_dataset(bad), "unresolved Wh with a value must fail"
    bad = json.loads(json.dumps(valid))
    bad["models"][0]["variants"][0]["motors"]["ratedPowerBasis"] = "per_motor"
    bad["models"][0]["variants"][0]["motors"]["count"] = 2
    assert validate_dataset(bad) == [], "explicit per-motor rating must remain valid"
    bad["models"][0]["variants"][0]["verification"]["status"] = "variant_unresolved"
    bad["models"][0]["variants"][0]["verification"]["confidence"] = "low"
    bad["models"][0]["variants"][0]["sources"][0]["supports"] = ["battery"]
    assert validate_dataset(bad) == [], "unresolved variants may retain partial evidence"
    bad["models"][0]["variants"][0]["verification"]["status"] = "verified_variant"
    assert validate_dataset(bad), "verified status without evidence coverage must fail"
    partial = json.loads(json.dumps(valid))
    partial_variant = partial["models"][0]["variants"][0]
    partial_variant["battery"]["nominalVoltageV"] = None
    partial_variant["battery"]["capacityAh"] = None
    partial_variant["battery"]["energyWh"] = None
    partial_variant["battery"]["energyWhBasis"] = "unresolved"
    partial_variant["motors"]["count"] = None
    partial_variant["motors"]["ratedPowerW"] = None
    partial_variant["motors"]["ratedPowerBasis"] = "unresolved"
    partial_variant["speed"]["maxKmh"] = None
    partial_variant["verification"]["status"] = "variant_unresolved"
    partial_variant["verification"]["confidence"] = "low"
    assert validate_dataset(partial) == [], "unresolved variants must support null measurements without guessed values"

    bad = json.loads(json.dumps(valid))
    bad["models"][0]["variants"][0]["motors"]["ratedPowerW"] = None
    assert validate_dataset(bad), "verified variants must not omit rated motor power"

    bad = json.loads(json.dumps(valid))
    bad["models"][0]["variants"][0]["battery"]["nominalVoltageV"] = None
    bad["models"][0]["variants"][0]["battery"]["energyWhBasis"] = "calculated_from_nominal_values"
    assert validate_dataset(bad), "calculated Wh must not be accepted without both nominal inputs"

    bad = json.loads(json.dumps(valid))
    bad["models"][0]["variants"][0]["sources"][0]["sourceType"] = []
    assert validate_dataset(bad), "malformed enum values must fail cleanly"

    print("Schema v2 validator self-tests passed.")


def main():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or schema.get("properties", {}).get("schemaVersion", {}).get("const") != 2:
        raise SystemExit("Schema document is missing the expected JSON Schema 2020-12 / version 2 contract.")
    self_test()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    errors = validate_dataset(data)
    if errors:
        print("Model data v2 validation failed:", file=sys.stderr)
        print("\n".join("- " + error for error in errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"Model data v2 validation passed: {len(data['models'])} canonical models, {sum(len(m['variants']) for m in data['models'])} variants.")
    if not data["models"]:
        print("No variants migrated yet; legacy models.json remains authoritative for production consumers.")


if __name__ == "__main__":
    main()
