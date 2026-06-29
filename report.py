"""
report.py
=========
Generates a self-contained, interactive HTML dashboard for the CCUS TEA tool.
All cost calculations are replicated in JavaScript so the file works offline
with no server: just open report/dashboard.html in a browser.
"""

from pathlib import Path

_HERE       = Path(__file__).parent
REPORT_DIR  = _HERE / "report"
REPORT_DIR.mkdir(exist_ok=True)
OUTPUT_PATH = REPORT_DIR / "dashboard.html"


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CCUS Techno-Economic Analysis</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {
    --bg:       #f0f4f8;
    --surface:  #ffffff;
    --border:   #e2e8f0;
    --divider:  #f1f5f9;
    --text:     #1e293b;
    --muted:    #64748b;
    --faint:    #94a3b8;
    --accent:   #2563eb;
    --accent-lt:#eff6ff;
    --green:    #16a34a;
    --green-lt: #f0fdf4;
    --mea:      #3b82f6;
    --pz:       #10b981;
    --k2co3:    #f59e0b;
    --shadow:   0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
    --shadow-md:0 4px 12px rgba(0,0,0,.08);
    --bg-grad:  radial-gradient(1000px 560px at 100% -5%, rgba(59,130,246,.22), transparent 60%),
                radial-gradient(900px 620px at -5% 105%, rgba(16,185,129,.16), transparent 58%),
                linear-gradient(160deg, #dde9fb 0%, #eef2f8 48%, #e7e0fa 100%);
    --sidebar-bg: #ffffff;
    --info-bg:   #e7edf5;
  }
  html[data-theme="dark"] {
    --bg:       #0d1117;
    --surface:  #171d26;
    --border:   rgba(148,163,184,.16);
    --divider:  #222b37;
    --text:     #e8edf4;
    --muted:    #9babbf;
    --faint:    #6b7b8f;
    --accent:   #6cb0ff;
    --accent-lt:rgba(108,176,255,.14);
    --green:    #3ddc97;
    --green-lt: rgba(61,220,151,.14);
    --mea:      #6cb0ff;
    --pz:       #3ddc97;
    --k2co3:    #f5b840;
    --shadow:   0 1px 3px rgba(0,0,0,.5), 0 1px 2px rgba(0,0,0,.35);
    --shadow-md:0 6px 18px rgba(0,0,0,.55);
    --bg-grad:  radial-gradient(1000px 560px at 100% -5%, rgba(108,176,255,.16), transparent 60%),
                radial-gradient(900px 620px at -5% 105%, rgba(61,220,151,.10), transparent 58%),
                linear-gradient(160deg, #0a0e14 0%, #0d1117 45%, #131628 100%);
    --sidebar-bg: #11161f;
    --info-bg:   #0f141d;
    color-scheme: dark;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    font-size: 13px;
    background: var(--bg-grad), var(--bg);
    background-attachment: fixed;
    color: var(--text);
    line-height: 1.5;
  }
  h1, h2, h3,
  .card-title, .card-header-text, .page-header,
  .kpi-value, .kpi-label, .modal-title, .step-title,
  .sidebar-section-label { font-family: 'Space Grotesk', system-ui, sans-serif; }
  code, pre, .mono { font-family: 'IBM Plex Mono', monospace; }

  /* ── Page shell ─────────────────────────────────────────────────────────── */
  .shell { position: relative; display: grid; grid-template-columns: 340px 1fr; min-height: 100vh; gap: 4px; }

  /* ── Sidebar ────────────────────────────────────────────────────────────── */
  .sidebar {
    background: var(--sidebar-bg);
    border: 1px solid var(--border);
    border-radius: 18px;
    margin: 16px 0 16px 16px;
    padding: 28px 22px;
    position: sticky; top: 16px; height: calc(100vh - 32px);
    overflow-y: auto;
    display: flex; flex-direction: column;
    box-shadow: var(--shadow);
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
  }
  /* scrollbar gutter matches the sidebar background on both sides of the thumb */
  .sidebar::-webkit-scrollbar { width: 8px; }
  .sidebar::-webkit-scrollbar-track { background: var(--sidebar-bg); }
  .sidebar::-webkit-scrollbar-thumb {
    background: var(--border); border-radius: 99px;
    border: 2px solid var(--sidebar-bg);
  }
  .sidebar-spacer { flex: 1; }
  .sidebar-brand { margin-bottom: 24px; }
  .brand-row { display: flex; align-items: center; gap: 11px; }
  .brand-mark {
    width: 36px; height: 36px; flex-shrink: 0; border-radius: 10px;
    background: linear-gradient(135deg, var(--accent), var(--pz));
    display: flex; align-items: center; justify-content: center;
    color: #fff; box-shadow: var(--shadow-md);
  }
  .brand-mark svg { width: 20px; height: 20px; }
  .sidebar-brand h1 {
    font-size: 17px; font-weight: 700; color: var(--text);
    letter-spacing: -0.01em; line-height: 1.3;
  }
  .sidebar-brand p {
    font-size: 13px; color: var(--muted); margin-top: 5px; line-height: 1.55;
  }

  .sidebar-section { margin-bottom: 22px; }
  .sidebar-section-label {
    font-size: 11.5px; font-weight: 700; text-transform: uppercase;
    letter-spacing: .07em; color: var(--faint); margin-bottom: 10px;
  }

  /* Solvent tabs */
  .solvent-tabs { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
  .stab {
    padding: 7px 6px; border-radius: 7px;
    border: 1.5px solid var(--border);
    background: transparent; color: var(--muted);
    font-size: 12.5px; font-weight: 600; font-family: inherit;
    cursor: pointer; text-align: center;
    transition: all .15s ease;
  }
  .stab:hover { border-color: var(--accent); color: var(--accent); }
  .stab.sel-mea   { background: var(--mea);   border-color: var(--mea);   color: #fff; }
  .stab.sel-pz    { background: var(--pz);    border-color: var(--pz);    color: #fff; }
  .stab.sel-k2co3 { background: var(--k2co3); border-color: var(--k2co3); color: #fff; }
  .solvent-info {
    margin-top: 8px; padding: 10px 12px;
    background: var(--info-bg); border: 1px solid var(--border); border-radius: 8px;
    font-size: 12.5px; color: var(--muted); line-height: 1.55;
  }
  .solvent-name {
    display: block; font-weight: 700; color: var(--text);
    font-size: 13px; margin-bottom: 6px;
  }
  .solvent-desc { list-style: none; margin: 0; padding: 0; }
  .solvent-desc li {
    position: relative; padding-left: 14px; margin-bottom: 6px;
  }
  .solvent-desc li:last-child { margin-bottom: 0; }
  .solvent-desc li::before {
    content: ""; position: absolute; left: 0; top: 7px;
    width: 5px; height: 5px; border-radius: 50%; background: var(--accent);
  }

  /* Sliders */
  .ctrl { margin-bottom: 14px; }
  .ctrl-label {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13px; color: var(--muted); margin-bottom: 7px;
  }
  .ctrl-label > span {
    font-weight: 600; color: var(--accent); font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    background: var(--accent-lt); padding: 3px 8px; border-radius: 6px;
    white-space: nowrap;
  }
  input[type=range] {
    width: 100%; height: 5px; cursor: pointer;
    appearance: none; -webkit-appearance: none;
    background: var(--border); border-radius: 99px; outline: none;
  }
  input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none; width: 14px; height: 14px;
    border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-lt);
    cursor: pointer;
  }

  .divider { border: none; border-top: 1px solid var(--border); margin: 18px 0; }

  /* ── Main content ───────────────────────────────────────────────────────── */
  .main { padding: 30px 30px 44px; display: flex; flex-direction: column; gap: 22px; }

  /* Page header */
  .page-header { display: flex; align-items: flex-start; justify-content: space-between; }
  .page-header h2 { font-size: 22px; font-weight: 700; letter-spacing: -.02em; }
  .page-header p  { font-size: 13px; color: var(--muted); margin-top: 4px; }
  .badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 12px; border-radius: 99px;
    background: var(--accent-lt); color: var(--accent);
    font-size: 12px; font-weight: 600; margin-right: 132px;
  }

  /* KPI row */
  .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
  .kpi {
    position: relative; overflow: hidden;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 20px 22px;
    box-shadow: var(--shadow);
    transition: transform .15s ease, box-shadow .15s ease;
  }
  .kpi:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
  /* accent strip on the headline (cost) card */
  .kpi.is-primary::before {
    content: ""; position: absolute; left: 0; top: 14px; bottom: 14px;
    width: 3px; border-radius: 0 3px 3px 0; background: var(--accent);
  }
  .kpi-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
  .kpi-label { font-size: 11.5px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
  .kpi-value { font-size: 29px; font-weight: 700; letter-spacing: -.025em; color: var(--text); line-height: 1; }
  .kpi-value.primary { color: var(--accent); }
  .kpi-value.green   { color: var(--green);  }
  .kpi-unit { font-size: 14px; font-weight: 700; letter-spacing: -.01em; margin-left: 7px; }
  .kpi-meta { font-size: 11.5px; color: var(--faint); margin-top: 9px; }

  /* Chart grid */
  .chart-grid    { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; }
  .chart-grid-3  { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 22px; }
  .card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 22px 24px;
    box-shadow: var(--shadow);
    transition: box-shadow .15s ease;
  }
  .card:hover { box-shadow: var(--shadow-md); }
  .card.span-2 { grid-column: span 2; }
  .card.span-3 { grid-column: span 3; }
  .card-title { font-size: 14.5px; font-weight: 600; color: var(--text); letter-spacing: -.01em; }
  .card-sub   { font-size: 12px; color: var(--muted); margin-top: 3px; }
  .chart-wrap { position: relative; }
  .chart-wrap.h200 { height: 230px; }
  .chart-wrap.h240 { height: 270px; }
  .chart-wrap.h180 { height: 210px; }

  /* Sources */
  .sources-bar {
    padding: 12px 18px; border: 1px solid var(--border);
    border-radius: 10px; background: var(--surface);
    font-size: 10.5px; color: var(--faint); line-height: 1.8;
  }
  .sources-bar strong { color: var(--muted); font-weight: 600; }

  /* ── Theme toggle ───────────────────────────────────────────────────────── */
  .theme-toggle {
    position: absolute; top: 18px; right: 20px; z-index: 50;
    display: flex; align-items: center; justify-content: center; gap: 7px;
    width: 118px; padding: 8px 12px;
    border: 1.5px solid var(--border); border-radius: 8px;
    background: var(--surface); color: var(--muted);
    font-size: 12px; font-weight: 500; font-family: inherit;
    cursor: pointer; transition: all .15s; box-shadow: var(--shadow);
  }
  .theme-toggle:hover { border-color: var(--accent); color: var(--accent); }
  .theme-toggle .icon { display: inline-flex; align-items: center; }

  /* ── Info button & popup ─────────────────────────────────────────────────── */
  .card-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 14px; }
  .card-header-text {}
  .info-btn {
    flex-shrink: 0; margin-left: 10px; margin-top: 1px;
    width: 18px; height: 18px; border-radius: 50%;
    border: 1.5px solid var(--border);
    background: transparent; color: var(--faint);
    font-size: 10px; font-weight: 700; font-family: inherit;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: all .15s; line-height: 1;
  }
  .info-btn:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-lt); }

  /* Modal overlay */
  .modal-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(15,23,42,.25); backdrop-filter: blur(2px);
    z-index: 100; align-items: center; justify-content: center;
  }
  .modal-overlay.open { display: flex; }
  .modal {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 26px 28px; max-width: 460px; width: 90%;
    box-shadow: 0 20px 60px rgba(0,0,0,.15); position: relative;
    animation: popIn .18s ease;
  }
  @keyframes popIn { from { opacity:0; transform:scale(.96) translateY(6px); } to { opacity:1; transform:none; } }
  .modal-title { font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 11px; }
  .modal-body  { font-size: 14px; color: var(--muted); line-height: 1.7; }
  .modal-body strong { color: var(--text); font-weight: 600; }
  .modal-close {
    position: absolute; top: 14px; right: 16px;
    width: 24px; height: 24px; border-radius: 50%;
    border: none; background: var(--divider); color: var(--muted);
    font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: background .15s;
  }
  .modal-close:hover { background: var(--border); }

  /* ── Page navigation ─────────────────────────────────────────────────────── */
  .page-nav { display:flex; gap:2px; margin-bottom:22px; border-bottom:1px solid var(--border); }
  #page-analysis, #page-overview { display:flex; flex-direction:column; gap:22px; }
  .page-tab {
    padding:8px 22px; font-size:12.5px; font-weight:600; font-family:inherit;
    border:none; background:transparent; color:var(--muted); cursor:pointer;
    border-bottom:2.5px solid transparent; margin-bottom:-1px; transition:all .15s;
  }
  .page-tab:hover { color:var(--text); }
  .page-tab.active { color:var(--accent); border-bottom-color:var(--accent); }

  /* ── PFD (new) ──────────────────────────────────────────────────────────────── */
  :root {
    --pfd-blue:#1f6feb; --pfd-teal:#0b9b8a; --pfd-heat:#e8590c; --pfd-power:#b07c08;
    --pfd-s-flue:#8b8f98; --pfd-s-clean:#2f9e44; --pfd-s-rich:#1f6feb;
    --pfd-s-lean:#0b9b8a; --pfd-s-co2:#8a4fce; --pfd-s-heat:#e8590c; --pfd-s-power:#b07c08;
    --pfd-stage-bg:#faf9f6; --pfd-stage-bd:#ddd9cf;
    --pfd-card-bg:#ffffff; --pfd-card-bd:#dbd7cf;
    --pfd-card-sh:0 1px 2px rgba(28,26,22,.05),0 8px 20px rgba(28,26,22,.05);
    --pfd-nm:#1b1a17; --pfd-ds:#78746c; --pfd-tray:#e7e3da;
  }
  html[data-theme="dark"] {
    --pfd-blue:#4d8dfb; --pfd-teal:#2ad4c4; --pfd-heat:#ff6b5d; --pfd-power:#f2c14e;
    --pfd-s-flue:#9aa0ab; --pfd-s-clean:#51cf66; --pfd-s-rich:#4d8dfb;
    --pfd-s-lean:#2ad4c4; --pfd-s-co2:#b483f0; --pfd-s-heat:#ff6b5d; --pfd-s-power:#f2c14e;
    --pfd-stage-bg:#15181d; --pfd-stage-bd:#262b33;
    --pfd-card-bg:#1c2027; --pfd-card-bd:#2c313b;
    --pfd-card-sh:0 0 0 1px rgba(255,255,255,.015),0 10px 28px rgba(0,0,0,.45);
    --pfd-nm:#edeff3; --pfd-ds:#8b919c; --pfd-tray:#2b3039;
  }
  .pfd-stage {
    position:relative; width:100%; aspect-ratio:1280/740;
    background:var(--pfd-stage-bg); border:1px solid var(--pfd-stage-bd);
    border-radius:12px; overflow:hidden; container-type:inline-size;
  }
  .s-flue  { stroke:var(--pfd-s-flue);  } .s-clean { stroke:var(--pfd-s-clean); }
  .s-rich  { stroke:var(--pfd-s-rich);  } .s-lean  { stroke:var(--pfd-s-lean);  }
  .s-co2   { stroke:var(--pfd-s-co2);   } .s-heat  { stroke:var(--pfd-s-heat);  }
  .s-power { stroke:var(--pfd-s-power); }
  .s-lbl { font-family:'IBM Plex Mono',monospace; font-size:15px; font-weight:600; letter-spacing:.03em; }
  .s-lbl-flue  { fill:var(--pfd-s-flue);  } .s-lbl-clean { fill:var(--pfd-s-clean); }
  .s-lbl-rich  { fill:var(--pfd-s-rich);  } .s-lbl-lean  { fill:var(--pfd-s-lean);  }
  .s-lbl-co2   { fill:var(--pfd-s-co2);   } .s-lbl-heat  { fill:var(--pfd-s-heat);  }
  .s-lbl-power { fill:var(--pfd-s-power); }
  .pfd-equip {
    position:absolute; box-sizing:border-box; border-radius:9px;
    background:var(--pfd-card-bg); border:1.5px solid var(--pfd-equip-accent,var(--pfd-blue));
    box-shadow:var(--pfd-card-sh); cursor:pointer;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    text-align:center; gap:0.35cqw; padding:0.8cqw; overflow:visible;
    transition:transform .15s, box-shadow .15s;
  }
  .pfd-equip:hover { transform:translateY(-2px); box-shadow:var(--pfd-card-sh),0 0 0 2px var(--pfd-equip-accent,var(--pfd-blue)); }
  .pfd-column {
    justify-content:flex-start; padding-top:1.4cqw;
    background-image:repeating-linear-gradient(to bottom,transparent 0%,transparent calc(16.67% - 0.5px),var(--pfd-tray) calc(16.67% - 0.5px),var(--pfd-tray) 16.67%);
    background-position:0 38%; background-size:100% 44%;
  }
  .pfd-badge {
    position:absolute; top:-1cqw; left:1cqw;
    width:2.1cqw; height:2.1cqw; min-width:18px; min-height:18px; border-radius:50%;
    background:var(--pfd-equip-accent,var(--pfd-blue)); color:#fff;
    display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:1.0cqw; font-family:'IBM Plex Mono',monospace;
    box-shadow:0 2px 6px rgba(0,0,0,.2);
  }
  .pfd-name { font-weight:700; font-size:1.45cqw; color:var(--pfd-nm); letter-spacing:-.01em; line-height:1.15; }
  .pfd-desc { font-size:0.95cqw; color:var(--pfd-ds); line-height:1.25; font-weight:500; }
  .pfd-blue  { --pfd-equip-accent:var(--pfd-blue);  }
  .pfd-teal  { --pfd-equip-accent:var(--pfd-teal);  }
  .pfd-heat  { --pfd-equip-accent:var(--pfd-heat);  }
  .pfd-power { --pfd-equip-accent:var(--pfd-power); }
  .pfd-legend { display:flex; flex-wrap:wrap; gap:8px 20px; justify-content:center; align-items:center; margin-top:14px; }
  .pfd-leg-item { display:flex; align-items:center; gap:7px; font-size:11px; color:var(--muted); font-weight:500; }
  .pfd-leg-sw { width:22px; display:block; }

  /* ── Step cards ──────────────────────────────────────────────────────────── */
  .step-row { display:grid; grid-template-columns:repeat(5,1fr); gap:14px; }
  .step-card {
    position:relative;
    background:var(--info-bg); border:1px solid var(--border);
    border-radius:14px; padding:18px 16px; box-shadow:var(--shadow);
    transition:transform .15s ease, box-shadow .15s ease;
  }
  .step-card:hover { transform:translateY(-2px); box-shadow:var(--shadow-md); }
  /* connector line between consecutive steps */
  .step-card:not(:first-child)::before {
    content:""; position:absolute; left:-14px; top:31px;
    width:14px; height:2px; background:var(--border);
  }
  .step-num {
    width:28px; height:28px; border-radius:9px;
    background:linear-gradient(135deg, var(--accent), var(--pz)); color:#fff;
    font-size:13px; font-weight:700; font-family:'Space Grotesk', system-ui, sans-serif;
    display:flex; align-items:center; justify-content:center;
    margin-bottom:11px; flex-shrink:0; box-shadow:var(--shadow);
  }
  .step-title { font-size:13.5px; font-weight:700; color:var(--text); margin-bottom:6px; letter-spacing:-.01em; }
  .step-body  { font-size:12px; color:var(--muted); line-height:1.6; }

  /* ── Responsive ─────────────────────────────────────────────────────────── */
  @media (max-width: 1100px) {
    .kpi-row { grid-template-columns: repeat(2, 1fr); }
  }
  @media (max-width: 900px) {
    .shell { grid-template-columns: 1fr; }
    .sidebar {
      position: static; height: auto; width: auto;
      margin: 16px; border: 1px solid var(--border);
    }
    .chart-grid, .chart-grid-3 { grid-template-columns: 1fr; }
    .card.span-2, .card.span-3 { grid-column: span 1; }
    .step-row { grid-template-columns: repeat(2, 1fr); }
    .step-card:not(:first-child)::before { display: none; }
  }
  @media (max-width: 560px) {
    .kpi-row { grid-template-columns: 1fr; }
    .step-row { grid-template-columns: 1fr; }
    .main { padding: 18px 16px 32px; }
  }
</style>
</head>
<body>
<div class="shell">

<!-- ── Sidebar ─────────────────────────────────────────────────────────────── -->
<aside class="sidebar">
  <div class="sidebar-brand">
    <div class="brand-row">
      <span class="brand-mark">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6"/></svg>
      </span>
      <h1>CCUS Techno-Economic<br>Analysis</h1>
    </div>
    <p>Levelised cost of post-combustion CO₂ capture: adjust parameters to explore configurations.</p>
  </div>

  <div class="sidebar-section">
    <div class="sidebar-section-label">Solvent</div>
    <div class="solvent-tabs">
      <button class="stab sel-mea" id="tab-MEA"        title="Monoethanolamine"      onclick="setSolvent('MEA')">MEA</button>
      <button class="stab"         id="tab-Piperazine"  title="Piperazine"            onclick="setSolvent('Piperazine')">PZ</button>
      <button class="stab"         id="tab-K2CO3"       title="Potassium Carbonate"   onclick="setSolvent('K2CO3')">K₂CO₃</button>
    </div>
    <div class="solvent-info" id="solvent-info"></div>
  </div>

  <hr class="divider">

  <div class="sidebar-section">
    <div class="sidebar-section-label">Plant Configuration</div>
    <div class="ctrl">
      <div class="ctrl-label">Capture capacity <span><span id="v-cap">500</span> t CO₂/day</span></div>
      <input type="range" id="capacity" min="100" max="5000" step="50" value="500" oninput="update()">
    </div>
    <div class="ctrl">
      <div class="ctrl-label">Capture rate <span><span id="v-cr">90</span>%</span></div>
      <input type="range" id="capture_rate" min="70" max="95" step="1" value="90" oninput="update()">
    </div>
  </div>

  <hr class="divider">

  <div class="sidebar-section">
    <div class="sidebar-section-label">Economic Assumptions</div>
    <div class="ctrl">
      <div class="ctrl-label">Thermal energy price <span>$<span id="v-ep">6.00</span>/GJ</span></div>
      <input type="range" id="energy_price" min="2" max="15" step="0.5" value="6" oninput="update()">
    </div>
    <div class="ctrl">
      <div class="ctrl-label">Electricity price <span>$<span id="v-elp">70</span>/MWh</span></div>
      <input type="range" id="electricity_price" min="30" max="200" step="5" value="70" oninput="update()">
    </div>
    <div class="ctrl">
      <div class="ctrl-label">Discount rate <span><span id="v-dr">8.0</span>%</span></div>
      <input type="range" id="discount_rate" min="4" max="14" step="0.5" value="8" oninput="update()">
    </div>
    <div class="ctrl">
      <div class="ctrl-label">Plant life <span><span id="v-pl">25</span> years</span></div>
      <input type="range" id="plant_life" min="15" max="35" step="1" value="25" oninput="update()">
    </div>
  </div>
  <div class="sidebar-spacer"></div>
</aside>

<!-- Theme toggle (fixed, top-right) -->
<button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark theme">
  <span class="icon" id="theme-icon"></span>
  <span id="theme-label">Dark Mode</span>
</button>

<!-- ── Main ────────────────────────────────────────────────────────────────── -->
<main class="main">

  <!-- Page navigation tabs -->
  <nav class="page-nav">
    <button class="page-tab active" data-page="analysis"  onclick="showPage('analysis')">Cost Analysis</button>
    <button class="page-tab"        data-page="overview" onclick="showPage('overview')">Process Overview</button>
  </nav>

  <!-- ════ PAGE 1: Process Overview ════════════════════════════════════════ -->
  <div id="page-overview" style="display:none;">

    <div class="page-header" >
      <div>
        <h2>Post-Combustion CO₂ Capture</h2>
        <p>How solvent-based carbon capture works: from flue gas to pipeline CO₂</p>
      </div>
    </div>

    <!-- PFD card -->
    <div class="card" >
      <div class="card-header">
        <div class="card-header-text">
          <div class="card-title">Process Flow Diagram</div>
          <div class="card-sub">Click any unit for details</div>
        </div>
      </div>

      <div class="pfd-stage">
        <!-- stream lines -->
        <svg class="pfd-streams" viewBox="0 0 1280 740" style="position:absolute;inset:0;width:100%;height:100%">
          <defs>
            <marker id="pfd-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
              <path d="M0,0 L10,5 L0,10 z" fill="context-stroke"></path>
            </marker>
          </defs>
          <g fill="none" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" marker-end="url(#pfd-arrow)">
            <path class="s-flue"  d="M30,460 H150"></path>
            <path class="s-clean" d="M235,150 V58"></path>
            <path class="s-rich"  d="M320,470 H430 V372 H520"></path>
            <path class="s-rich"  d="M685,345 H750 V215 H815"></path>
            <path class="s-lean"  d="M815,400 H685"></path>
            <path class="s-lean"  d="M602,430 V515"></path>
            <path class="s-lean"  d="M520,565 H400 V180 H320"></path>
            <path class="s-co2"   d="M905,140 V96 H1150 V115"></path>
            <path class="s-co2"   d="M1225,172 H1268"></path>
            <path class="s-heat"  d="M872,500 V560"></path>
            <path class="s-heat"  d="M938,560 V500"></path>
          </g>
          <text class="s-lbl s-lbl-flue"  x="34"   y="445">FLUE GAS</text>
          <text class="s-lbl s-lbl-clean" x="250"  y="92">CLEAN GAS</text>
          <text class="s-lbl s-lbl-rich"  x="338"  y="455">RICH</text>
          <text class="s-lbl s-lbl-lean"  x="408"  y="165">LEAN</text>
          <text class="s-lbl s-lbl-co2"   x="915"  y="118">CO₂</text>
          <text class="s-lbl s-lbl-co2"   x="1120" y="210">TO STORAGE</text>
          <text class="s-lbl s-lbl-heat"  x="965"  y="540">HEAT</text>
        </svg>

        <!-- equipment -->
        <div class="pfd-equip pfd-column pfd-teal" style="left:11.72%;top:20.27%;width:13.28%;height:56.76%" onclick="showInfo('pfd-absorber')">
          <span class="pfd-badge">1</span>
          <span class="pfd-name">Absorber</span>
          <span class="pfd-desc">CO₂ → solvent</span>
        </div>
        <div class="pfd-equip pfd-blue" style="left:40.63%;top:42.57%;width:12.89%;height:15.54%" onclick="showInfo('pfd-hx')">
          <span class="pfd-badge">2</span>
          <span class="pfd-name">Lean–Rich HX</span>
          <span class="pfd-desc">Heat recovery</span>
        </div>
        <div class="pfd-equip pfd-teal" style="left:40.63%;top:69.59%;width:12.89%;height:13.51%" onclick="showInfo('pfd-cooler')">
          <span class="pfd-badge">3</span>
          <span class="pfd-name">Lean Cooler</span>
          <span class="pfd-desc">Cools solvent</span>
        </div>
        <div class="pfd-equip pfd-column pfd-heat" style="left:63.67%;top:18.92%;width:14.06%;height:48.65%" onclick="showInfo('pfd-regenerator')">
          <span class="pfd-badge">4</span>
          <span class="pfd-name">Regenerator</span>
          <span class="pfd-desc">Strips CO₂</span>
        </div>
        <div class="pfd-equip pfd-heat" style="left:63.67%;top:75.68%;width:14.06%;height:12.84%" onclick="showInfo('pfd-reboiler')">
          <span class="pfd-badge">5</span>
          <span class="pfd-name">Reboiler</span>
          <span class="pfd-desc">Steam heat</span>
        </div>
        <div class="pfd-equip pfd-power" style="left:83.98%;top:15.54%;width:11.72%;height:15.54%" onclick="showInfo('pfd-compressor')">
          <span class="pfd-badge">6</span>
          <span class="pfd-name">CO₂ Compressor</span>
          <span class="pfd-desc">→ 150 bar</span>
        </div>
      </div>

      <!-- stream legend -->
      <div class="pfd-legend">
        <span class="pfd-leg-item"><svg class="pfd-leg-sw" height="8" viewBox="0 0 22 8"><line x1="0" y1="4" x2="22" y2="4" class="s-flue"  stroke-width="3"></line></svg>Flue gas</span>
        <span class="pfd-leg-item"><svg class="pfd-leg-sw" height="8" viewBox="0 0 22 8"><line x1="0" y1="4" x2="22" y2="4" class="s-clean" stroke-width="3"></line></svg>Clean gas</span>
        <span class="pfd-leg-item"><svg class="pfd-leg-sw" height="8" viewBox="0 0 22 8"><line x1="0" y1="4" x2="22" y2="4" class="s-rich"  stroke-width="3"></line></svg>Rich solvent</span>
        <span class="pfd-leg-item"><svg class="pfd-leg-sw" height="8" viewBox="0 0 22 8"><line x1="0" y1="4" x2="22" y2="4" class="s-lean"  stroke-width="3"></line></svg>Lean solvent</span>
        <span class="pfd-leg-item"><svg class="pfd-leg-sw" height="8" viewBox="0 0 22 8"><line x1="0" y1="4" x2="22" y2="4" class="s-co2"   stroke-width="3"></line></svg>CO₂</span>
        <span class="pfd-leg-item"><svg class="pfd-leg-sw" height="8" viewBox="0 0 22 8"><line x1="0" y1="4" x2="22" y2="4" class="s-heat"  stroke-width="3"></line></svg>Heat</span>
      </div>
    </div>

    <!-- Step cards -->
    <div class="step-row">
      <div class="step-card">
        <div class="step-num">1</div>
        <div class="step-title">Flue Gas Entry</div>
        <div class="step-body">Hot flue gas from combustion enters the base of the absorber. It contains 10-15% CO₂ by volume alongside N₂, O₂, and water vapour.</div>
      </div>
      <div class="step-card">
        <div class="step-num">2</div>
        <div class="step-title">CO₂ Absorption</div>
        <div class="step-body">Gas rises through packing material while liquid solvent falls from above. CO₂ reacts chemically with the solvent, producing a CO₂-rich solution. Clean gas exits the top.</div>
      </div>
      <div class="step-card">
        <div class="step-num">3</div>
        <div class="step-title">Solvent Regeneration</div>
        <div class="step-body">Rich solvent is heated in the regenerator by steam from the reboiler. Heat reverses the absorption reaction, releasing concentrated CO₂ and regenerating lean solvent for reuse.</div>
      </div>
      <div class="step-card">
        <div class="step-num">4</div>
        <div class="step-title">CO₂ Compression</div>
        <div class="step-body">Released CO₂ at near-atmospheric pressure is compressed to ~150 bar (supercritical state) in a multi-stage train. This requires ~0.11 MWh per tonne of CO₂ captured.</div>
      </div>
      <div class="step-card">
        <div class="step-num">5</div>
        <div class="step-title">Storage or Use</div>
        <div class="step-body">Supercritical CO₂ is transported by pipeline to geological storage (saline aquifer or depleted reservoir) or used as feedstock for synthetic fuels, chemicals, or enhanced oil recovery.</div>
      </div>
    </div>

  </div><!-- end page-overview -->

  <!-- ════ PAGE 2: Cost Analysis (hidden by default) ════════════════════════ -->
  <div id="page-analysis">

  <!-- Header -->
  <div class="page-header">
    <div>
      <h2>Cost of Carbon Capture</h2>
      <p>Post-combustion, solvent-based: parameters from NETL/IEA published literature</p>
    </div>
    <div class="badge" id="header-badge">MEA · 500 t/day</div>
  </div>

  <!-- KPIs -->
  <div class="kpi-row">
    <div class="kpi is-primary">
      <div class="kpi-header">
        <div class="kpi-label">Levelised Cost</div>
        <button class="info-btn" onclick="showInfo('kpi-cost')">i</button>
      </div>
      <div class="kpi-value primary" id="kpi-cost">-</div>
      <div class="kpi-meta">USD per tonne CO₂</div>
    </div>
    <div class="kpi">
      <div class="kpi-header">
        <div class="kpi-label">Total CAPEX</div>
        <button class="info-btn" onclick="showInfo('kpi-capex')">i</button>
      </div>
      <div class="kpi-value" id="kpi-capex">-</div>
      <div class="kpi-meta" id="kpi-crf">CRF:</div>
    </div>
    <div class="kpi">
      <div class="kpi-header">
        <div class="kpi-label">CO₂ Captured</div>
        <button class="info-btn" onclick="showInfo('kpi-co2')">i</button>
      </div>
      <div class="kpi-value green"><span id="kpi-co2">-</span><span class="kpi-unit">tonnes/yr</span></div>
      <div class="kpi-meta">Captured annually</div>
    </div>
    <div class="kpi">
      <div class="kpi-header">
        <div class="kpi-label">Annual OPEX</div>
        <button class="info-btn" onclick="showInfo('kpi-opex')">i</button>
      </div>
      <div class="kpi-value" id="kpi-opex">-</div>
      <div class="kpi-meta" id="kpi-energy-share">Energy:</div>
    </div>
  </div>

  <!-- Row 1: breakdown + comparison -->
  <div class="chart-grid">
    <div class="card">
      <div class="card-header">
        <div class="card-header-text">
          <div class="card-title">Cost Breakdown</div>
          <div class="card-sub">$/tonne CO₂ by component</div>
        </div>
        <button class="info-btn" onclick="showInfo('breakdown')">i</button>
      </div>
      <div class="chart-wrap h240"><canvas id="breakdownChart"></canvas></div>
    </div>
    <div class="card">
      <div class="card-header">
        <div class="card-header-text">
          <div class="card-title">Solvent Comparison</div>
          <div class="card-sub">All solvents at current configuration</div>
        </div>
        <button class="info-btn" onclick="showInfo('comparison')">i</button>
      </div>
      <div class="chart-wrap h240"><canvas id="comparisonChart"></canvas></div>
    </div>
  </div>

  <!-- Row 2: scale curve (full width) -->
  <div class="card">
    <div class="card-header">
      <div class="card-header-text">
        <div class="card-title">Economy of Scale</div>
        <div class="card-sub">Levelised cost vs. plant capacity for all three solvents: current operating conditions</div>
      </div>
      <button class="info-btn" onclick="showInfo('scale')">i</button>
    </div>
    <div class="chart-wrap h200"><canvas id="scaleChart"></canvas></div>
  </div>

  <!-- Row 3: sensitivity (full width) -->
  <div class="card">
    <div class="card-header">
      <div class="card-header-text">
        <div class="card-title">Sensitivity Analysis</div>
        <div class="card-sub">Impact of ±20% change in each input on $/tonne CO₂: ranked by influence</div>
      </div>
      <button class="info-btn" onclick="showInfo('sensitivity')">i</button>
    </div>
    <div class="chart-wrap h180"><canvas id="sensitivityChart"></canvas></div>
  </div>

  <!-- Info modal -->
  <div class="modal-overlay" id="modal-overlay" onclick="closeInfo(event)">
    <div class="modal">
      <button class="modal-close" onclick="hideInfo()">✕</button>
      <div class="modal-title" id="modal-title"></div>
      <div class="modal-body"  id="modal-body"></div>
    </div>
  </div>

  <!-- Sources -->
  <div class="sources-bar">
    <strong>Data sources:</strong>
    [1] NETL DOE/NETL-2019/2041 &nbsp;·&nbsp;
    [2] Rubin et al. (2015) Int J Greenhouse Gas Control 40: 378-400 &nbsp;·&nbsp;
    [3] Rochelle (2009) Science 325: 1652-1654 &nbsp;·&nbsp;
    [4] IEA GHG Programme Report PH4/33 (2004) &nbsp;·&nbsp;
    [5] Bohloul et al. (2014) Sep. Purif. Technol.
  </div>

  </div><!-- end page-analysis -->

</main>
</div>

<script>
// ── Solvent data ──────────────────────────────────────────────────────────────
const SOLVENTS = {
  MEA: {
    name:"Monoethanolamine (MEA)", short:"MEA",
    desc:[
      "It is the industry benchmark solvent, deployed in nearly every commercial post-combustion capture plant to date.",
      "Its high reactivity comes at the cost of energy-intensive regeneration and faster solvent degradation.",
    ],
    regen:3.7, comp_mwh:0.110, makeup:1.50, sol_cost:1.50,
    cap_max:0.90, capex_f:1.00, color:"#3b82f6",
  },
  Piperazine: {
    name:"Piperazine (PZ)", short:"PZ",
    desc:[
      "Piperazine is an advanced amine with faster CO₂ absorption kinetics and about 35% lower regeneration energy than MEA.",
      "These efficiency gains are offset by a higher solvent purchase cost per kilogram.",
    ],
    regen:2.4, comp_mwh:0.110, makeup:0.50, sol_cost:2.50,
    cap_max:0.95, capex_f:1.05, color:"#10b981",
  },
  K2CO3: {
    name:"Potassium Carbonate (K₂CO₃)", short:"K₂CO₃",
    desc:[
      "Potassium carbonate is a low-cost inorganic solvent with the lowest energy penalty of the three options.",
      "Its slower reaction kinetics limit the maximum achievable capture efficiency to around 85%.",
    ],
    regen:2.0, comp_mwh:0.110, makeup:0.30, sol_cost:0.50,
    cap_max:0.85, capex_f:0.95, color:"#f59e0b",
  },
};

// ── TEA model ─────────────────────────────────────────────────────────────────
const REF=500, EXP=0.6, AVAIL=0.90, IND=0.30, MAINT=0.025, INS=0.005, WATER=1.50;
const CAPS={absorber:20,regenerator:32,heat_exchangers:14,compression:34,utilities:17,civil:9};
const REF_D=Object.values(CAPS).reduce((a,b)=>a+b,0);

function calc(sol,cap,cr,ep,elp,dr,pl){
  const s=SOLVENTS[sol]; cr=Math.min(cr,s.cap_max);
  const aco2=cap*365*AVAIL;
  const sf=Math.pow(cap/REF,EXP)*s.capex_f;
  const tc=REF_D*sf*1e6*(1+IND);
  const crf=(dr*Math.pow(1+dr,pl))/(Math.pow(1+dr,pl)-1);
  const acap=tc*crf;
  const en=aco2*s.regen*ep, co=aco2*s.comp_mwh*elp,
        sv=aco2*s.makeup*s.sol_cost,
        lb=900000+250000*Math.log10(Math.max(cap/100,1)+1),
        mn=tc*MAINT, wt=aco2*WATER, ins=tc*INS;
  const aop=en+co+sv+lb+mn+wt+ins;
  const pt=x=>+(x/aco2).toFixed(2);
  return {
    sol,cap,cr,aco2:Math.round(aco2),
    cpt:+((acap+aop)/aco2).toFixed(2),
    tc_m:+(tc/1e6).toFixed(1), ac_m:+(acap/1e6).toFixed(2),
    ao_m:+(aop/1e6).toFixed(2), crf:+crf.toFixed(4),
    en_share:+((en/aop)*100).toFixed(1),
    bd:{
      "CAPEX":pt(acap),"Energy":pt(en),"Compression":pt(co),
      "Solvent":pt(sv),"Labor":pt(lb),"Maintenance":pt(mn),"Other":pt(wt+ins),
    },
  };
}

function sens(base,sw=0.20){
  const {sol,cap,cr}=base;
  const ep=+el("energy_price").value, elp=+el("electricity_price").value,
        dr=+el("discount_rate").value/100, pl=+el("plant_life").value;
  return [
    ["Energy price",    ep,  (v)=>calc(sol,cap,cr,v,elp,dr,pl).cpt],
    ["Electricity",     elp, (v)=>calc(sol,cap,cr,ep,v,dr,pl).cpt],
    ["Discount rate",   dr,  (v)=>calc(sol,cap,cr,ep,elp,v,pl).cpt],
    ["Plant life",      pl,  (v)=>calc(sol,cap,cr,ep,elp,dr,Math.max(5,Math.round(v))).cpt],
    ["Plant capacity",  cap, (v)=>calc(sol,Math.max(100,v),cr,ep,elp,dr,pl).cpt],
  ].map(([lbl,val,fn])=>({
    lbl, lo:fn(val*(1-sw)), base:base.cpt, hi:fn(val*(1+sw)),
    sw:+(fn(val*(1+sw))-fn(val*(1-sw))).toFixed(2),
  })).sort((a,b)=>Math.abs(b.sw)-Math.abs(a.sw));
}

function scaleCurve(cr,ep,elp,dr,pl){
  const caps=[100,200,300,500,750,1000,1500,2000,3000,5000];
  const out={caps};
  for(const s of Object.keys(SOLVENTS))
    out[s]=caps.map(c=>calc(s,c,Math.min(cr,SOLVENTS[s].cap_max),ep,elp,dr,pl).cpt);
  return out;
}

// ── State & helpers ───────────────────────────────────────────────────────────
let sol="MEA";
const el=id=>document.getElementById(id);

// Paint an accent-filled track on a range input up to its current value
function fillSlider(id){
  const s=el(id); if(!s) return;
  const pct=((s.value-s.min)/(s.max-s.min))*100;
  const cs=getComputedStyle(s);
  const fill=cs.getPropertyValue('--accent').trim();
  const rest=cs.getPropertyValue('--border').trim();
  s.style.background=`linear-gradient(to right, ${fill} 0%, ${fill} ${pct}%, ${rest} ${pct}%, ${rest} 100%)`;
}

function setSolvent(s){
  sol=s;
  document.querySelectorAll(".stab").forEach(t=>{
    t.className="stab";
    if(t.id===`tab-${s}`){
      const c=s==="K2CO3"?"sel-k2co3":s==="Piperazine"?"sel-pz":"sel-mea";
      t.classList.add(c);
    }
  });
  const bullets=SOLVENTS[s].desc.map(d=>`<li>${d}</li>`).join("");
  el("solvent-info").innerHTML=`<span class="solvent-name">${SOLVENTS[s].name}</span><ul class="solvent-desc">${bullets}</ul>`;
  update();
}

// ── Chart setup ───────────────────────────────────────────────────────────────
Chart.defaults.font.family="IBM Plex Sans, system-ui, sans-serif";
Chart.defaults.font.size=13;
Chart.defaults.color="#64748b";
Chart.defaults.borderColor="#f1f5f9";

const BCOLORS={
  "CAPEX":"#3b82f6","Energy":"#ef4444","Compression":"#8b5cf6",
  "Solvent":"#10b981","Labor":"#f59e0b","Maintenance":"#06b6d4","Other":"#94a3b8"
};

function mkChart(id,type,data,opts){
  return new Chart(el(id).getContext("2d"),{type,data,options:{
    responsive:true,maintainAspectRatio:false,...opts
  }});
}

const TIP_PT=(label)=>({callbacks:{label:ctx=>` ${ctx.dataset.label||label||""}: $${(ctx.parsed.y??ctx.parsed.x).toFixed(2)}`}});

const breakdownChart=mkChart("breakdownChart","bar",{labels:[],datasets:[]},{
  plugins:{legend:{display:true,position:"bottom",labels:{boxWidth:12,padding:12,font:{size:12}}},...TIP_PT()},
  scales:{
    x:{stacked:true,grid:{display:false},ticks:{display:false}},
    y:{stacked:true,grid:{color:"#f1f5f9"},ticks:{callback:v=>`$${v}`},border:{display:false}},
  },
});

const compChart=mkChart("comparisonChart","bar",{labels:[],datasets:[]},{
  plugins:{legend:{display:false},...TIP_PT("$/t CO₂")},
  scales:{
    x:{grid:{display:false},border:{display:false}},
    y:{grid:{color:"#f1f5f9"},ticks:{callback:v=>`$${v}`},border:{display:false}},
  },
});

const scaleChart=mkChart("scaleChart","line",{labels:[],datasets:[]},{
  plugins:{legend:{display:true,position:"top",labels:{boxWidth:12,padding:16,font:{size:12}}},
    tooltip:{callbacks:{label:ctx=>` ${ctx.dataset.label}: $${ctx.parsed.y.toFixed(2)}/t CO₂`}}},
  scales:{
    x:{grid:{color:"#f1f5f9"},border:{display:false},
       title:{display:true,text:"Plant capacity (tonne CO₂ / day)",color:"#94a3b8",font:{size:12}}},
    y:{grid:{color:"#f1f5f9"},border:{display:false},ticks:{callback:v=>`$${v}`},
       title:{display:true,text:"$/tonne CO₂",color:"#94a3b8",font:{size:12}}},
  },
  elements:{line:{tension:.35},point:{radius:3,hoverRadius:5}},
});

const sensChart=mkChart("sensitivityChart","bar",{labels:[],datasets:[]},{
  indexAxis:"y",
  grouped:false,
  plugins:{
    legend:{display:true,position:"top",labels:{boxWidth:12,padding:14,font:{size:12}}},
    tooltip:{callbacks:{label:ctx=>{
      const [lo,hi]=Array.isArray(ctx.raw)?ctx.raw:[ctx.raw,ctx.raw];
      return ` $${lo.toFixed(2)} → $${hi.toFixed(2)}/t CO₂`;
    }}},
  },
  scales:{
    x:{grid:{color:"#f1f5f9"},border:{display:false},ticks:{callback:v=>`$${v}`}},
    y:{grid:{display:false},border:{display:false}},
  },
});

// ── Update ────────────────────────────────────────────────────────────────────
function update(){
  const cap=+el("capacity").value, cr=+el("capture_rate").value/100,
        ep=+el("energy_price").value, elp=+el("electricity_price").value,
        dr=+el("discount_rate").value/100, pl=+el("plant_life").value;

  el("v-cap").textContent=cap.toLocaleString();
  el("v-cr").textContent=Math.round(cr*100);
  el("v-ep").textContent=ep.toFixed(2);
  el("v-elp").textContent=elp;
  el("v-dr").textContent=(dr*100).toFixed(1);
  el("v-pl").textContent=pl;

  // Filled slider tracks (accent fill up to the thumb)
  ["capacity","capture_rate","energy_price","electricity_price","discount_rate","plant_life"]
    .forEach(fillSlider);

  const r=calc(sol,cap,cr,ep,elp,dr,pl);

  el("header-badge").textContent=`${SOLVENTS[sol].short} · ${cap.toLocaleString()} t/day`;
  el("kpi-cost").textContent=`$${r.cpt}`;
  el("kpi-capex").textContent=`$${r.tc_m}M`;
  el("kpi-crf").textContent=`CRF ${(r.crf*100).toFixed(1)}%`;
  el("kpi-co2").textContent=r.aco2.toLocaleString();
  el("kpi-opex").textContent=`$${r.ao_m}M/yr`;
  el("kpi-energy-share").textContent=`Energy: ${r.en_share}% of OPEX`;

  // Breakdown (stacked)
  const bdK=Object.keys(r.bd), bdV=Object.values(r.bd);
  breakdownChart.data.labels=[""];
  breakdownChart.data.datasets=bdK.map((k,i)=>({
    label:k,data:[bdV[i]],backgroundColor:BCOLORS[k]||"#94a3b8",
    borderRadius:i===bdK.length-1?4:0,borderSkipped:"bottom",
  }));
  breakdownChart.update("none");

  // Comparison
  const sols=Object.keys(SOLVENTS);
  compChart.data.labels=sols.map(s=>SOLVENTS[s].short);
  compChart.data.datasets=[{
    data:sols.map(s=>calc(s,cap,Math.min(cr,SOLVENTS[s].cap_max),ep,elp,dr,pl).cpt),
    backgroundColor:sols.map(s=>SOLVENTS[s].color+"cc"),
    borderColor:sols.map(s=>SOLVENTS[s].color),
    borderWidth:1.5, borderRadius:6,
  }];
  compChart.update("none");

  // Scale curve
  const sc=scaleCurve(cr,ep,elp,dr,pl);
  scaleChart.data.labels=sc.caps.map(c=>c.toLocaleString());
  scaleChart.data.datasets=sols.map(s=>({
    label:SOLVENTS[s].short, data:sc[s],
    borderColor:SOLVENTS[s].color,
    backgroundColor:SOLVENTS[s].color+"18",
    borderWidth:s===sol?2.5:1.5,
    fill:false,
  }));
  scaleChart.update("none");

  // Sensitivity: true tornado: floating bars emanating from the base value
  const sv=sens(r);
  const xPad=5;
  sensChart.options.scales.x.min=Math.floor(Math.min(...sv.map(s=>s.lo))-xPad);
  sensChart.options.scales.x.max=Math.ceil(Math.max(...sv.map(s=>s.hi))+xPad);
  sensChart.data.labels=sv.map(s=>s.lbl);
  sensChart.data.datasets=[
    {
      label:"−20% scenario",
      data:sv.map(s=>[s.lo, s.base]),   // bar spans lo → base
      backgroundColor:"#93c5fd",
      borderColor:"#3b82f6",
      borderWidth:1,
      borderSkipped:false,
      borderRadius:3,
    },
    {
      label:"+20% scenario",
      data:sv.map(s=>[s.base, s.hi]),   // bar spans base → hi
      backgroundColor:"#fca5a5",
      borderColor:"#ef4444",
      borderWidth:1,
      borderSkipped:false,
      borderRadius:3,
    },
  ];
  sensChart.update("none");
}

// ── Theme toggle ─────────────────────────────────────────────────────────────
function applyTheme(theme) {
  const dark = theme === 'dark';
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : '');
  localStorage.setItem('theme', theme);
  const sunIcon  = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>';
  const moonIcon = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  el('theme-icon').innerHTML    = dark ? sunIcon : moonIcon;
  el('theme-label').textContent = dark ? 'Light Mode' : 'Dark Mode';

  // Update Chart.js global defaults for new theme
  const gridColor  = dark ? 'rgba(148,163,184,.12)' : '#f1f5f9';
  const labelColor = dark ? '#9babbf' : '#64748b';
  Chart.defaults.color       = labelColor;
  Chart.defaults.borderColor = gridColor;

  // Re-apply grid colors to all existing charts
  [breakdownChart, compChart, scaleChart, sensChart].forEach(c => {
    if (!c) return;
    (c.options.scales?.x?.grid  || {}).color = gridColor;
    (c.options.scales?.y?.grid  || {}).color = gridColor;
    c.update('none');
  });

  // Repaint slider fills with the new theme's accent color
  ["capacity","capture_rate","energy_price","electricity_price","discount_rate","plant_life"]
    .forEach(fillSlider);
}
function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  applyTheme(isDark ? 'light' : 'dark');
}

setSolvent("MEA");
applyTheme(localStorage.getItem('theme') || 'light');

// ── Info popups ───────────────────────────────────────────────────────────────
// ── Page switching ─────────────────────────────────────────────────────────
function showPage(name) {
  document.getElementById('page-overview').style.display = name === 'overview' ? '' : 'none';
  document.getElementById('page-analysis').style.display = name === 'analysis' ? '' : 'none';
  document.querySelectorAll('.page-tab').forEach(t =>
    t.classList.toggle('active', t.dataset.page === name)
  );
}

const INFO = {
  // ── PFD equipment ─────────────────────────────────────────────────────────
  "pfd-absorber": {
    title: "Absorber Column",
    body: `The absorber is a tall packed column where CO₂ is transferred from the flue gas into the liquid solvent.
<br><br>
<strong>How it works:</strong> flue gas enters at the bottom and rises through structured packing material. Lean solvent (stripped of CO₂) is sprayed from the top and trickles down. As the two phases contact each other, CO₂ reacts chemically with the solvent (e.g. CO₂ + 2MEA → carbamate), loading the solvent with CO₂.
<br><br>
<strong>What leaves:</strong> CO₂-rich solvent exits from the bottom (heading to the regenerator). Treated flue gas, now 85-90% depleted in CO₂, exits from the top.
<br><br>
<strong>Key design parameter:</strong> column height and packing surface area determine how much CO₂ is absorbed per pass. Higher capture rates require taller columns and more packing.`
  },
  "pfd-hx": {
    title: "Lean-Rich Heat Exchanger",
    body: `The lean-rich heat exchanger (L-R HX) is one of the most important energy-saving components in the plant.
<br><br>
<strong>What it does:</strong> transfers heat from the hot lean solvent returning from the regenerator (~120°C) to the cool rich solvent heading toward the regenerator (~50°C). This pre-heats the rich solvent before it enters the reboiler, dramatically reducing the steam demand.
<br><br>
<strong>Why it matters:</strong> without this heat recovery step, all the thermal energy needed to heat the rich solvent from ~50°C to regeneration temperature (~120°C) would have to come from external steam. The L-R HX recovers 60-80% of that energy internally, directly cutting the reboiler duty.
<br><br>
<strong>Typical approach temperature:</strong> 5-10°C (the closer the temperatures, the more heat is recovered but the larger and more expensive the exchanger).`
  },
  "pfd-cooler": {
    title: "Lean Solvent Cooler",
    body: `After passing through the lean-rich heat exchanger, the lean solvent is still too hot to return directly to the absorber.
<br><br>
<strong>Why cooling is needed:</strong> CO₂ absorption is an exothermic reaction: it releases heat. Lower temperatures favour absorption (Le Chatelier's principle). If the lean solvent enters the absorber too hot, the absorption efficiency drops significantly. The cooler brings it down to ~40-45°C.
<br><br>
<strong>Cooling medium:</strong> typically cooling water from a cooling tower. The heat rejected here is waste heat from the process.
<br><br>
<strong>Cost impact:</strong> the lean cooler adds to cooling water consumption (~1.5 USD/tonne CO₂ in this model for water and treatment costs).`
  },
  "pfd-regenerator": {
    title: "Regenerator (Stripper) Column",
    body: `The regenerator reverses the absorption reaction, releasing CO₂ from the rich solvent and producing lean solvent ready for reuse.
<br><br>
<strong>How it works:</strong> rich solvent enters near the top. Steam from the reboiler at the base heats the solvent to 120-130°C, reversing the carbamate reaction: carbamate → CO₂ + MEA + heat. CO₂ gas rises to the top and is collected. Lean solvent accumulates at the bottom.
<br><br>
<strong>Operating conditions:</strong> 1-2 bar pressure, 120-130°C. Higher pressure slightly reduces stripping efficiency but reduces the energy needed for downstream CO₂ compression.
<br><br>
<strong>The energy bottleneck:</strong> the heat input here (from the reboiler) is the single largest cost component in the process. MEA requires 3.7 GJ per tonne CO₂. Piperazine cuts this to 2.4 GJ/t, and K₂CO₃ to 2.0 GJ/t, which is why solvent choice strongly affects cost.`
  },
  "pfd-reboiler": {
    title: "Reboiler",
    body: `The reboiler is a heat exchanger at the base of the regenerator that provides the thermal energy needed to strip CO₂ from the solvent.
<br><br>
<strong>Energy source:</strong> low-pressure steam (typically 3-4 bar, 130-150°C), extracted from a nearby power plant or industrial boiler. This steam demand is the dominant operating cost.
<br><br>
<strong>Energy required (this model):</strong><br>
MEA: 3.7 GJ/tonne CO₂ (industry baseline)<br>
Piperazine: 2.4 GJ/tonne CO₂ (-35%)<br>
K₂CO₃: 2.0 GJ/tonne CO₂ (-46%)
<br><br>
<strong>Why MEA needs more energy:</strong> MEA forms a stable carbamate bond that requires significant heat to break. Advanced solvents with weaker CO₂ binding (like K₂CO₃) need less energy to regenerate, directly reducing the energy cost per tonne on the Cost Analysis page.`
  },
  "pfd-compressor": {
    title: "CO₂ Compressor Train",
    body: `CO₂ exits the regenerator at near-atmospheric pressure (1-2 bar). Before it can be transported by pipeline or injected for storage, it must be compressed to supercritical conditions.
<br><br>
<strong>Target pressure:</strong> ~150 bar. At this pressure, CO₂ is in a supercritical state, behaving like a dense fluid, which allows efficient pipeline transport.
<br><br>
<strong>Compression stages:</strong> typically 4-6 stages with intercooling between each to maintain manageable temperatures and avoid excessive compression work.
<br><br>
<strong>Energy requirement:</strong> 0.11 MWh per tonne CO₂ (used in this model). This is electricity, not heat, so it is priced separately from the reboiler steam.
<br><br>
<strong>Cost contribution:</strong> compression is typically the 3rd largest cost component, after annualized CAPEX and energy for regeneration.`
  },
  "kpi-cost": {
    title: "Levelised Cost of Capture",
    body: `The all-in cost to capture one tonne of CO₂, expressed as a single lifetime-averaged number that makes the project economically neutral (NPV = 0) at the given discount rate.
<br><br>
It sums every cost component (CAPEX, energy, compression, solvent, labor, maintenance, water, insurance) and divides by the total CO₂ captured over the plant's life.
<br><br>
<strong>How to use it:</strong> a carbon price or policy support above this number makes the project financially viable. Published ranges for post-combustion capture: $40-80/t for large optimized plants (IEA), $100-200/t for smaller or first-of-kind projects. The base case here (~$164/t at 500 tpd with MEA) reflects a mid-scale plant without economies of scale.`
  },
  "kpi-capex": {
    title: "Total CAPEX and Capital Recovery Factor",
    body: `<strong>Total CAPEX</strong> includes all direct equipment costs (absorber column, regenerator, heat exchangers, CO₂ compressors, utilities, civil works) scaled from the NETL reference plant using the six-tenths rule, plus 30% indirect costs for EPC, engineering, and contingency.
<br><br>
<strong>Capital Recovery Factor (CRF)</strong> converts this one-time capital cost into an equivalent annual payment, the same way a mortgage converts a purchase price into annual repayments.
<br><br>
<strong>CRF = r(1+r)^n / ((1+r)^n - 1)</strong>
<br><br>
where r = discount rate and n = plant life in years. At 8% discount rate over 25 years, CRF = 9.4%, meaning 9.4% of total CAPEX is charged each year. This annual charge, divided by tonnes of CO₂ captured per year, gives the CAPEX component of $/tonne.`
  },
  "kpi-co2": {
    title: "Annual CO₂ Captured",
    body: `Total CO₂ captured per year, calculated as:
<br><br>
<strong>Annual CO₂ = Capacity (tpd) x 365 days x 0.90 availability</strong>
<br><br>
The <strong>90% availability factor</strong> accounts for planned maintenance shutdowns, unplanned outages, and start-up/shutdown periods. A typical chemical plant operates around 7,884 hours per year (90% of 8,760).
<br><br>
This figure is the denominator in all per-tonne cost calculations. Increasing plant capacity or availability directly reduces $/tonne by spreading fixed costs over more CO₂.`
  },
  "kpi-opex": {
    title: "Annual Operating Expenditure",
    body: `All recurring costs to run the plant for one year, broken into seven components:
<br><br>
<strong>Energy</strong>: heat to regenerate (strip CO₂ from) the solvent each cycle. Largest OPEX item for MEA (3.7 GJ/tonne CO₂).<br>
<strong>Compression</strong>: electricity to compress captured CO₂ to pipeline pressure (~150 bar, fixed at 0.11 MWh/tonne).<br>
<strong>Solvent makeup</strong>: replacing solvent lost to thermal/oxidative degradation and entrainment.<br>
<strong>Labor</strong>: base staffing cost with a logarithmic scale effect (larger plants need proportionally fewer workers).<br>
<strong>Maintenance</strong>: 2.5% of total CAPEX per year.<br>
<strong>Water</strong>: cooling water and process water treatment.<br>
<strong>Insurance</strong>: 0.5% of total CAPEX per year.
<br><br>
<strong>Energy share</strong> shows what fraction of OPEX is energy cost. A high share (e.g. 50%+) means solvent efficiency is the key lever for cost reduction.`
  },
  breakdown: {
    title: "Cost Breakdown: how to read it",
    body: `This stacked bar shows what drives the total capture cost per tonne of CO₂, split into seven components:
<br><br>
<strong>CAPEX (annualized)</strong>: the plant's build cost converted into an annual payment using the Capital Recovery Factor (CRF). Sensitive to discount rate and plant life.
<br><br>
<strong>Energy</strong>: heat needed to regenerate (strip CO₂ from) the solvent each cycle. The single largest OPEX driver for MEA; much lower for PZ and K₂CO₃.
<br><br>
<strong>Compression</strong>: electricity to compress captured CO₂ to pipeline pressure (~150 bar). Fixed at 0.11 MWh/tonne CO₂ regardless of solvent.
<br><br>
<strong>Solvent makeup</strong>: replacing solvent lost to degradation and entrainment. MEA degrades faster and costs more per kg than alternatives.
<br><br>
<strong>Labor, Maintenance, Other</strong>: fixed and semi-fixed costs that diminish on a per-tonne basis as plant scale increases.`
  },
  comparison: {
    title: "Solvent Comparison: how to read it",
    body: `Compares the three solvents at <em>identical</em> plant configuration and economic assumptions, so differences are purely due to solvent chemistry:
<br><br>
<strong>MEA (Monoethanolamine)</strong>: the industry benchmark, deployed in every commercial post-combustion plant. High energy demand (3.7 GJ/t CO₂) and solvent degradation make it the most expensive at most configurations.
<br><br>
<strong>Piperazine (PZ)</strong>: an advanced amine with ~35% lower regeneration energy (2.4 GJ/t CO₂) and faster absorption kinetics. Higher solvent purchase cost but lower operating cost.
<br><br>
<strong>K₂CO₃ (Potassium Carbonate)</strong>:the cheapest solvent by far ($0.50/kg vs $1.50 for MEA) and lowest regeneration energy (2.0 GJ/t CO₂), but slower reaction kinetics cap its maximum capture efficiency at 85%.
<br><br>
Note: capture rate is clamped to each solvent's maximum, so PZ may show a higher capture rate than K₂CO₃ at the same slider setting.`
  },
  scale: {
    title: "Economy of Scale: how to read it",
    body: `Shows how the levelised cost falls as plant size increases, for all three solvents at current operating conditions.
<br><br>
<strong>Why costs fall with scale:</strong> capital cost scales with the <em>six-tenths rule</em>: a standard chemical engineering heuristic where cost ∝ capacity<sup>0.6</sup>. Doubling capacity increases cost by only ~52%, not 100%, because vessel walls, foundations, and piping don't scale linearly with throughput.
<br><br>
<strong>Fixed costs spread out:</strong> labor, insurance, and some maintenance are semi-fixed, so their per-tonne contribution shrinks as more CO₂ is captured each year.
<br><br>
<strong>Diminishing returns:</strong> the curves flatten above ~2,000 t/day. Very large plants still benefit from scale, but the savings per additional tonne of capacity become smaller.
<br><br>
The <strong>currently selected solvent</strong> is shown with a thicker line.`
  },
  sensitivity: {
    title: "Sensitivity Analysis: how to read it",
    body: `A tornado chart showing which input assumptions move the cost the most. Five parameters are varied ±20% from their current slider values, one at a time, while all others are held fixed.
<br><br>
<strong>How to read it:</strong> bars emanate left and right from the base-case cost. The wider the combined bar, the more influence that parameter has. Parameters are ranked by magnitude from top to bottom.
<br><br>
<strong>Blue bar</strong>: cost when the parameter is 20% below its current value.<br>
<strong>Red bar</strong>: cost when the parameter is 20% above its current value.
<br><br>
<strong>Discount rate</strong> typically dominates: CCUS plants are capital-intensive, so financing cost directly drives the annualized CAPEX component.<br><br>
<strong>Plant capacity</strong> has an inverse effect: a larger plant costs <em>less</em> per tonne (six-tenths rule), so the blue bar extends right and the red bar extends left, opposite to the other parameters.<br><br>
<strong>Plant life</strong> is also inverse: a longer operating life spreads CAPEX over more years, lowering cost per tonne.<br><br>
<em>Note: capture rate is not included because this model defines capacity as tonnes of CO₂ captured per day, so $/tonne is independent of capture rate; only the total annual volume changes.</em>`
  },
};

function showInfo(key) {
  const info = INFO[key];
  el("modal-title").textContent = info.title;
  el("modal-body").innerHTML    = info.body;
  el("modal-overlay").classList.add("open");
}
function hideInfo() { el("modal-overlay").classList.remove("open"); }
function closeInfo(e) { if(e.target===el("modal-overlay")) hideInfo(); }
document.addEventListener("keydown", e => { if(e.key==="Escape") hideInfo(); });
</script>
</body>
</html>"""


def generate() -> Path:
    OUTPUT_PATH.write_text(HTML_TEMPLATE, encoding="utf-8")
    print(f"✓  Dashboard written → {OUTPUT_PATH}")
    return OUTPUT_PATH
