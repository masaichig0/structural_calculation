import math
from .models import Inputs, Results

def pf(flag: bool) -> str:
    return "PASS" if flag else "CHECK"

def calc(inputs: Inputs) -> Results:
    log = []

    q_psf = inputs.DL_psf + inputs.SL_psf + inputs.LL_psf
    log.append(f"q = DL + SL + LL = {inputs.DL_psf} + {inputs.SL_psf} + {inputs.LL_psf} = {q_psf:.3f} psf")

    w_plf = q_psf * inputs.tributary_width_ft
    log.append(f"w = q × tributary_width = {q_psf:.3f} × {inputs.tributary_width_ft:.3f} = {w_plf:.3f} plf")

    w_lbin = w_plf / 12.0
    L_in = inputs.span_ft * 12.0
    b, d = inputs.beam_b_in, inputs.beam_d_in

    S = b * d**2 / 6.0
    I = b * d**3 / 12.0
    log.append(f"S = b d² / 6 = {b:.3f}×{d:.3f}²/6 = {S:.3f} in³")
    log.append(f"I = b d³ / 12 = {b:.3f}×{d:.3f}³/12 = {I:.3f} in⁴")

    M_max = w_lbin * L_in**2 / 8.0
    V_max = w_plf * inputs.span_ft / 2.0
    log.append(f"Mmax = w L² / 8 = {w_lbin:.3f} × {L_in:.1f}² / 8 = {M_max:.1f} lb·in")
    log.append(f"Vmax = w_plf × L / 2 = {w_plf:.3f} × {inputs.span_ft:.3f} / 2 = {V_max:.1f} lb")

    fb = M_max / S
    fv = 1.5 * V_max / (b * d)
    log.append(f"fb = M/S = {M_max:.1f}/{S:.3f} = {fb:.1f} psi  (Fb'={inputs.Fb_prime:.0f})")
    log.append(f"fv = 1.5V/(bd) = 1.5×{V_max:.1f}/({b:.3f}×{d:.3f}) = {fv:.1f} psi  (Fv'={inputs.Fv_prime:.0f})")

    R = V_max
    f_bearing = R / max(inputs.post_base_bearing_area_in2, 1e-6)
    log.append(f"bearing = R/A = {R:.1f}/{inputs.post_base_bearing_area_in2:.3f} = {f_bearing:.1f} psi  (Fc⊥'={inputs.Fc_perp_prime:.0f})")

    delta = 5 * w_lbin * L_in**4 / (384.0 * inputs.E * I)
    delta_limit = L_in / inputs.deflection_limit_ratio
    log.append(f"Δ = 5 w L⁴/(384 E I) = {delta:.3f} in  (limit L/{inputs.deflection_limit_ratio:.0f} = {delta_limit:.3f} in)")

    bending_ok = fb <= inputs.Fb_prime
    shear_ok = fv <= inputs.Fv_prime
    bearing_ok = f_bearing <= inputs.Fc_perp_prime
    deflection_ok = delta <= delta_limit
    log += [f"Bending:   {pf(bending_ok)}", f"Shear:     {pf(shear_ok)}", f"Bearing:   {pf(bearing_ok)}", f"Deflection:{pf(deflection_ok)}"]

    # Column (simplified axial capacity with slenderness knockdown)
    column_ok = None
    col_allow_lb = None
    if inputs.Fc_axis_prime and inputs.post_section_b_in and inputs.post_section_d_in:
        A = inputs.post_section_b_in * inputs.post_section_d_in
        Icol = inputs.post_section_b_in * inputs.post_section_d_in**3 / 12.0
        r = (Icol / A) ** 0.5
        Le = inputs.post_unsupported_height_in
        slender = Le / max(r, 1e-6)
        Pcrit = (math.pi**2) * inputs.E * A / (slender**2 + 1e-6)
        axial_allow = min(inputs.Fc_axis_prime * A, 0.3 * Pcrit)
        col_allow_lb = axial_allow
        column_ok = (R <= axial_allow)
        log.append(f"Column: A={A:.2f} in², r={r:.3f} in, Le={Le:.1f} in, (Le/r)={slender:.1f}")
        log.append(f"Pcrit≈{Pcrit:,.0f} lb; Allowable axial≈min(Fc'×A,0.3Pcrit)={axial_allow:,.0f} lb -> {pf(column_ok)}")
    else:
        log.append("Column check skipped (provide Fc_axis_prime & post section).")

    lateral_flags = {
        "needs_top_moment_or_bracing": not (inputs.has_knee_braces or inputs.has_moment_top_connector),
        "needs_base_anchorage": not inputs.has_hold_downs_or_shear_base,
        "span_long_for_depth_watch_deflection": (not deflection_ok),
    }
    for k, v in lateral_flags.items():
        log.append(f"Lateral '{k}': {'ATTENTION' if v else 'OK'}")

    return Results(
        line_load_plf=w_plf,
        max_moment_lb_in=M_max,
        max_shear_lb=V_max,
        bending_stress_psi=fb,
        shear_stress_psi=fv,
        bearing_stress_psi=f_bearing,
        deflection_in=delta,
        deflection_limit_in=delta_limit,
        reaction_per_post_lb=R,
        bending_ok=bending_ok,
        shear_ok=shear_ok,
        bearing_ok=bearing_ok,
        deflection_ok=deflection_ok,
        column_axial_ok=column_ok,
        column_allowable_axial_lb=col_allow_lb,
        lateral_warnings=lateral_flags,
        calc_log=log
    )
