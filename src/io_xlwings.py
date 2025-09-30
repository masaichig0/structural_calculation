# src/io_xlwings.py
from typing import Dict, Any, Tuple, List
import xlwings as xw
from .models import Inputs
from .connectors import ConnectorSpecTop, ConnectorSpecBase

LABELS = [
    "span_ft","tributary_width_ft","beam_b_in","beam_d_in",
    "post_unsupported_height_in","post_base_bearing_area_in2",
    "Fb_prime","Fv_prime","Fc_perp_prime","E",
    "DL_psf","SL_psf","LL_psf","deflection_limit_ratio",
    "Fc_axis_prime","post_section_b_in","post_section_d_in",
    "has_knee_braces","has_moment_top_connector","has_hold_downs_or_shear_base",
    "top_connector_model","base_connector_model",
    "roof_uplift_psf","uplift_area_per_post_ft2",
    "lateral_line_load_plf","wind_wall_psf","exposed_height_ft","post_to_beam_arm_in",
    # NEW footing labels:
    "soil_bearing_capacity_psf","soil_unit_weight_pcf","concrete_unit_weight_pcf",
    "base_friction_coeff_mu","SF_bearing","SF_sliding","SF_uplift",
    "credit_connector_uplift_lb","include_soil_overburden",
    "footing_length_in","footing_width_in","footing_thickness_in","footing_depth_below_grade_in",
    "post_self_weight_lb"
]

YESNO = {"yes": True, "no": False, "y": True, "n": False, "true": True, "false": False, "1": True, "0": False}

def _get_book(wb_path: str):
    try:
        return xw.Book.caller()
    except Exception:
        return xw.Book(wb_path)

def _read_inputs_sheet(sht) -> Dict[str, Any]:
    data = {}
    last = sht.range("A" + str(sht.cells.last_cell.row)).end("up").row
    for r in range(1, last+1):
        label = sht.range(f"A{r}").value
        val = sht.range(f"B{r}").value
        if label in LABELS:
            data[label] = val
    return data

def _yn(v):
    if isinstance(v, bool): return v
    if v is None: return False
    if isinstance(v, (int, float)): return bool(v)
    return YESNO.get(str(v).strip().lower(), False)

def read_inputs(wb_path: str) -> Inputs:
    wb = _get_book(wb_path)
    sht = wb.sheets["Inputs"]
    d = _read_inputs_sheet(sht)

    return Inputs(
        span_ft=float(d["span_ft"]),
        tributary_width_ft=float(d["tributary_width_ft"]),
        beam_b_in=float(d["beam_b_in"]),
        beam_d_in=float(d["beam_d_in"]),
        post_unsupported_height_in=float(d["post_unsupported_height_in"]),
        post_base_bearing_area_in2=float(d["post_base_bearing_area_in2"]),
        Fb_prime=float(d["Fb_prime"]),
        Fv_prime=float(d["Fv_prime"]),
        Fc_perp_prime=float(d["Fc_perp_prime"]),
        E=float(d["E"]),
        DL_psf=float(d["DL_psf"]),
        SL_psf=float(d["SL_psf"]),
        LL_psf=float(d.get("LL_psf", 0) or 0),
        deflection_limit_ratio=float(d.get("deflection_limit_ratio", 240) or 240),
        Fc_axis_prime=float(d["Fc_axis_prime"]) if d.get("Fc_axis_prime") not in (None, "", 0) else None,
        post_section_b_in=float(d["post_section_b_in"]) if d.get("post_section_b_in") not in (None, "", 0) else None,
        post_section_d_in=float(d["post_section_d_in"]) if d.get("post_section_d_in") not in (None, "", 0) else None,
        has_knee_braces=_yn(d.get("has_knee_braces")),
        has_moment_top_connector=_yn(d.get("has_moment_top_connector")),
        has_hold_downs_or_shear_base=_yn(d.get("has_hold_downs_or_shear_base")),
        top_connector_model=(d.get("top_connector_model") or None),
        base_connector_model=(d.get("base_connector_model") or None),
        roof_uplift_psf=float(d.get("roof_uplift_psf", 0) or 0),
        uplift_area_per_post_ft2=float(d.get("uplift_area_per_post_ft2", 0) or 0),
        lateral_line_load_plf=float(d["lateral_line_load_plf"]) if d.get("lateral_line_load_plf") not in (None, "") else None,
        wind_wall_psf=float(d["wind_wall_psf"]) if d.get("wind_wall_psf") not in (None, "") else None,
        exposed_height_ft=float(d["exposed_height_ft"]) if d.get("exposed_height_ft") not in (None, "") else None,
        post_to_beam_arm_in=float(d.get("post_to_beam_arm_in", 0) or 0),
        # NEW footing
        soil_bearing_capacity_psf=float(d["soil_bearing_capacity_psf"]) if d.get("soil_bearing_capacity_psf") not in (None, "") else None,
        soil_unit_weight_pcf=float(d["soil_unit_weight_pcf"]) if d.get("soil_unit_weight_pcf") not in (None, "") else None,
        concrete_unit_weight_pcf=float(d["concrete_unit_weight_pcf"]) if d.get("concrete_unit_weight_pcf") not in (None, "") else None,
        base_friction_coeff_mu=float(d["base_friction_coeff_mu"]) if d.get("base_friction_coeff_mu") not in (None, "") else None,
        SF_bearing=float(d["SF_bearing"]) if d.get("SF_bearing") not in (None, "") else None,
        SF_sliding=float(d["SF_sliding"]) if d.get("SF_sliding") not in (None, "") else None,
        SF_uplift=float(d["SF_uplift"]) if d.get("SF_uplift") not in (None, "") else None,
        credit_connector_uplift_lb=float(d["credit_connector_uplift_lb"]) if d.get("credit_connector_uplift_lb") not in (None, "") else None,
        include_soil_overburden=_yn(d.get("include_soil_overburden")),
        footing_length_in=float(d["footing_length_in"]) if d.get("footing_length_in") not in (None, "") else None,
        footing_width_in=float(d["footing_width_in"]) if d.get("footing_width_in") not in (None, "") else None,
        footing_thickness_in=float(d["footing_thickness_in"]) if d.get("footing_thickness_in") not in (None, "") else None,
        footing_depth_below_grade_in=float(d["footing_depth_below_grade_in"]) if d.get("footing_depth_below_grade_in") not in (None, "") else None,
        post_self_weight_lb=float(d.get("post_self_weight_lb", 0) or 0),
    )

def read_connectors(wb_path: str) -> Tuple[List[ConnectorSpecTop], List[ConnectorSpecBase]]:
    wb = _get_book(wb_path)
    sht = wb.sheets["Connectors"]
    last = sht.range("A" + str(sht.cells.last_cell.row)).end("up").row
    tops, bases = [], []
    for r in range(2, last+1):
        row = sht.range(f"A{r}:F{r}").value
        if not row or not row[0]: continue
        typ = str(row[0]).strip().lower()
        if typ == "top":
            tops.append(ConnectorSpecTop(
                model=str(row[1]),
                allowable_download_lb=float(row[2] or 0),
                allowable_uplift_lb=float(row[3] or 0),
                allowable_lateral_lb=float(row[4] or 0),
                allowable_moment_lb_in=float(row[5] or 0)
            ))
        elif typ == "base":
            # base table is 4 cols; row[4], row[5] may be None
            bases.append(ConnectorSpecBase(
                model=str(row[1]),
                allowable_shear_lb=float(row[2] or 0),
                allowable_uplift_lb=float(row[3] or 0)
            ))
    return tops, bases

def write_results(wb_path: str, summary_rows, log_lines):
    wb = _get_book(wb_path)
    sht = wb.sheets["Results"]
    sht.clear_contents()

    sht.range("A1").value = "RESULT SUMMARY"
    sht.range("A1").api.Font.Bold = True
    sht.range("A3").value = [["Item","Value","Status"]]
    sht.range("A3").api.Font.Bold = True
    sht.range("A4").value = summary_rows

    start_row = 4 + len(summary_rows) + 2
    sht.range(f"A{start_row}").value = "CALCULATION LOG"
    sht.range(f"A{start_row}").api.Font.Bold = True
    sht.range(f"A{start_row+2}").value = [[l] for l in log_lines]

    sht.autofit()

def write_connector_results(wb_path: str, top_model, base_model, top_checks, base_checks, start_row: int = 50) -> int:
    wb = _get_book(wb_path)
    sht = wb.sheets["Results"]
    r = start_row

    def write_block(title, model, checks):
        nonlocal r
        sht.range(f"A{r}").value = title
        sht.range(f"A{r}").api.Font.Bold = True
        r += 1
        sht.range(f"A{r}").value = [["Model","Demand","Capacity","Utilization","Status"]]
        sht.range(f"A{r}").api.Font.Bold = True
        r += 1
        sht.range(f"A{r}").value = [[model,"","","",""]]
        r += 1
        for k, d in checks.items():
            cap = d["cap"] if d["cap"] else 0.0
            util = (d["demand"]/cap) if cap > 0 else 0.0
            status = "PASS" if d["pass"] else "CHECK"
            sht.range(f"A{r}").value = [k, d["demand"], cap, util, status]
            r += 1
        r += 2

    write_block("TOP CONNECTOR", top_model or "(auto-selected)", top_checks)
    write_block("BASE CONNECTOR", base_model or "(auto-selected)", base_checks)

    sht.autofit()
    return r

def write_footing_results(wb_path: str, fchk, start_row: int) -> int:
    wb = _get_book(wb_path)
    sht = wb.sheets["Results"]
    r = start_row
    sht.range(f"A{r}").value = "FOOTING CHECKS (per post)"
    sht.range(f"A{r}").api.Font.Bold = True; r += 2

    # Summary table
    sht.range(f"A{r}").value = [["Item","Demand/Actual","Capacity/Allowable","Status"]]
    sht.range(f"A{r}").api.Font.Bold = True; r += 1

    def status(ok): return "PASS" if ok else "CHECK"

    sht.range(f"A{r}").value = ["Bearing (psf)", f"{fchk.q_actual_psf:.0f}", f"{fchk.q_allow_eff_psf:.0f}", status(fchk.bearing_ok)]; r += 1
    sht.range(f"A{r}").value = ["Sliding (lb)", f"{fchk.H_post_lb:.0f}", f"{fchk.R_slide_lb:.0f}", status(fchk.sliding_ok)]; r += 1
    sht.range(f"A{r}").value = ["Uplift (lb)", f"{fchk.U_post_lb:.0f}", f"{fchk.R_uplift_lb:.0f}", status(fchk.uplift_ok)]; r += 2

    # Details
    sht.range(f"A{r}").value = "FOOTING CALC LOG"
    sht.range(f"A{r}").api.Font.Bold = True; r += 1
    sht.range(f"A{r}").value = [[l] for l in fchk.calc_log]
    r += len(fchk.calc_log) + 1

    sht.autofit()
    return r
