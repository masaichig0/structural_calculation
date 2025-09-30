# src/models.py
from dataclasses import dataclass
from typing import Optional, Dict, List

@dataclass
class Inputs:
    # Geometry
    span_ft: float
    tributary_width_ft: float
    beam_b_in: float
    beam_d_in: float
    post_unsupported_height_in: float
    post_base_bearing_area_in2: float
    # Material allowables (psi)
    Fb_prime: float
    Fv_prime: float
    Fc_perp_prime: float
    E: float
    # Loads (psf)
    DL_psf: float
    SL_psf: float
    LL_psf: float = 0.0
    deflection_limit_ratio: float = 240
    # Column (optional)
    Fc_axis_prime: Optional[float] = None
    post_section_b_in: Optional[float] = None
    post_section_d_in: Optional[float] = None
    # Lateral flags
    has_knee_braces: bool = False
    has_moment_top_connector: bool = False
    has_hold_downs_or_shear_base: bool = False
    # Connectors & wind
    top_connector_model: Optional[str] = None
    base_connector_model: Optional[str] = None
    roof_uplift_psf: float = 0.0
    uplift_area_per_post_ft2: float = 0.0
    lateral_line_load_plf: Optional[float] = None
    wind_wall_psf: Optional[float] = None
    exposed_height_ft: Optional[float] = None
    post_to_beam_arm_in: float = 0.0
    # --- NEW: footing & site parameters ---
    soil_bearing_capacity_psf: Optional[float] = None
    soil_unit_weight_pcf: Optional[float] = None
    concrete_unit_weight_pcf: Optional[float] = None
    base_friction_coeff_mu: Optional[float] = None
    SF_bearing: Optional[float] = None
    SF_sliding: Optional[float] = None
    SF_uplift: Optional[float] = None
    credit_connector_uplift_lb: Optional[float] = None
    include_soil_overburden: Optional[bool] = False
    footing_length_in: Optional[float] = None
    footing_width_in: Optional[float] = None
    footing_thickness_in: Optional[float] = None
    footing_depth_below_grade_in: Optional[float] = None
    post_self_weight_lb: Optional[float] = 0.0

@dataclass
class Results:
    # Beam
    line_load_plf: float
    max_moment_lb_in: float
    max_shear_lb: float
    bending_stress_psi: float
    shear_stress_psi: float
    bearing_stress_psi: float
    deflection_in: float
    deflection_limit_in: float
    reaction_per_post_lb: float
    bending_ok: bool
    shear_ok: bool
    bearing_ok: bool
    deflection_ok: bool
    # Column
    column_axial_ok: Optional[bool]
    column_allowable_axial_lb: Optional[float]
    # Lateral
    lateral_warnings: Dict[str, bool]
    # Log
    calc_log: List[str]
