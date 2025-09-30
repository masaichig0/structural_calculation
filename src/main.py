# src/main.py
import sys
from .io_xlwings import read_inputs, write_results, read_connectors, write_connector_results, write_footing_results
from .calc import calc
from .report import summary_table, calc_log_lines
from .connectors import compute_connection_demands, select_or_verify_connectors
from .footing import footing_checks

def main(xlsx_path: str):
    inputs = read_inputs(xlsx_path)
    results = calc(inputs)

    # 1) Primary results
    summary = summary_table(results)
    log = calc_log_lines(results)
    write_results(xlsx_path, summary, log)

    # 2) Connector selection
    top_specs, base_specs = read_connectors(xlsx_path)
    demands = compute_connection_demands(inputs, results)
    selection = select_or_verify_connectors(inputs, demands, top_specs, base_specs)

    r = write_connector_results(
        xlsx_path,
        selection.top_model,
        selection.base_model,
        selection.top_checks,
        selection.base_checks,
        start_row=50
    )

    # 3) Footing checks (Option 1: evaluate given size)
    fchk = footing_checks(inputs, results)
    write_footing_results(xlsx_path, fchk, start_row=r + 2)

if __name__ == "__main__":
    xlsx = sys.argv[1] if len(sys.argv) > 1 else r"excel\Deck_Screening_Template.xlsm"
    main(xlsx)
