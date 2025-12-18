# Bulk Upload Validation — PyShiny

This repository contains a PyShiny application for validating and exporting bulk upload files (CSV/Excel) against configurable rules. The app provides download templates, file assignment UI, validation reporting, and optional CSV export of validated data.

**Highlights**
- Validate single-sheet and multi-sheet Excel files.
- Support for long (column) and wide (date-columns) formats, date parsing with custom formats, numeric/string checks, and value constraints.
- Downloadable templates for common file types and built-in export helpers.

**Files to inspect**
- App source: [App/app.py](App/app.py)
- Requirements: [requirements.txt](requirements.txt)

**Folder structure**
- App/
	- app.py                — PyShiny application and validation logic
	- (generated) exports/  — CSV exports are written here when export paths are configured
- requirements.txt        — Python dependencies
- README.md               — this file

**Requirements**
Install the Python dependencies from `requirements.txt` (recommended in a venv):

```powershell
python -m pip install -r requirements.txt
```

The app relies on the `shiny` package (Shiny for Python), `pandas`, and `openpyxl` for Excel handling. See `requirements.txt` for exact versions.

**Run the app (development)**
From the repository root run:

```powershell
python -m shiny run App.app:app --reload
```

This launches the app and serves it locally (default: http://127.0.0.1:8000). The `--reload` flag enables automatic reload on code changes.

**How to use the app**
1. Open the app in your browser.
2. Use the "Download Sample Templates" buttons in the sidebar to get example files for each file type.
3. Upload one or more CSV/XLSX files using the upload control.
4. Assign each uploaded file to the correct file type using the assignment UI and click "Submit Assignment".
5. The app will validate assigned files and show success, warning, or error messages. When configured, validated data will be exported to the `exports/` folder.

**Where exports go**
The app writes validated exports to an `export/` directory located next to `App/app.py` (created automatically). Example export paths are configured in the `validation_rules` dictionary inside [App/app.py](App/app.py).

**Development notes**
- The main validation logic and rules live in `App/app.py` (search for `validation_rules`).
- To change file schemas or export behavior, update the `validation_rules` mapping and the export helper functions (e.g., `export_attrition`).

**Next steps / Suggestions**
- Add automated tests for `validate_file`/`validate_single_file` to lock behavior.
- Add a small CI workflow to run linting/tests on push.

**License**
See the project `LICENSE` file.
