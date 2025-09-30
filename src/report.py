# src/report.py
from .models import Results

def summary_table(res: Results):
    rows = []

    # Always add 3 columns: Item, Value, Status
    def add3(item, value, status=""):
        rows.append([item, value, status])

    add3("Line load w (plf)",            f"{res.line_load_plf:,.1f}")
    add3("Reaction per post (lb)",       f"{res.reaction_per_post_lb:,.0f}")
    add3("Bending stress (psi)",         f"{res.bending_stress_psi:,.0f}", "PASS" if res.bending_ok else "CHECK")
    add3("Shear stress (psi)",           f"{res.shear_stress_psi:,.0f}",  "PASS" if res.shear_ok else "CHECK")
    add3("Bearing stress (psi)",         f"{res.bearing_stress_psi:,.0f}", "PASS" if res.bearing_ok else "CHECK")
    add3("Deflection Δ (in)",            f"{res.deflection_in:.3f}")
    add3("Deflection limit (in)",        f"{res.deflection_limit_in:.3f}", "PASS" if res.deflection_ok else "CHECK")

    if res.column_axial_ok is not None:
        add3("Allowable axial per post (lb)", f"{res.column_allowable_axial_lb:,.0f}", "PASS" if res.column_axial_ok else "CHECK")
    else:
        add3("Column check", "— supply Fc′ and post size —", "SKIPPED")

    for k, v in res.lateral_warnings.items():
        add3(f"Lateral: {k}", "OK" if not v else "ATTENTION", "")

    return rows

def calc_log_lines(res: Results):
    return res.calc_log
