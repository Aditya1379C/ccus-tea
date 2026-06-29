"""
tea.py — CLI entry point for the CCUS TEA tool.

Usage
-----
  python tea.py calculate              # interactive cost calculation
  python tea.py compare                # compare all 3 solvents side-by-side
  python tea.py report                 # generate HTML dashboard
  python tea.py serve                  # open dashboard in browser (Flask)
  python tea.py sensitivity            # print sensitivity table
"""

import json
import webbrowser
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich import box

import model
import report as rpt
from solvents import SOLVENTS, list_solvents

app     = Console()
cli     = typer.Typer(help="CCUS Techno-Economic Analysis tool")
_HERE   = Path(__file__).parent


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(val: float, prefix="$", suffix="") -> str:
    return f"{prefix}{val:,.2f}{suffix}"


def _print_result(res: dict) -> None:
    sol = SOLVENTS[res["solvent"]]
    app.print()
    app.print(f"[bold cyan]  {sol['name']}[/bold cyan]  —  "
              f"{res['capacity_tpd']:,} tonne CO₂/day  |  "
              f"{res['capture_rate']*100:.0f}% capture rate")
    app.print(f"  [dim]Annual CO₂ captured:[/dim]  {res['annual_co2_tonnes']:,} tonne/year")

    t = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    t.add_column("Metric",          style="dim",  width=32)
    t.add_column("Value",           justify="right")

    t.add_row("Total CAPEX",        f"${res['total_capex_musd']:.1f} M USD")
    t.add_row("Annual CAPEX (CRF)", f"${res['annual_capex_musd']:.2f} M USD/yr  [dim](CRF {res['crf']*100:.2f}%)[/dim]")
    t.add_row("Annual OPEX",        f"${res['annual_opex_musd']:.2f} M USD/yr")
    t.add_row("─" * 28,             "─" * 14)

    for component, value in res["breakdown"].items():
        t.add_row(f"  {component}", _fmt(value, suffix=" /tonne CO₂"))

    t.add_row("─" * 28,             "─" * 14)
    t.add_row("[bold]Levelised cost[/bold]",
              f"[bold green]{_fmt(res['cost_per_tonne'], suffix=' /tonne CO₂')}[/bold green]")
    app.print(t)


# ── Commands ──────────────────────────────────────────────────────────────────

@cli.command()
def calculate(
    solvent:           str   = typer.Option("MEA",   help="MEA | Piperazine | K2CO3"),
    capacity:          float = typer.Option(500.0,   help="Capture capacity (tonne CO₂/day)"),
    capture_rate:      float = typer.Option(0.90,    help="Fraction of CO₂ captured (0.70–0.95)"),
    energy_price:      float = typer.Option(6.00,    help="Thermal energy price (USD/GJ)"),
    electricity_price: float = typer.Option(70.0,    help="Electricity price (USD/MWh)"),
    discount_rate:     float = typer.Option(0.08,    help="Discount rate / WACC"),
    plant_life:        int   = typer.Option(25,      help="Plant life (years)"),
    save:              bool  = typer.Option(False,   help="Save results to data/results.json"),
):
    """Calculate levelised cost of CO₂ capture for a single configuration."""
    if solvent not in list_solvents():
        app.print(f"[red]Unknown solvent '{solvent}'. Choose: {list_solvents()}[/red]")
        raise typer.Exit(1)

    res = model.calculate(
        solvent=solvent, capacity_tpd=capacity, capture_rate=capture_rate,
        energy_price=energy_price, electricity_price=electricity_price,
        discount_rate=discount_rate, plant_life=plant_life,
    )
    _print_result(res)

    if save:
        model.save_results(res)
        app.print(f"\n[dim]Results saved → {model.RESULTS_PATH}[/dim]")


@cli.command()
def compare(
    capacity:          float = typer.Option(500.0,  help="Capture capacity (tonne CO₂/day)"),
    capture_rate:      float = typer.Option(0.90,   help="Fraction of CO₂ captured"),
    energy_price:      float = typer.Option(6.00,   help="Thermal energy price (USD/GJ)"),
    electricity_price: float = typer.Option(70.0,   help="Electricity price (USD/MWh)"),
    discount_rate:     float = typer.Option(0.08,   help="Discount rate"),
    plant_life:        int   = typer.Option(25,     help="Plant life (years)"),
):
    """Compare all 3 solvents at identical operating conditions."""
    results = model.compare_solvents(
        capacity_tpd=capacity, capture_rate=capture_rate,
        energy_price=energy_price, electricity_price=electricity_price,
        discount_rate=discount_rate, plant_life=plant_life,
    )

    app.print()
    app.print(f"[bold]Solvent Comparison[/bold]  —  {capacity:,} tpd  |  "
              f"{capture_rate*100:.0f}% capture  |  "
              f"${energy_price}/GJ  |  {discount_rate*100:.0f}% discount rate  |  {plant_life}yr life")
    app.print()

    t = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    t.add_column("Solvent",         width=26)
    t.add_column("$/tonne CO₂",     justify="right")
    t.add_column("CAPEX (M USD)",   justify="right")
    t.add_column("Energy cost",     justify="right")
    t.add_column("Solvent cost",    justify="right")
    t.add_column("OPEX total",      justify="right")

    for sol_name, res in results.items():
        bd = res["breakdown"]
        t.add_row(
            SOLVENTS[sol_name]["name"],
            f"[bold green]{_fmt(res['cost_per_tonne'])}[/bold green]",
            f"{res['total_capex_musd']:.1f}",
            _fmt(bd["energy"]),
            _fmt(bd["solvent"]),
            f"{res['annual_opex_musd']:.2f} M/yr",
        )

    app.print(t)


@cli.command()
def sensitivity(
    solvent:           str   = typer.Option("MEA",   help="MEA | Piperazine | K2CO3"),
    capacity:          float = typer.Option(500.0,   help="Capture capacity (tonne CO₂/day)"),
    capture_rate:      float = typer.Option(0.90,    help="Fraction of CO₂ captured"),
    energy_price:      float = typer.Option(6.00,    help="Thermal energy price (USD/GJ)"),
    electricity_price: float = typer.Option(70.0,    help="Electricity price (USD/MWh)"),
    discount_rate:     float = typer.Option(0.08,    help="Discount rate"),
    plant_life:        int   = typer.Option(25,      help="Plant life (years)"),
    swing:             float = typer.Option(0.20,    help="Parameter swing fraction (default ±20%)"),
):
    """Tornado sensitivity: show cost impact of ±swing% change in each parameter."""
    base = model.calculate(
        solvent=solvent, capacity_tpd=capacity, capture_rate=capture_rate,
        energy_price=energy_price, electricity_price=electricity_price,
        discount_rate=discount_rate, plant_life=plant_life,
    )
    sens = model.sensitivity(base, swing=swing)

    app.print()
    app.print(f"[bold]Sensitivity Analysis[/bold]  —  {SOLVENTS[solvent]['name']}  "
              f"| Base cost: [green]${base['cost_per_tonne']:.2f}[/green] /tonne CO₂")
    app.print(f"[dim]  Parameter swing: ±{swing*100:.0f}%[/dim]")
    app.print()

    t = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    t.add_column("Parameter",       width=30)
    t.add_column("-20% cost",       justify="right")
    t.add_column("Base cost",       justify="right")
    t.add_column("+20% cost",       justify="right")
    t.add_column("Swing (Δ$/t)",    justify="right")

    for label, vals in sens.items():
        t.add_row(
            label,
            _fmt(vals["low"]),
            _fmt(vals["base"]),
            _fmt(vals["high"]),
            f"[yellow]{_fmt(vals['swing'])}[/yellow]",
        )

    app.print(t)


@cli.command()
def report():
    """Generate the interactive HTML dashboard."""
    path = rpt.generate()
    app.print(f"\n[green]✓[/green]  Dashboard → [cyan]{path}[/cyan]")
    app.print("    Open in any browser — no server needed.")


@cli.command()
def serve(port: int = typer.Option(8080, help="Port for Flask dev server")):
    """Generate dashboard and open it in your default browser."""
    path = rpt.generate()
    webbrowser.open(f"file://{path.resolve()}")
    app.print(f"\n[green]✓[/green]  Opened {path.name} in browser.")


if __name__ == "__main__":
    cli()
