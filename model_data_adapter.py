"""Explicit-variant projection from canonical model-data v2 to legacy spec fields.

This module is a staged compatibility boundary. It does not change production
consumers or choose a default variant: callers must provide both variant ID
and market, and only high-confidence verified variants may be projected.
"""
from __future__ import annotations


class VariantProjectionError(ValueError):
    """Raised when a v2 variant cannot be safely represented by legacy fields."""


def project_verified_variant(dataset: dict, model_id: str, variant_id: str, market: str) -> dict:
    if not isinstance(dataset, dict) or dataset.get("schemaVersion") != 2:
        raise VariantProjectionError("Unsupported model-data schema")
    if not all(isinstance(x, str) and x.strip() for x in (model_id, variant_id, market)):
        raise VariantProjectionError("model_id, variant_id and market are required explicitly")

    models = [m for m in dataset.get("models", []) if m.get("id") == model_id]
    if len(models) != 1:
        raise VariantProjectionError(f"Expected exactly one model record for {model_id}")
    model = models[0]
    variants = [v for v in model.get("variants", []) if v.get("variantId") == variant_id]
    if len(variants) != 1:
        raise VariantProjectionError(f"Expected exactly one variant {variant_id} for {model_id}")
    variant = variants[0]

    if market not in variant.get("market", []):
        raise VariantProjectionError(f"Variant {variant_id} is not verified for market {market}")
    verification = variant.get("verification", {})
    if verification.get("status") != "verified_variant" or verification.get("confidence") != "high":
        raise VariantProjectionError("Only high-confidence verified variants may be projected")

    battery = variant.get("battery", {})
    motors = variant.get("motors", {})
    speed = variant.get("speed", {})
    claim = variant.get("rangeClaim", {})
    sources = variant.get("sources", [])
    required_support = {"identity", "battery", "motors", "speed"}
    source_support = {field for source in sources for field in source.get("supports", [])}
    if not required_support.issubset(source_support):
        raise VariantProjectionError("Source evidence does not cover identity, battery, motors and speed")

    voltage = battery.get("nominalVoltageV")
    capacity = battery.get("capacityAh")
    energy = battery.get("energyWh")
    if not all(isinstance(x, (int, float)) and x > 0 for x in (voltage, capacity, energy)):
        raise VariantProjectionError("Verified battery voltage, capacity and energy are required")
    if battery.get("energyWhBasis") == "unresolved":
        raise VariantProjectionError("Unresolved battery energy cannot be projected")

    rated = motors.get("ratedPowerW")
    count = motors.get("count")
    basis = motors.get("ratedPowerBasis")
    if not isinstance(rated, (int, float)) or rated <= 0:
        raise VariantProjectionError("Rated motor power is required; peak power is not a substitute")
    if not isinstance(count, int) or count < 1:
        raise VariantProjectionError("Motor count is required")
    if basis == "combined":
        combined_rated = rated
    elif basis == "per_motor":
        combined_rated = rated * count
    else:
        raise VariantProjectionError("Rated motor power basis must be explicit")

    max_speed = speed.get("maxKmh")
    if not isinstance(max_speed, (int, float)) or max_speed <= 0:
        raise VariantProjectionError("A market-specific maximum speed is required")

    return {
        "legacy_fields": {
            "id": model["id"],
            "name": model["name"],
            "category": model["category"],
            "voltage": voltage,
            "ah": capacity,
            "motor": combined_rated,
            "speed": max_speed,
        },
        "range_claim": {
            "max_km": claim.get("maxKm"),
            "basis": claim.get("basis"),
            "conditions": claim.get("conditions"),
        },
        "provenance": {
            "variant_id": variant_id,
            "market": market,
            "verification": verification,
            "sources": sources,
            "battery_energy_wh": energy,
            "battery_energy_basis": battery.get("energyWhBasis"),
            "rated_power_basis": basis,
            "motor_count": count,
        },
    }
