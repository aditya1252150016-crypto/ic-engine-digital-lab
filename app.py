import math
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="IC Engine Digital Lab", page_icon="⚙️", layout="wide")

st.title("⚙️ IC Engine Digital Lab")
st.caption("Web-based IC engine performance calculator, heat balance analysis and test graphs")
st.info(
    "Educational prototype. Enter actual laboratory readings and verify formulas, units, "
    "and assumptions with your lab manual or faculty before using results in a report."
)

with st.sidebar:
    st.header("Experiment setup")
    engine_type = st.selectbox(
        "Engine type",
        ["4-stroke diesel", "4-stroke petrol", "2-stroke", "Other / unspecified"],
    )
    test_name = st.text_input("Experiment / test name", "IC Engine Performance Test")
    operator = st.text_input("Student / team (optional)", "")
    test_date = st.date_input("Test date", value=datetime.today().date())

    st.divider()
    st.subheader("Engine specifications")
    bore_mm = st.number_input("Bore diameter (mm)", min_value=1.0, value=80.0, step=1.0)
    stroke_mm = st.number_input("Stroke length (mm)", min_value=1.0, value=110.0, step=1.0)
    num_cylinders = st.number_input("Number of cylinders", min_value=1, value=1, step=1)
    compression_ratio = st.number_input("Compression ratio", min_value=1.0, value=16.0, step=0.5)
    max_power_kw = st.number_input("Rated maximum power (kW)", min_value=0.1, value=3.68, step=0.1)
    max_speed_rpm = st.number_input("Rated maximum speed (RPM)", min_value=1, value=1500, step=100)

    st.divider()
    st.subheader("Fuel properties")
    fuel_cv = st.number_input("Fuel calorific value (kJ/kg)", min_value=1.0, value=41000.0, step=100.0)
    fuel_density = st.number_input("Fuel density (kg/L)", min_value=0.01, value=0.80, step=0.01)

displacement_l = (
    math.pi * (bore_mm / 1000.0) ** 2 / 4
    * (stroke_mm / 1000.0) * num_cylinders * 1000.0
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1 · Performance calculator",
    "2 · Heat balance",
    "3 · CSV data & graphs",
    "4 · Manual comparison",
    "5 · Formula guide",
])

with tab1:
    st.subheader("Engine specifications summary")
    a, b, c = st.columns(3)
    a.metric("Total swept volume", f"{displacement_l:.3f} L")
    b.metric("Rated maximum power", f"{max_power_kw:.2f} kW")
    c.metric("Rated maximum speed", f"{max_speed_rpm} RPM")
    st.caption(f"Compression ratio: {compression_ratio:g}:1 · Cylinders: {num_cylinders}")

    st.subheader("Experimental readings")
    c1, c2, c3 = st.columns(3)
    with c1:
        speed = st.number_input("Engine speed (RPM)", min_value=0.0, value=1500.0, step=50.0)
        torque = st.number_input("Brake torque (N·m)", min_value=0.0, value=20.0, step=1.0)
        fuel_input_type = st.selectbox("Fuel flow input", ["Mass flow (kg/h)", "Volume flow (mL/min)"])
        if fuel_input_type == "Mass flow (kg/h)":
            fuel_mass_kg_h = st.number_input("Fuel mass flow (kg/h)", min_value=0.0, value=1.2, step=0.1)
            fuel_mass_kg_s = fuel_mass_kg_h / 3600.0
        else:
            fuel_volume_ml_min = st.number_input("Fuel volume flow (mL/min)", min_value=0.0, value=25.0, step=1.0)
            fuel_mass_kg_s = fuel_volume_ml_min / 1_000_000.0 * fuel_density * 60.0
    with c2:
        cooling_water_kg_s = st.number_input("Cooling-water flow (kg/s)", min_value=0.0, value=0.10, step=0.01, format="%.4f")
        cooling_in = st.number_input("Cooling-water inlet temperature (°C)", value=25.0, step=1.0)
        cooling_out = st.number_input("Cooling-water outlet temperature (°C)", value=35.0, step=1.0)
        ambient_temp = st.number_input("Ambient temperature (°C)", value=25.0, step=1.0)
    with c3:
        exhaust_mass_kg_s = st.number_input("Exhaust-gas flow (kg/s; optional)", min_value=0.0, value=0.0, step=0.01, format="%.4f")
        exhaust_temp = st.number_input("Exhaust-gas temperature (°C)", value=250.0, step=5.0)
        ip_method = st.selectbox("Indicated power source", [
            "Not supplied", "Measured/calculated IP (kW)",
            "IMEP-based calculation (4-stroke)", "IMEP-based calculation (2-stroke)"
        ])
        indicated_power_kw = None
        if ip_method == "Measured/calculated IP (kW)":
            indicated_power_kw = st.number_input("Indicated power (kW)", min_value=0.0, value=2.5, step=0.1)
        elif ip_method.startswith("IMEP-based"):
            imep_bar = st.number_input("Indicated mean effective pressure (bar)", min_value=0.0, value=6.0, step=0.5)
            strokes = 4 if "4-stroke" in ip_method else 2
            if speed > 0:
                indicated_power_kw = imep_bar * 1e5 * (displacement_l / 1000.0) * (
                    speed / (60.0 * (strokes / 2.0))
                ) / 1000.0
            st.caption(f"Using {strokes}-stroke cycle and {displacement_l:.3f} L total displacement.")

    if st.button("Calculate performance", type="primary", use_container_width=True):
        errors = []
        if speed <= 0:
            errors.append("Engine speed must be greater than zero.")
        if fuel_mass_kg_s <= 0:
            errors.append("Fuel flow must be greater than zero.")
        if cooling_out < cooling_in:
            errors.append("Cooling-water outlet temperature is below inlet temperature. Check readings.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            bp_kw = 2 * math.pi * speed * torque / 60000.0
            fuel_heat_kw = fuel_mass_kg_s * fuel_cv
            cooling_heat_kw = cooling_water_kg_s * 4.186 * (cooling_out - cooling_in)
            exhaust_heat_kw = None
            if exhaust_mass_kg_s > 0:
                exhaust_heat_kw = exhaust_mass_kg_s * 1.05 * max(exhaust_temp - ambient_temp, 0.0)
            brake_eff = bp_kw / fuel_heat_kw * 100 if fuel_heat_kw > 0 else None
            bsfc = fuel_mass_kg_s * 3600 / bp_kw if bp_kw > 0 else None
            mech_eff = bp_kw / indicated_power_kw * 100 if indicated_power_kw and indicated_power_kw > 0 else None
            unaccounted_kw = fuel_heat_kw - bp_kw - cooling_heat_kw - (exhaust_heat_kw or 0.0)
            unaccounted_pct = unaccounted_kw / fuel_heat_kw * 100 if fuel_heat_kw > 0 else None

            result = {
                "Test name": test_name,
                "Date": str(test_date),
                "Student/team": operator,
                "Engine type": engine_type,
                "Speed (RPM)": speed,
                "Torque (N·m)": torque,
                "Total displacement (L)": displacement_l,
                "Brake power (kW)": bp_kw,
                "Indicated power (kW)": indicated_power_kw,
                "Fuel flow (kg/s)": fuel_mass_kg_s,
                "Fuel energy input (kW)": fuel_heat_kw,
                "Cooling-water heat (kW)": cooling_heat_kw,
                "Exhaust heat (kW)": exhaust_heat_kw,
                "Unaccounted heat (kW)": unaccounted_kw,
                "Brake thermal efficiency (%)": brake_eff,
                "Mechanical efficiency (%)": mech_eff,
                "BSFC (kg/kWh)": bsfc,
                "Unaccounted heat (%)": unaccounted_pct,
            }
            st.session_state["single_result"] = result
            st.success("Calculation completed.")
    if "single_result" in st.session_state:
        r = st.session_state["single_result"]
        st.subheader("Calculated results")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Brake power", f'{r["Brake power (kW)"]:.3f} kW')
        m2.metric("Brake thermal efficiency", f'{r["Brake thermal efficiency (%)"]:.2f}%')
        m3.metric("BSFC", f'{r["BSFC (kg/kWh)"]:.3f} kg/kWh' if r["BSFC (kg/kWh)"] is not None else "N/A")
        m4.metric("Indicated power", f'{r["Indicated power (kW)"]:.3f} kW' if r["Indicated power (kW)"] is not None else "Not supplied")
        if r["Mechanical efficiency (%)"] is not None:
            st.metric("Mechanical efficiency", f'{r["Mechanical efficiency (%)"]:.2f}%')
            if r["Mechanical efficiency (%)"] > 100:
                st.warning("Mechanical efficiency exceeds 100%. Check readings and units.")
        if r["Brake thermal efficiency (%)"] > 100:
            st.warning("Brake thermal efficiency exceeds 100%. Check fuel flow, calorific value and units.")
        if r["Unaccounted heat (kW)"] < 0:
            st.warning("Calculated heat leaving the system exceeds fuel energy input. Check readings and assumptions.")
        st.dataframe(pd.DataFrame([r]).T.rename(columns={0: "Value"}), use_container_width=True)
        st.download_button(
            "Download single-point results (CSV)",
            pd.DataFrame([r]).to_csv(index=False).encode("utf-8"),
            file_name="ic_engine_single_point_results.csv",
            mime="text/csv",
        )

with tab2:
    st.subheader("Heat balance")
    if "single_result" not in st.session_state:
        st.info("Calculate a single operating point in Tab 1 first.")
    else:
        r = st.session_state["single_result"]
        heat_rows = [
            ("Brake power", r["Brake power (kW)"]),
            ("Cooling-water heat", r["Cooling-water heat (kW)"]),
        ]
        if r["Exhaust heat (kW)"] is not None:
            heat_rows.append(("Exhaust-gas sensible heat", r["Exhaust heat (kW)"]))
        heat_rows.append(("Unaccounted heat", r["Unaccounted heat (kW)"]))
        heat_df = pd.DataFrame(heat_rows, columns=["Heat component", "Heat (kW)"])
        fuel_input = r["Fuel energy input (kW)"]
        heat_df["Percentage of fuel input (%)"] = heat_df["Heat (kW)"] / fuel_input * 100 if fuel_input else 0
        st.metric("Fuel energy input", f"{fuel_input:.3f} kW")
        st.plotly_chart(px.bar(heat_df, x="Heat component", y="Heat (kW)", color="Heat component", title="Heat balance components"), use_container_width=True)
        st.dataframe(heat_df.round(3), use_container_width=True)
        st.caption("Exhaust heat is an estimate using Cp = 1.05 kJ/(kg·K). Radiation and other losses are included in unaccounted heat.")

with tab3:
    st.subheader("Multiple test readings and graphs")
    st.write("Download the CSV template, enter measured readings in Excel, save as CSV, then upload it here.")
    template = pd.DataFrame({
        "Speed_rpm": [1000, 1200, 1400],
        "Torque_Nm": [10, 15, 20],
        "FuelFlow_kg_h": [0.7, 0.9, 1.2],
        "CoolingWater_kg_s": [0.08, 0.09, 0.10],
        "CoolingIn_C": [25, 25, 25],
        "CoolingOut_C": [31, 33, 35],
        "IP_kW_optional": [None, None, None],
    })
    st.download_button("Download CSV template", template.to_csv(index=False).encode("utf-8"), file_name="ic_engine_test_template.csv", mime="text/csv")
    uploaded = st.file_uploader("Upload your experimental CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            required = ["Speed_rpm", "Torque_Nm", "FuelFlow_kg_h", "CoolingWater_kg_s", "CoolingIn_C", "CoolingOut_C"]
            missing = [col for col in required if col not in df.columns]
            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                for col in required + (["IP_kW_optional"] if "IP_kW_optional" in df.columns else []):
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                df["BrakePower_kW"] = 2 * math.pi * df["Speed_rpm"] * df["Torque_Nm"] / 60000.0
                df["FuelFlow_kg_s"] = df["FuelFlow_kg_h"] / 3600.0
                df["FuelInput_kW"] = df["FuelFlow_kg_s"] * fuel_cv
                df["CoolingHeat_kW"] = df["CoolingWater_kg_s"] * 4.186 * (df["CoolingOut_C"] - df["CoolingIn_C"])
                df["BrakeThermalEfficiency_pct"] = df["BrakePower_kW"] / df["FuelInput_kW"].replace(0, float("nan")) * 100
                df["BSFC_kg_kWh"] = df["FuelFlow_kg_h"] / df["BrakePower_kW"].replace(0, float("nan"))
                if "IP_kW_optional" in df.columns:
                    df["MechanicalEfficiency_pct"] = df["BrakePower_kW"] / df["IP_kW_optional"].replace(0, float("nan")) * 100
                df["UnaccountedHeat_kW_no_exhaust_measurement"] = df["FuelInput_kW"] - df["BrakePower_kW"] - df["CoolingHeat_kW"]
                st.dataframe(df, use_container_width=True)
                x_axis = st.selectbox("X-axis", ["Speed_rpm", "Torque_Nm", "BrakePower_kW", "FuelFlow_kg_h"])
                y_axis = st.selectbox("Y-axis", ["BrakePower_kW", "BrakeThermalEfficiency_pct", "BSFC_kg_kWh", "CoolingHeat_kW", "UnaccountedHeat_kW_no_exhaust_measurement"])
                st.plotly_chart(px.line(df, x=x_axis, y=y_axis, markers=True, title=f"{y_axis} vs {x_axis}"), use_container_width=True)
                st.download_button("Download calculated dataset", df.to_csv(index=False).encode("utf-8"), file_name="ic_engine_calculated_dataset.csv", mime="text/csv")
                if (df["CoolingOut_C"] < df["CoolingIn_C"]).any():
                    st.warning("One or more rows have cooling-water outlet temperature below inlet temperature.")
        except Exception as exc:
            st.error(f"Could not process this CSV: {exc}")

with tab4:
    st.subheader("Manual vs digital calculation comparison")
    if "single_result" not in st.session_state:
        st.info("Calculate a single operating point in Tab 1 first.")
    else:
        r = st.session_state["single_result"]
        comparison_rows = []
        for label in ["Brake power (kW)", "Brake thermal efficiency (%)", "BSFC (kg/kWh)"]:
            digital = r[label]
            if digital is None or not math.isfinite(float(digital)):
                continue
            manual = st.number_input(f"Manual {label}", min_value=0.0, value=float(digital), key=f"manual_{label}")
            absolute_error = abs(manual - digital)
            percentage_error = absolute_error / abs(digital) * 100 if digital != 0 else 0.0
            comparison_rows.append({
                "Parameter": label,
                "Manual value": manual,
                "Digital value": digital,
                "Absolute error": absolute_error,
                "Percentage error (%)": percentage_error,
            })
        if comparison_rows:
            comparison = pd.DataFrame(comparison_rows)
            st.dataframe(comparison.round(4), use_container_width=True)
            st.download_button("Download comparison CSV", comparison.to_csv(index=False).encode("utf-8"), file_name="manual_vs_digital_comparison.csv", mime="text/csv")

with tab5:
    st.subheader("Formula guide")
    formulas = [
        ("Brake power", "BP = 2πNT / 60000", "N in RPM, T in N·m; result in kW."),
        ("Fuel energy input", "Q̇fuel = fuel mass flow × calorific value", "kg/s × kJ/kg gives kW."),
        ("Cooling-water heat", "Q̇cool = ṁ × Cp × (Tout − Tin)", "Cp for water ≈ 4.186 kJ/(kg·K)."),
        ("Brake thermal efficiency", "ηbth = BP / fuel energy input × 100", "Percentage."),
        ("BSFC", "BSFC = fuel flow (kg/h) / BP (kW)", "Result in kg/kWh."),
        ("Mechanical efficiency", "ηm = BP / IP × 100", "Requires valid indicated power."),
        ("IMEP-based IP", "IP = IMEP × total swept volume × power cycles per second", "4-stroke cycles: RPM/120; 2-stroke cycles: RPM/60."),
    ]
    st.table(pd.DataFrame(formulas, columns=["Parameter", "Formula", "Notes"]))
    st.warning("Sample readings are for demonstration only. Use actual lab readings and your instructor's approved equations.")

st.divider()
st.caption("IC Engine Digital Lab · Student project prototype · Verify calculations against your lab manual.")
