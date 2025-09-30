# src/footing.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .models import Inputs, Results

@dataclass
class FootingChecks:
    # Demands
    V_struct_lb: float
    H_post_lb: float
    U_post_lb: float
    # Weights / effective vertical
    W_footing_lb: float
    W_overburden_lb: float
    V_eff_lb: float
    # Bearing
    q_actual_psf: float
    q_allow_eff_psf: float
    bearing_ok: bool
    # Sliding
    R_slide_lb: float
    sliding_ok: bool
    # Uplift
    R_uplift_lb: float
    uplift_ok: bool
    # Log
    calc_log: List[str]

def _bool_from_yesno(v: Any) -> bool:
    if isinstance(v, bool): return v
    if v is None: return False
    s = str(v).strip().lower()
    return s in ("yes", "y", "true", "1")

def footing_checks(inputs: Inputs, beam_results: Results) -> FootingChecks:
    log: List[str] = []

    # --- Geometry -> feet
    L_in = float(inputs.footing_length_in or 0.0)
    W_in = float(inputs.footing_width_in or 0.0)
    T_in = float(inputs.footing_thickness_in or 0.0)
    Dcov_in = float(inputs.footing_depth_below_grade_in or 0.0)

    L_ft = L_in / 12.0
    W_ft = W_in / 12.0
    T_ft = T_in / 12.0
    Dcov_ft = Dcov_in / 12.0

    # Areas / volumes
    A_ft2 = L_ft * W_ft
    Vconc_ft3 = L_ft * W_ft * T_ft

    gamma_soil = float(inputs.soil_unit_weight_pcf or 120.0)
    gamma_conc = float(inputs.concrete_unit_weight_pcf or 150.0)

    W_footing = Vconc_ft3 * gamma_conc
    include_overburden = _bool_from_yesno(inputs.include_soil_overburden)
    W_overburden = (A_ft2 * Dcov_ft * gamma_soil) if include_overburden else 0.0

    log.append(f"Footing A={A_ft2:.3f} ft², Vconc={Vconc_ft3:.3f} ft³, W_footing={W_footing:.1f} lb, "
               f"W_overburden={W_overburden:.1f} lb (include={include_overburden})")

    # --- Structural demands at post
    V_struct = (beam_results.reaction_per_post_lb or 0.0) + float(inputs.post_self_weight_lb or 0.0)
    log.append(f"V_struct = Reaction(post) + Post self-weight = {beam_results.reaction_per_post_lb:.1f} + "
               f"{float(inputs.post_self_weight_lb or 0.0):.1f} = {V_struct:.1f} lb")

    # Lateral line load -> H at post
    H_post = 0.0
    if inputs.lateral_line_load_plf is not None:
        H_post = float(inputs.lateral_line_load_plf) * float(inputs.span_ft) / 2.0
        log.append(f"H_post = lateral_plf × span / 2 = {inputs.lateral_line_load_plf:.2f} × {inputs.span_ft:.2f} / 2 = {H_post:.1f} lb")
    elif inputs.wind_wall_psf and inputs.exposed_height_ft:
        w_lat_plf = float(inputs.wind_wall_psf) * float(inputs.exposed_height_ft)
        H_post = w_lat_plf * float(inputs.span_ft) / 2.0
        log.append(f"H_post = (wind_wall_psf×height)×span/2 = ({inputs.wind_wall_psf:.2f}×{inputs.exposed_height_ft:.2f})×{inputs.span_ft:.2f}/2 = {H_post:.1f} lb")
    else:
        log.append("H_post = 0 (no lateral line load provided)")

    # Uplift at post from wind on roof
    U_post = 0.0
    if inputs.roof_uplift_psf and inputs.uplift_area_per_post_ft2:
        U_post = float(inputs.roof_uplift_psf) * float(inputs.uplift_area_per_post_ft2)
        log.append(f"U_post = roof_uplift_psf × uplift_area = {inputs.roof_uplift_psf:.2f} × {inputs.uplift_area_per_post_ft2:.2f} = {U_post:.1f} lb")
    else:
        log.append("U_post = 0 (no uplift psf or area provided)")

    # Effective vertical for sliding/uplift resistance (footing + overburden + structural)
    V_eff = V_struct + W_footing + W_overburden

    # --- Bearing check
    q_actual = V_struct / max(A_ft2, 1e-9)
    q_allow = float(inputs.soil_bearing_capacity_psf or 0.0)
    SF_bearing = float(inputs.SF_bearing or 1.0)
    q_allow_eff = q_allow / max(SF_bearing, 1e-9)
    bearing_ok = q_actual <= q_allow_eff
    log.append(f"Bearing: q_actual={q_actual:.0f} psf vs q_allow_eff={q_allow_eff:.0f} psf -> {'PASS' if bearing_ok else 'CHECK'}")

    # --- Sliding check
    mu = float(inputs.base_friction_coeff_mu or 0.5)
    SF_sliding = float(inputs.SF_sliding or 1.5)
    R_slide = (mu * V_eff) / max(SF_sliding, 1e-9)
    sliding_ok = H_post <= R_slide
    log.append(f"Sliding: H={H_post:.0f} lb vs μ·V_eff/SF={mu:.2f}·{V_eff:.0f}/{SF_sliding:.2f}={R_slide:.0f} lb -> {'PASS' if sliding_ok else 'CHECK'}")

    # --- Uplift check
    SF_uplift = float(inputs.SF_uplift or 1.5)
    credit_uplift = float(inputs.credit_connector_uplift_lb or 0.0)
    R_uplift = (W_footing + W_overburden + credit_uplift) / max(SF_uplift, 1e-9)
    uplift_ok = U_post <= R_uplift
    log.append(f"Uplift: U={U_post:.0f} lb vs (W_footing+W_overburden+credit)/SF=({W_footing:.0f}+{W_overburden:.0f}+{credit_uplift:.0f})/{SF_uplift:.2f}={R_uplift:.0f} lb -> {'PASS' if uplift_ok else 'CHECK'}")

    return FootingChecks(
        V_struct_lb=V_struct,
        H_post_lb=H_post,
        U_post_lb=U_post,
        W_footing_lb=W_footing,
        W_overburden_lb=W_overburden,
        V_eff_lb=V_eff,
        q_actual_psf=q_actual,
        q_allow_eff_psf=q_allow_eff,
        bearing_ok=bearing_ok,
        R_slide_lb=R_slide,
        sliding_ok=sliding_ok,
        R_uplift_lb=R_uplift,
        uplift_ok=uplift_ok,
        calc_log=log
    )
