# CCUS TEA — Carbon Capture Techno-Economic Analysis

A Python techno-economic analysis engine for post-combustion CO₂ capture plants, with a self-contained, interactive web dashboard.

**CCUS** = Carbon Capture, Utilization & Storage  **TEA** = Techno-Economic Analysis

---

## The problem this solves

The decision to build a carbon capture plant comes down to one number: the **Levelised Cost of Carbon Capture (LCOC)**, in dollars per tonne of CO₂. That single figure determines whether a project gets financed, qualifies for a subsidy, or gets shelved. Yet arriving at it normally means proprietary consulting models, dense NETL spreadsheets, and chemical-engineering knowledge most decision-makers don't have, and every "what if energy prices rise 20%?" means starting over.

**This tool collapses that into something anyone can interrogate in a browser, offline, in seconds.** It implements real DOE/NETL methodology, six-tenths scaling laws, capital recovery factors, and a bottom-up operating-cost build, then exposes it through live sliders and charts so the economics become explorable instead of opaque.

## The impact

- **Makes capture economics legible.** Drag a slider, watch every chart respond in real time, the full model is re-implemented in JavaScript and runs live in the browser, so users build intuition for *what drives* cost, not just the headline number.
- **Answers decision-grade questions:** which solvent wins (MEA vs Piperazine vs K₂CO₃), how plant size changes cost (economy-of-scale curve), and which assumption matters most (sensitivity tornado, which surfaces that **energy price dominates** , the real lever for cheap capture).
- **Grounded, not a toy.** Reference plant of 500 t/day (~$126M direct CAPEX), peer-reviewed solvent data, proper CRF and OPEX modelling.
- **Zero-friction to share.** Output is a single portable `dashboard.html`, no server, no dependencies, works offline, emailable.

**Scope:** this is a **screening tool**. It models capture cost only (not transport, storage, or utilization revenue), and uses literature-sourced reference figures, so it's for early viability assessment, not bankable cost estimates.

---

## Quick start

```bash
pip install -r requirements.txt

# Single calculation (rich terminal table)
python3 tea.py calculate --solvent MEA --capacity 500

# Compare all three solvents
python3 tea.py compare

# Sensitivity (tornado) analysis
python3 tea.py sensitivity

# Generate the interactive dashboard → report/dashboard.html
python3 tea.py report
```

Then open `report/dashboard.html` in any browser.

The model engine (`model.py` / `solvents.py`) uses only the Python standard library. The `typer` and `rich` dependencies are only for the CLI front-end.

---

## How it works

| File | Role |
|---|---|
| `solvents.py` | Solvent parameter data (NETL/DOE, Rubin et al., Rochelle, IEA GHG) |
| `model.py` | TEA engine — CAPEX (six-tenths rule), CRF, bottom-up OPEX, LCOC |
| `tea.py` | Typer CLI — `calculate`, `compare`, `sensitivity`, `report`, `serve` |
| `report.py` | Builds the self-contained interactive `dashboard.html` |

The cost model:

```
LCOC ($/tonne CO₂) = (Annualized CAPEX + Annual OPEX) / Annual CO₂ captured
```

CAPEX scales from the NETL reference plant by the six-tenths rule (`cost ∝ capacity^0.6`), is annualized via the Capital Recovery Factor, and OPEX is built bottom-up from regeneration energy, compression electricity, solvent makeup, labor, maintenance, water, and insurance.

See [WORKING_OF_PROJECT.md](WORKING_OF_PROJECT.md) for a full walkthrough of the methodology and the live-update architecture.

---

## Solvents compared

| Solvent | Regen. energy | Max capture | Cost/kg | Trait |
|---|---|---|---|---|
| MEA | 3.7 GJ/t | 90% | $1.50 | Industry standard |
| Piperazine (PZ) | 2.4 GJ/t | 95% | $2.50 | Lower energy, higher cost |
| K₂CO₃ | 2.0 GJ/t | 85% | $0.50 | Cheapest, slower kinetics |

---

## License

[MIT](LICENSE)
