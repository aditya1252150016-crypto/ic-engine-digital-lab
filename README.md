# IC Engine Digital Lab

A student project prototype for web-based IC engine performance calculation, heat balance analysis, test-data visualization, and manual-vs-digital comparison.

## Run online without installing Python locally

1. Create a GitHub repository (for example `ic-engine-digital-lab`).
2. Upload `app.py` and `requirements.txt` to the repository root.
3. Open https://share.streamlit.io/ or https://streamlit.io/cloud and sign in with GitHub.
4. Create a new app, select the repository and branch, and set the main file path to `app.py`.
5. Deploy. Streamlit Community Cloud will install dependencies from `requirements.txt`.

## Run locally (optional)

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Current features

- Brake power from measured engine speed and torque.
- Fuel-energy input, brake thermal efficiency and BSFC.
- Optional indicated power entry or IMEP-based estimate using displacement data.
- Cooling-water heat calculation.
- Optional simplified exhaust-gas sensible-heat estimate.
- Heat-balance table and chart.
- CSV upload for multi-point test data and performance graphs.
- Manual-versus-digital result comparison.
- CSV downloads and a CSV template.

## Important engineering notes

- Use actual readings and properties supplied by your laboratory.
- Sample/template data are illustrative and are not research results.
- Indicated power cannot be determined from speed and torque alone. Supply a measured IP value or appropriate IMEP/displacement data.
- IMEP calculation uses total swept volume across all cylinders. Confirm cylinder count and volume convention against your lab manual.
- Exhaust heat is an approximate sensible-heat calculation using Cp = 1.05 kJ/(kg K), unless replaced with a lab-specified value.
- The simplified heat balance groups unmeasured losses into an unaccounted term; it is not a complete combustion/energy model.
- This is an educational prototype. Validate formulas, units, and assumptions with the project guide before presenting results.

## Suggested next improvements

1. Add a report export with experimental procedure and charts.
2. Add engine test-specific input modes (rope brake, eddy-current dynamometer, or other lab apparatus).
3. Add validation test cases approved by the project guide.
4. Add user login or experiment history only if required and appropriate.
