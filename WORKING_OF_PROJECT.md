# CCUS TEA Dashboard — How It Works

A Python tool that models the economics of a carbon capture plant and produces a fully interactive, self-contained web dashboard.

**CCUS** = Carbon Capture, Utilization & Storage  
**TEA** = Techno-Economic Analysis  
**Key output** = LCOC (Levelised Cost of Carbon Capture) in $/tonne CO₂ — the single number energy companies and governments use to decide whether a carbon capture project is financially viable.

---

## Project Overview

The tool lets you choose a solvent, dial in plant size, energy prices, and financing assumptions, and instantly see how the economics shift. All output lives in a single portable `dashboard.html` file — no server, no dependencies, works offline and can be shared as an email attachment.

---

## File Structure

```
ccus_tea/
├── solvents.py              # Solvent parameter data (sourced from DOE/NETL literature)
├── model.py                 # TEA engine — all engineering/economics calculations
├── report.py                # Dashboard generator — builds dashboard.html
└── report/
    └── dashboard.html       # Generated output (open directly in browser)
```

> The process flow diagram is now rendered natively inside `dashboard.html` (themed SVG + HTML). The old bundled `Carbon Capture Flow.html` iframe has been removed.

---

## The Python Files

### `solvents.py` — Data Layer

A structured dictionary of physical and economic parameters for three industrial solvents, sourced from peer-reviewed literature (NETL/DOE, Rubin et al., Rochelle, IEA GHG Programme).

Each solvent stores:
- Regeneration energy (GJ/tonne CO₂)
- Compression electricity consumption (MWh/tonne CO₂)
- Solvent makeup rate and cost per kg
- Maximum achievable capture efficiency
- CAPEX scaling factor relative to the MEA reference plant

The three solvents compared:

| Solvent | Regen. Energy | Max Capture | Cost/kg | Key trait |
|---|---|---|---|---|
| MEA | 3.7 GJ/t | 90% | $1.50 | Industry standard |
| Piperazine (PZ) | 2.4 GJ/t | 95% | $2.50 | Lower energy, higher cost |
| K₂CO₃ | 2.0 GJ/t | 85% | $0.50 | Cheapest, slower kinetics |

> Physical data is completely separated from calculation logic — adding a new solvent is a single dictionary entry.

---

### `model.py` — Engineering/Economics Engine

The core of the project. Pure Python standard library (`math`, `json`, `pathlib`) — no pip installs. Implements real DOE/NETL engineering methodology. Has four public functions:

#### `calculate()` — Main TEA calculation

Given a solvent, plant size, capture rate, energy prices, discount rate, and plant life, returns the full cost picture in one pass:

**Step 1 — Annual CO₂ captured**
```
annual_CO₂ = capacity × 365 days × 0.90 (availability factor)
```

**Step 2 — CAPEX**
Starts from a NETL reference plant (500 t/day, 6 equipment components, ~$126M direct cost). Scales to the target size using the **six-tenths rule** — a standard chemical engineering scaling law:
```
scale_factor = (capacity / 500)^0.6 × solvent_capex_factor
```
The 0.6 exponent means costs grow sub-linearly with size — bigger plants are cheaper per unit of capacity. Adds 30% for EPC costs and contingency.

**Step 3 — Capital Recovery Factor (CRF)**
Converts the lump-sum CAPEX into an equivalent annual cost, like a mortgage:
```
CRF = r(1+r)^n / ((1+r)^n − 1)
```
where `r` = discount rate and `n` = plant life in years.

**Step 4 — OPEX (bottom-up)**
- Thermal energy for solvent regeneration
- Electricity for CO₂ compression to 150 bar
- Solvent makeup losses (degradation + entrainment)
- Labor — base + `log10(capacity)` scaling (bigger plants need proportionally fewer workers)
- Maintenance — 2.5% of total CAPEX per year
- Water treatment + insurance

**Step 5 — LCOC**
```
LCOC ($/tonne CO₂) = (Annual CAPEX + Annual OPEX) / Annual CO₂ captured
```

#### `sensitivity()` — Tornado Analysis
Varies each input (energy price, electricity price, discount rate, plant life, capacity) by ±20%, re-runs `calculate()` each time, and sorts results by impact magnitude. This produces the tornado chart — showing which lever moves the cost the most.

#### `scale_curve()`
Runs `calculate()` across 10 plant sizes (100 → 5,000 t/day) for all three solvents. Produces the Economy of Scale chart showing how cost falls as plant size grows.

#### `compare_solvents()`
Runs `calculate()` once per solvent at identical conditions for the side-by-side comparison bar chart.

---

### `report.py` — Dashboard Generator

Calls the model functions, embeds all results into a large HTML template string, and writes `dashboard.html` to disk.

```python
# Run with:
python3 -c "import report; report.generate()"
```

The dashboard is a **two-page layout** switched by a segmented control, defaulting to **Cost Analysis**:

**Cost Analysis page**
- **4 KPI cards:** Levelised Cost, Total CAPEX, CO₂ Captured, Annual OPEX, each colour-tinted (blue / indigo / green / slate) and updating live
- **4 Chart.js charts:** stacked cost breakdown, solvent comparison bars, economy of scale curves, sensitivity tornado
- **6 interactive sliders** plus a 3-way solvent segmented control (capacity, capture rate, energy price, electricity price, discount rate, plant life)

**Process Overview page**
- **Native Process Flow Diagram:** themed SVG/HTML (not an iframe), with clickable equipment units (A to F) that open detail popups, colour-coded stream lines, and a legend
- **5 numbered step cards** walking through the capture process

**Shared UI**
- **Info popups:** click any “i” or equipment unit; a modal scales in with a spring and fades out
- **Light/dark theme toggle:** fixed in the top-right corner, driven by CSS custom properties

---

## How the Sliders Work in Real Time

This is the most technically interesting part. The sliders are not reading from pre-computed lookup tables — **the entire Python model is re-implemented in JavaScript** and runs live in the browser.

`report.py` embeds a complete JS port of `model.py` — the same constants, same six-tenths rule, same CRF formula, same OPEX breakdown — directly in the HTML output.

**The chain on every slider movement:**

1. `oninput="update()"` fires on every pixel of drag
2. `update()` reads all 6 slider values simultaneously
3. `calc()` runs the full TEA model — same math as Python, in microseconds
4. `update()` then calls `calc()` ~44 more times to refresh every chart:
   - Comparison chart → 3 calls (one per solvent)
   - Scale curve → 30 calls (10 capacities × 3 solvents)
   - Sensitivity tornado → 10 calls (5 parameters × ±20%)
5. All 4 charts redraw instantly using `chart.update("none")` — the `"none"` argument disables Chart.js's transition animation so charts snap to new values rather than animating

**Why it's fast:** The model is pure arithmetic — no loops bigger than ~30 iterations, no network calls, no DOM queries in the hot path. ~44 floating-point calculations complete in under 1ms, well within a 16ms frame budget.

**The key design decision:** The project maintains two implementations of the same model — Python (authoritative, runs at generation time) and JavaScript (embedded in the HTML, runs hundreds of times per session during exploration). The Python version runs once; the JS version runs every time a slider moves.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Model engine | Python stdlib (`math`, `json`, `pathlib`) | Zero dependencies, pure logic |
| Dashboard output | Single HTML file | Portable, shareable, no server needed |
| Charts | Chart.js (CDN) | Only external dependency |
| Interactivity | Vanilla JS | No framework overhead |
| Styling | CSS custom properties + `backdrop-filter` glass | Light/dark theming and liquid-glass surfaces with minimal JS |
| Fonts | Google Fonts (IBM Plex Sans, IBM Plex Mono, Space Grotesk) | Clean technical type system |
| PFD diagram | Native themed SVG + HTML | Fully integrated, theme-aware, clickable equipment |
| Popup motion | Web Animations API | Spring scale-in / fade-out for info modals |

---

## The Elevator Pitch

> "I built a techno-economic analysis tool for industrial carbon capture plants. The Python engine implements real DOE/NETL engineering methodology — six-tenths scaling laws, capital recovery factors, bottom-up operating cost modelling — across three commercial solvents. It generates an interactive dashboard where sliders update every chart in real time because the full model is re-implemented in JavaScript and runs live in the browser. The output is a single portable HTML file — no server, no dependencies, works offline."

---

## Key Concepts

| Term | Plain English |
|---|---|
| **LCOC** | All-in cost to capture one tonne of CO₂ — the viability metric |
| **Six-tenths rule** | Cost ∝ capacity^0.6 — bigger plants are cheaper per unit; standard chemical engineering |
| **Capital Recovery Factor** | Converts lump-sum CAPEX into an annual cost, like a mortgage payment |
| **Tornado chart** | Ranks which input assumptions move the cost the most — energy price dominates |
| **Availability factor** | Plant runs at 90% of theoretical maximum (downtime, maintenance) |
| **EPC + contingency** | Engineering, procurement, construction overhead — adds 30% on top of equipment costs |
