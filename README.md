# Deck Cover Screening Tool (Excel + Python)

Screening-level structural checks for deck cover beams, posts, connectors, wind uplift, and footing capacity.  
**UI:** Excel `.xlsm` with a macro to run Python via xlwings or shell.

## Features
- Beam bending/shear/deflection
- Post axial (optional)
- Connector checks (top/base) against catalog allowables
- Wind uplift per post, lateral line load
- Footing checks: bearing, sliding, uplift

## How to run
1. Install Python 3.x
2. `pip install -r requirements.txt`
3. Open `Deck_Screening_Template.xlsm`
4. Run macro:
   - **Shell method:** `Run_Deck_Screening_Shell` (no xlwings add-in needed)
   - **xlwings add-in:** `Run_Deck_Screening` (requires xlwings add-in)

> If using shell method, update the Python path in VBA (`PYTHON_EXE`) if needed.

## Folder structure
- `src/` Python package
- `Deck_Screening_Template.xlsm` Excel front-end (Inputs/Results/Connectors)
- `requirements.txt` Python deps

## Notes
- Values are screening-level—not a substitute for an engineer’s sealed design.
- See `Connectors` sheet for the allowable loads database.

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.
