"""
model.py
========
Techno-Economic Analysis (TEA) engine for post-combustion CO₂ capture.

Methodology:
  CAPEX  — factored cost estimate using NETL reference plant scaled by the
            six-tenths rule (cost ∝ capacity^0.6), adjusted per solvent.
  OPEX   — bottom-up: energy, solvent makeup, labor, maintenance, water, insurance.
  Output — levelised cost of CO₂ capture ($/tonne CO₂).

Reference plant: 500 tonne CO₂/day (post-combustion, coal-fired power plant context)
Capital costs sourced from: NETL DOE/NETL-2019/2041 (Table 3-3, adjusted to 2024 USD)
"""

import json
import math
from pathlib import Path

from solvents import get_solvent, SOLVENTS

# ── Constants ─────────────────────────────────────────────────────────────────

REFERENCE_CAPACITY_TPD = 500      # tonne CO₂/day — NETL reference scale
SCALE_EXPONENT         = 0.60     # six-tenths rule for process plant scaling
AVAILABILITY_FACTOR    = 0.90     # fraction of year plant operates at full load
INDIRECT_COST_FACTOR   = 0.30    # EPC + contingency as fraction of direct CAPEX
MAINTENANCE_RATE       = 0.025    # annual maintenance as fraction of total CAPEX
INSURANCE_RATE         = 0.005    # annual insurance as fraction of total CAPEX
WATER_COST_PER_TCO2    = 1.50    # USD / tonne CO₂ (cooling water + treatment)

# NETL reference direct CAPEX components at 500 tpd (USD million, 2024)
# Source: DOE/NETL-2019/2041 Table 3-3, escalated ~15% to 2024 USD
_REF_CAPEX_MUSD = {
    "absorber":        20.0,   # absorber column + internals + auxiliaries
    "regenerator":     32.0,   # stripper + reboiler
    "heat_exchangers": 14.0,   # lean-rich HX, condenser, intercoolers
    "compression":     34.0,   # CO₂ compression train to 150 bar
    "utilities":       17.0,   # pumps, fans, instrumentation, piping
    "civil":            9.0,   # civil works, buildings, foundations
}
_REF_CAPEX_DIRECT = sum(_REF_CAPEX_MUSD.values())  # ~126 M USD at reference scale


# ── Core TEA calculation ───────────────────────────────────────────────────────

def calculate(
    solvent: str,
    capacity_tpd: float,
    capture_rate: float,
    energy_price: float,
    electricity_price: float,
    discount_rate: float,
    plant_life: int,
) -> dict:
    """
    Calculate levelised cost of CO₂ capture.

    Parameters
    ----------
    solvent           : one of "MEA", "Piperazine", "K2CO3"
    capacity_tpd      : CO₂ captured per day (tonne/day), 100–5000
    capture_rate      : fraction of flue-gas CO₂ captured, 0.70–0.95
    energy_price      : thermal energy cost (USD/GJ)
    electricity_price : electricity cost for compression (USD/MWh)
    discount_rate     : weighted average cost of capital (fraction, e.g. 0.08)
    plant_life        : economic plant life (years)

    Returns
    -------
    dict with cost_per_tonne, breakdown, and supporting metrics
    """
    sol = get_solvent(solvent)

    # Clamp capture rate to solvent maximum
    capture_rate = min(capture_rate, sol["capture_efficiency_max"])

    # ── Annual CO₂ captured ───────────────────────────────────────────────────
    annual_co2 = capacity_tpd * 365.0 * AVAILABILITY_FACTOR   # tonnes/year

    # ── CAPEX ─────────────────────────────────────────────────────────────────
    sf = (capacity_tpd / REFERENCE_CAPACITY_TPD) ** SCALE_EXPONENT * sol["capex_factor"]

    capex_components_musd = {k: v * sf for k, v in _REF_CAPEX_MUSD.items()}
    direct_capex = sum(capex_components_musd.values()) * 1e6   # USD
    total_capex  = direct_capex * (1 + INDIRECT_COST_FACTOR)   # + EPC/contingency

    # Capital Recovery Factor
    r, n = discount_rate, plant_life
    crf = (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    annual_capex = total_capex * crf                           # USD/year

    # ── OPEX ──────────────────────────────────────────────────────────────────
    # Thermal energy for solvent regeneration
    energy_cost = annual_co2 * sol["regen_energy_gj_per_tco2"] * energy_price

    # Electricity for CO₂ compression
    compression_cost = annual_co2 * sol["compression_mwh_per_tco2"] * electricity_price

    # Solvent makeup (losses due to degradation / entrainment)
    solvent_cost = (
        annual_co2
        * sol["makeup_rate_kg_per_tco2"]
        * sol["solvent_cost_usd_per_kg"]
    )

    # Labor: base + logarithmic scale effect (larger plants need proportionally fewer workers)
    labor_cost = (900_000 + 250_000 * math.log10(max(capacity_tpd / 100, 1) + 1))

    # Maintenance (% of total CAPEX annually)
    maintenance_cost = total_capex * MAINTENANCE_RATE

    # Water treatment
    water_cost = annual_co2 * WATER_COST_PER_TCO2

    # Insurance (% of total CAPEX annually)
    insurance_cost = total_capex * INSURANCE_RATE

    annual_opex = (
        energy_cost + compression_cost + solvent_cost
        + labor_cost + maintenance_cost + water_cost + insurance_cost
    )

    # ── Levelised cost ────────────────────────────────────────────────────────
    total_annual = annual_capex + annual_opex
    cost_per_tonne = total_annual / annual_co2

    # Per-tonne breakdown
    def _pt(x):
        return round(x / annual_co2, 2)

    return {
        "solvent":             solvent,
        "capacity_tpd":        capacity_tpd,
        "capture_rate":        round(capture_rate, 3),
        "annual_co2_tonnes":   round(annual_co2),
        "cost_per_tonne":      round(cost_per_tonne, 2),
        "total_capex_musd":    round(total_capex / 1e6, 1),
        "crf":                 round(crf, 4),
        "annual_capex_musd":   round(annual_capex / 1e6, 2),
        "annual_opex_musd":    round(annual_opex / 1e6, 2),
        "breakdown": {
            "capex_annualized": _pt(annual_capex),
            "energy":           _pt(energy_cost),
            "compression":      _pt(compression_cost),
            "solvent":          _pt(solvent_cost),
            "labor":            _pt(labor_cost),
            "maintenance":      _pt(maintenance_cost),
            "water_insurance":  _pt(water_cost + insurance_cost),
        },
        "capex_components_musd": {
            k: round(v, 2) for k, v in capex_components_musd.items()
        },
        "inputs": {
            "energy_price":        energy_price,
            "electricity_price":   electricity_price,
            "discount_rate":       discount_rate,
            "plant_life":          plant_life,
        },
    }


# ── Sensitivity analysis ───────────────────────────────────────────────────────

def sensitivity(base_result: dict, swing: float = 0.20) -> dict:
    """
    Tornado sensitivity: vary each key input ±swing% and record cost impact.

    Returns dict of {parameter: {"low": cost_low, "high": cost_high, "swing": delta}}
    sorted by swing magnitude (largest first).
    """
    base_inputs = base_result["inputs"]
    base_cost   = base_result["cost_per_tonne"]

    params = {
        "Energy price ($/GJ)":        "energy_price",
        "Electricity price ($/MWh)":  "electricity_price",
        "Discount rate":              "discount_rate",
        "Plant life (years)":         "plant_life",
    }

    results = {}
    for label, key in params.items():
        base_val = base_inputs[key]
        lo_val = base_val * (1 - swing)
        hi_val = base_val * (1 + swing)

        def _recalc(val):
            inputs = {**base_inputs, key: val}
            # plant_life must be int
            if key == "plant_life":
                inputs["plant_life"] = max(5, round(val))
            r = calculate(
                solvent=base_result["solvent"],
                capacity_tpd=base_result["capacity_tpd"],
                capture_rate=base_result["capture_rate"],
                **inputs,
            )
            return r["cost_per_tonne"]

        cost_lo = _recalc(lo_val)
        cost_hi = _recalc(hi_val)

        results[label] = {
            "low":   round(cost_lo, 2),
            "base":  round(base_cost, 2),
            "high":  round(cost_hi, 2),
            "swing": round(cost_hi - cost_lo, 2),
        }

    # Plant capacity — must be handled separately (not in base_inputs)
    base_cap = base_result["capacity_tpd"]
    for cap_val, key2 in [(max(100, base_cap * (1 - swing)), "lo"),
                          (base_cap * (1 + swing),             "hi")]:
        pass  # computed below
    cost_lo_cap = calculate(
        solvent=base_result["solvent"],
        capacity_tpd=max(100, base_cap * (1 - swing)),
        capture_rate=base_result["capture_rate"],
        **base_inputs,
    )["cost_per_tonne"]
    cost_hi_cap = calculate(
        solvent=base_result["solvent"],
        capacity_tpd=base_cap * (1 + swing),
        capture_rate=base_result["capture_rate"],
        **base_inputs,
    )["cost_per_tonne"]
    results["Plant capacity (tpd)"] = {
        "low":   round(cost_lo_cap, 2),
        "base":  round(base_cost, 2),
        "high":  round(cost_hi_cap, 2),
        "swing": round(cost_hi_cap - cost_lo_cap, 2),
    }

    return dict(sorted(results.items(), key=lambda x: abs(x[1]["swing"]), reverse=True))


# ── Scale curve ────────────────────────────────────────────────────────────────

def scale_curve(
    base_result: dict,
    capacities: list[float] | None = None,
) -> dict[str, list]:
    """
    Cost vs. capacity for all three solvents at the same operating conditions.
    Returns {solvent: [cost_per_tonne, ...]} for each capacity in capacities.
    """
    if capacities is None:
        capacities = [100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000]

    inputs = base_result["inputs"]
    capture_rate = base_result["capture_rate"]

    curves: dict[str, list] = {"capacities": capacities}
    for sol_name in SOLVENTS:
        costs = []
        for cap in capacities:
            r = calculate(
                solvent=sol_name,
                capacity_tpd=cap,
                capture_rate=min(capture_rate, SOLVENTS[sol_name]["capture_efficiency_max"]),
                **inputs,
            )
            costs.append(round(r["cost_per_tonne"], 2))
        curves[sol_name] = costs

    return curves


# ── Solvent comparison at fixed conditions ─────────────────────────────────────

def compare_solvents(
    capacity_tpd: float,
    capture_rate: float,
    energy_price: float,
    electricity_price: float,
    discount_rate: float,
    plant_life: int,
) -> dict[str, dict]:
    """Run TEA for all solvents at identical conditions."""
    results = {}
    for sol_name in SOLVENTS:
        results[sol_name] = calculate(
            solvent=sol_name,
            capacity_tpd=capacity_tpd,
            capture_rate=min(capture_rate, SOLVENTS[sol_name]["capture_efficiency_max"]),
            energy_price=energy_price,
            electricity_price=electricity_price,
            discount_rate=discount_rate,
            plant_life=plant_life,
        )
    return results


# ── Persistence ───────────────────────────────────────────────────────────────

_HERE      = Path(__file__).parent
_DATA_DIR  = _HERE / "data"
_DATA_DIR.mkdir(exist_ok=True)
RESULTS_PATH = _DATA_DIR / "results.json"


def save_results(results: dict) -> None:
    RESULTS_PATH.write_text(json.dumps(results, indent=2))


def load_results() -> dict | None:
    if RESULTS_PATH.exists():
        return json.loads(RESULTS_PATH.read_text())
    return None
