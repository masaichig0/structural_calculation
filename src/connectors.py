# src/connectors.py
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple

# ---- Define connector spec dataclasses HERE (not in models.py) ----
@dataclass
class ConnectorSpecTop:
    model: str
    allowable_download_lb: float
    allowable_uplift_lb: float
    allowable_lateral_lb: float
    allowable_moment_lb_in: float

@dataclass
class ConnectorSpecBase:
    model: str
    allowable_shear_lb: float
    allowable_uplift_lb: float

# If you use these in your selection logic, define them here too:
@dataclass
class ConnectionDemands:
    top_download_lb: float
    top_uplift_lb: float
    top_lateral_lb: float
    top_moment_lb_in: float
    base_shear_lb: float
    base_uplift_lb: float

@dataclass
class ConnectionSelection:
    top_model: Optional[str]
    base_model: Optional[str]
    top_checks: Dict[str, Dict[str, float]]   # {"download": {"demand":..., "cap":..., "pass": 0/1}, ...}
    base_checks: Dict[str, Dict[str, float]]

# ---- Only after the dataclasses, import Inputs/Results from models ----
from .models import Inputs, Results

# ... keep the rest of your connector functions here ...



def compute_connection_demands(inputs, results) -> ConnectionDemands:
    # --- example calc; keep your existing formulas/variables ---
    download = results.reaction_per_post_lb             # vertical gravity (per post)
    uplift   = (inputs.roof_uplift_psf or 0.0) * (inputs.uplift_area_per_post_ft2 or 0.0)
    # lateral from line load (if provided) else from wall pressure * height
    if inputs.lateral_line_load_plf is not None:
        w_lat = float(inputs.lateral_line_load_plf)
    elif inputs.wind_wall_psf and inputs.exposed_height_ft:
        w_lat = float(inputs.wind_wall_psf) * float(inputs.exposed_height_ft)
    else:
        w_lat = 0.0
    lateral = w_lat * float(inputs.span_ft) / 2.0       # per post
    moment  = lateral * float(inputs.post_to_beam_arm_in or 0.0)  # lb·in

    # Base shear typically same lateral at post (you may refine if needed)
    base_shear = lateral
    # Base uplift: use uplift (roof) if you attribute it to base, else 0 if you only check uplift at top
    base_uplift = uplift

    return ConnectionDemands(
        top_download_lb=download,
        top_uplift_lb=uplift,
        top_lateral_lb=lateral,
        top_moment_lb_in=moment,
        base_shear_lb=base_shear,
        base_uplift_lb=base_uplift
    )


def _top_checks(dem: ConnectionDemands, spec: ConnectorSpecTop):
    c = {}
    # DOWNLOAD (gravity)
    c["download"] = {
        "demand": dem.top_download_lb,
        "cap": spec.allowable_download_lb,
        "pass": dem.top_download_lb <= spec.allowable_download_lb,
    }
    # UPLIFT
    c["uplift"] = {
        "demand": dem.top_uplift_lb,
        "cap": spec.allowable_uplift_lb,
        "pass": dem.top_uplift_lb <= spec.allowable_uplift_lb,
    }
    # LATERAL (shear at top connector)
    c["lateral"] = {
        "demand": dem.top_lateral_lb,
        "cap": spec.allowable_lateral_lb,
        "pass": dem.top_lateral_lb <= spec.allowable_lateral_lb,
    }
    # MOMENT (if spec publishes a moment cap)
    c["moment"] = {
        "demand": dem.top_moment_lb_in,
        "cap": spec.allowable_moment_lb_in,
        "pass": (dem.top_moment_lb_in <= spec.allowable_moment_lb_in) if spec.allowable_moment_lb_in else (dem.top_moment_lb_in == 0),
    }
    return c

def _base_checks(dem: ConnectionDemands, spec: ConnectorSpecBase):
    c = {}
    # SHEAR (lateral at base)
    c["shear"] = {
        "demand": dem.base_shear_lb,
        "cap": spec.allowable_shear_lb,
        "pass": dem.base_shear_lb <= spec.allowable_shear_lb,
    }
    # UPLIFT (at base, if you credit base connector)
    c["uplift"] = {
        "demand": dem.base_uplift_lb,
        "cap": spec.allowable_uplift_lb,
        "pass": dem.base_uplift_lb <= spec.allowable_uplift_lb,
    }
    return c


def select_or_verify_connectors(inputs: Inputs, demands: ConnectionDemands,
                                top_list: List[ConnectorSpecTop], base_list: List[ConnectorSpecBase]) -> ConnectionSelection:
    # Top
    chosen_top = None; top_checks = {}
    if inputs.top_connector_model:
        spec = next((t for t in top_list if t.model == inputs.top_connector_model), None)
        if not spec: raise ValueError(f"Top connector '{inputs.top_connector_model}' not found.")
        top_checks = _top_checks(demands, spec)
        chosen_top = spec.model
    else:
        for spec in top_list:
            c = _top_checks(demands, spec)
            if all(v["pass"] for v in c.values()):
                chosen_top = spec.model; top_checks = c; break
        if not chosen_top and top_list:
            # Choose the connector with the best (lowest worst-case utilization)
            def util(spec):
                from math import inf
                vals = []
                vals.append(demands.download_lb / (spec.allowable_download_lb or 1e9))
                vals.append(demands.uplift_lb   / (spec.allowable_uplift_lb   or 1e9))
                vals.append(demands.lateral_lb  / (spec.allowable_lateral_lb  or 1e9))
                if spec.allowable_moment_lb_in>0 and demands.moment_lb_in>0:
                    vals.append(demands.moment_lb_in / (spec.allowable_moment_lb_in or 1e9))
                return max(vals) if vals else float('inf')
            best = min(top_list, key=util)
            top_checks = _top_checks(demands, best)
            chosen_top = best.model

    # Base
    chosen_base = None; base_checks = {}
    if inputs.base_connector_model:
        spec = next((b for b in base_list if b.model == inputs.base_connector_model), None)
        if not spec: raise ValueError(f"Base connector '{inputs.base_connector_model}' not found.")
        base_checks = _base_checks(demands, spec)
        chosen_base = spec.model
    else:
        for spec in base_list:
            c = _base_checks(demands, spec)
            if all(v["pass"] for v in c.values()):
                chosen_base = spec.model; base_checks = c; break
        if not chosen_base and base_list:
            def util(spec):
                from math import inf
                vals = [
                    demands.lateral_lb / (spec.allowable_shear_lb or 1e9),
                    demands.uplift_lb  / (spec.allowable_uplift_lb or 1e9)
                ]
                return max(vals)
            best = min(base_list, key=util)
            base_checks = _base_checks(demands, best)
            chosen_base = best.model

    return ConnectionSelection(top_model=chosen_top, base_model=chosen_base,
                               top_checks=top_checks, base_checks=base_checks)
