"""
solvents.py
===========
Solvent parameters sourced from published literature.

Sources:
  [1] NETL Report DOE/NETL-2019/2041 — Cost and Performance Baseline for Fossil Energy Plants
  [2] Rubin et al. (2015) — "The cost of CO2 capture and storage"
      Int J Greenhouse Gas Control 40: 378–400
  [3] Rochelle (2009) — "Amine Scrubbing for CO2 Capture" Science 325: 1652–1654
  [4] IEA GHG Programme (2004) — "Improvement in Power Generation with Post-Combustion
      Capture of CO2"
  [5] Bohloul et al. (2014) — "CO2 absorption using K2CO3/KHCO3 solution"
      Separation and Purification Technology
"""

SOLVENTS: dict[str, dict] = {
    "MEA": {
        "name": "Monoethanolamine (MEA)",
        "short": "MEA",
        "description": (
            "Industry benchmark for post-combustion capture. "
            "Widely deployed commercially. High reactivity with CO₂ but "
            "energy-intensive regeneration and prone to degradation."
        ),
        "concentration_wt": 30,              # wt% in aqueous solution
        "regen_energy_gj_per_tco2": 3.7,     # GJ / tonne CO₂  [2]
        "compression_mwh_per_tco2": 0.110,   # MWh / tonne CO₂ (to 150 bar) [1]
        "makeup_rate_kg_per_tco2": 1.50,     # kg solvent lost / tonne CO₂ [1]
        "solvent_cost_usd_per_kg": 1.50,     # USD/kg (bulk market)
        "capture_efficiency_max": 0.90,      # max achievable capture fraction
        "capex_factor": 1.00,                # relative to MEA reference plant
        "color": "#2196F3",                  # for charts
        "sources": "[1][2]",
    },
    "Piperazine": {
        "name": "Piperazine (PZ)",
        "short": "PZ",
        "description": (
            "Advanced amine with faster CO₂ absorption kinetics and lower "
            "regeneration energy than MEA. Higher solvent cost but smaller "
            "equipment footprint. Increasingly used in advanced capture plants."
        ),
        "concentration_wt": 40,
        "regen_energy_gj_per_tco2": 2.4,     # GJ / tonne CO₂  [3]
        "compression_mwh_per_tco2": 0.110,
        "makeup_rate_kg_per_tco2": 0.50,     # less degradation than MEA
        "solvent_cost_usd_per_kg": 2.50,
        "capture_efficiency_max": 0.95,
        "capex_factor": 1.05,                # slightly larger absorber
        "color": "#4CAF50",
        "sources": "[3][4]",
    },
    "K2CO3": {
        "name": "Potassium Carbonate (K₂CO₃)",
        "short": "K₂CO₃",
        "description": (
            "Low-cost inorganic solvent suited to high-temperature or high-CO₂ "
            "concentration flue gas streams. Slower kinetics than amines, often "
            "requires promoters (e.g., piperazine). Very low solvent cost."
        ),
        "concentration_wt": 30,
        "regen_energy_gj_per_tco2": 2.0,     # GJ / tonne CO₂  [5]
        "compression_mwh_per_tco2": 0.110,
        "makeup_rate_kg_per_tco2": 0.30,
        "solvent_cost_usd_per_kg": 0.50,
        "capture_efficiency_max": 0.85,      # lower max efficiency
        "capex_factor": 0.95,                # simpler materials (no amine corrosion)
        "color": "#FF9800",
        "sources": "[4][5]",
    },
}


def get_solvent(name: str) -> dict:
    """Return solvent parameters by name. Raises KeyError if not found."""
    if name not in SOLVENTS:
        raise KeyError(
            f"Unknown solvent '{name}'. Choose from: {list(SOLVENTS.keys())}"
        )
    return SOLVENTS[name]


def list_solvents() -> list[str]:
    return list(SOLVENTS.keys())
