import math
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="IC Engine Digital Lab",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ IC Engine Digital Lab")
st.caption("Web-based IC engine performance calculator and heat-balance analysis")
st.info(
    "Use readings from your actual experiment. Confirm equations, units, and assumptions "
    "with your lab manual or faculty before submitting results."
)

# -------------------- Sidebar: engine specifications --------------------
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
    cylinders = st.number_input("Number of cylinders", min_value=1, value=1, step=1)
    compression_ratio = st.number_input("Compression ratio", min_value=1.0, value=16.0, step=0.5)
    rated_power_kw = st.number_input("Rated maximum power (kW)", min_value=0.1, value=3.68, step=0.1)
    rated_speed_rpm = st.number_input("Rated maximum speed (RPM)", min_value=1, value=1500, step=100)

    st.divider()
    st.subheader("Fuel and fluid properties")
    fuel_cv = st.number_input("Fuel calorific value (kJ/kg)", min_value=1.0, value=41000.0, step=100.0)
    fuel_density = st.number_input("Fuel density (kg/L)", min_value=0.01, value=0.80, step=0.01)
    water_cp = st.number_input("Specific heat of water (kJ/kg·K)", min_value=0.1, value=4.186, step=0.001, format="%.3f")
    exhaust_cp = st.number_input("Exhaust-gas Cp (kJ/kg·K; estimate)", min_value=0.1, value=1.05, step=0.05)

displacement_l = (
    math.pi * (bore_mm / 1000.0) ** 2 / 4.0
    * (stroke_mm / 1000.0) * cylinders * 1000.0
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["1 · Lab readings & heat balance", "2 · Performance calculator", "3 · CSV data & graphs", "4 · Formula guide"]
)

# -------------------- Tab 1: lab readings and heat balance --------------------
with tab1:
    st.subheader("Enter your laboratory observations")
    st.write("The default values are filled from the sample readings you provided. Change them if your lab readings differ.")

    with st.form("heat_balance_form"):
        st.markdown("**Electrical and engine readings**")
        c1, c2, c3 = st.columns(3)
        with c1:
            current_a = st.number_input("Current (A)", min_value=0.0, value=12.5, step=0.1)
            voltage_v = st.number_input("Voltage (V)", min_value=0.0, value=238.0, step=1.0)
        with c2:
            speed_rpm = st.number_input("Engine speed (RPM)", min_value=0.0, value=1500.0, step=50.0)
            measured_bp_kw = st.number_input(
                "Measured brake power (kW, if available)",
                min_value=0.0, value=0.0, step=0.1,
                help="Enter a verified brake-power value only. Leave 0 if it was not measured.",
            )
        with c3:
            fuel_volume_cc = st.number_input("Fuel volume used (cc)", min_value=0.0, value=50.0, step=5.0)
            fuel_time_s = st.number_input("Time for that fuel volume (s)", min_value=0.1, value=76.0, step=1.0)

        st.markdown("**Air/manometer and ambient readings**")
        c1, c2, c3 = st.columns(3)
        with c1:
            manometer_cm = st.number_input("Manometer reading (cm)", min_value=0.0, value=4.3, step=0.1)
        with c2:
            ambient_temp_c = st.number_input("Atmospheric temperature (°C)", value=25.0, step=1.0)
        with c3:
            atmospheric_pressure_mmhg = st.number_input("Atmospheric pressure (mmHg)", min_value=0.0, value=715.0, step=1.0)

        st.markdown("**Cooling-jacket water readings**")
        c1, c2, c3 = st.columns(3)
        with c1:
            jacket_in_c = st.number_input("Jacket water inlet (°C)", value=26.0, step=1.0)
        with c2:
            jacket_out_c = st.number_input("Jacket water outlet (°C)", value=62.0, step=1.0)
        with c3:
            jacket_flow_lpm = st.number_input("Jacket water flow (L/min)", min_value=0.0, value=3.0, step=0.1)

        st.markdown("**Exhaust calorimeter readings**")
        c1, c2, c3 = st.columns(3)
        with c1:
            gas_in_c = st.number_input("Exhaust gas at calorimeter inlet (°C)", value=550.0, step=5.0)
        with c2:
            gas_out_c = st.number_input("Exhaust gas at calorimeter outlet (°C)", value=120.0, step=5.0)
        with c3:
            calorimeter_flow_lpm = st.number_input("Calorimeter water flow (L/min)", min_value=0.0, value=2.9, step=0.1)

        c1, c2 = st.columns(2)
        with c1:
            calorimeter_water_in_c = st.number_input("Calorimeter water inlet (°C)", value=26.0, step=1.0)
        with c2:
            calorimeter_water_out_c = st.number_input("Calorimeter water outlet (°C)", value=45.0, step=1.0)

        calculate_heat = st.form_submit_button("Calculate heat balance", type="primary", use_container_width=True)

    if calculate_heat:
        errors = []
        if fuel_volume_cc <= 0:
            errors.append("Fuel volume must be greater than zero.")
        if fuel_time_s <= 0:
            errors.append("Fuel-consumption time must be greater than zero.")
        if jacket_out_c < jacket_in_c:
            errors.append("Jacket-water outlet temperature is below inlet temperature. Check your readings.")
        if calorimeter_water_out_c < calorimeter_water_in_c:
            errors.append("Calorimeter-water outlet temperature is below inlet temperature. Check your readings.")
        if errors:
            for message in errors:
                st.error(message)
        else:
            # 1 cc = 0.001 L. Density is in kg/L.
            fuel_mass_kg = (fuel_volume_cc / 1000.0) * fuel_density
            fuel_mass_flow_kg_s = fuel_mass_kg / fuel_time_s
            fuel_mass_flow_kg_h = fuel_mass_flow_kg_s * 3600.0
            fuel_heat_kw = fuel_mass_flow_kg_s * fuel_cv

            electrical_power_kw = current_a * voltage_v / 1000.0

            # Approximate water mass flow: 1 L of water ~= 1 kg.
            jacket_water_kg_s = jacket_flow_lpm / 60.0
            jacket_heat_kw = jacket_water_kg_s * water_cp * (jacket_out_c - jacket_in_c)

            calorimeter_water_kg_s = calorimeter_flow_lpm / 60.0
            calorimeter_water_heat_kw = (
                calorimeter_water_kg_s * water_cp
                * (calorimeter_water_out_c - calorimeter_water_in_c)
            )

            measured_terms_kw = jacket_heat_kw + calorimeter_water_heat_kw
            remaining_before_brake_kw = fuel_heat_kw - measured_terms_kw
            remaining_after_brake_kw = (
                fuel_heat_kw - measured_terms_kw - measured_bp_kw
                if measured_bp_kw > 0 else None
            )

            results = {
                "Test name": test_name,
                "Date": str(test_date),
                "Student/team": operator,
                "Engine type": engine_type,
                "Bore (mm)": bore_mm,
                "Stroke (mm)": stroke_mm,
                "Number of cylinders": cylinders,
                "Compression ratio": compression_ratio,
                "Rated power (kW)": rated_power_kw,
                "Rated speed (RPM)": rated_speed_rpm,
                "Current (A)": current_a,
                "Voltage (V)": voltage_v,
                "Electrical input power (kW)": electrical_power_kw,
                "Engine speed (RPM)": speed_rpm,
                "Fuel volume (cc)": fuel_volume_cc,
                "Fuel time (s)": fuel_time_s,
                "Fuel mass flow (kg/s)": fuel_mass_flow_kg_s,
                "Fuel mass flow (kg/h)": fuel_mass_flow_kg_h,
                "Fuel heat input (kW)": fuel_heat_kw,
                "Manometer reading (cm)": manometer_cm,
                "Atmospheric temperature (°C)": ambient_temp_c,
                "Atmospheric pressure (mmHg)": atmospheric_pressure_mmhg,
                "Jacket water flow (L/min)": jacket_flow_lpm,
                "Jacket water heat (kW)": jacket_heat_kw,
                "Calorimeter water flow (L/min)": calorimeter_flow_lpm,
                "Calorimeter water heat (kW)": calorimeter_water_heat_kw,
                "Exhaust gas inlet temperature (°C)": gas_in_c,
                "Exhaust gas outlet temperature (°C)": gas_out_c,
                "Remaining heat before brake power (kW)": remaining_before_brake_kw,
                "Measured brake power entered (kW)": measured_bp_kw if measured_bp_kw > 0 else None,
                "Remaining heat after measured brake power (kW)": remaining_after_brake_kw,
            }
            st.session_state["heat_balance_results"] = results
            st.session_state["heat_balance_inputs"] = {
                "fuel_heat_kw": fuel_heat_kw,
                "electrical_power_kw": electrical_power_kw,
                "jacket_heat_kw": jacket_heat_kw,
                "calorimeter_water_heat_kw": calorimeter_water_heat_kw,
                "remaining_before_brake_kw": remaining_before_brake_kw,
                "remaining_after_brake_kw": remaining_after_brake_kw,
                "measured_bp_kw": measured_bp_kw,
            }

    if "heat_balance_results" in st.session_state:
        r = st.session_state["heat_balance_results"]
        vals = st.session_state["heat_balance_inputs"]
        st.subheader("Calculated results")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Fuel heat input", f"{vals['fuel_heat_kw']:.3f} kW")
        m2.metric("Electrical input power (V × I)", f"{vals['electrical_power_kw']:.3f} kW")
        m3.metric("Jacket-water heat", f"{vals['jacket_heat_kw']:.3f} kW")
        m4.metric("Calorimeter-water heat", f"{vals['calorimeter_water_heat_kw']:.3f} kW")

        heat_rows = [
            ("Fuel heat input", vals["fuel_heat_kw"]),
            ("Jacket-water heat", vals["jacket_heat_kw"]),
            ("Calorimeter-water heat transfer", vals["calorimeter_water_heat_kw"]),
        ]
        if vals["measured_bp_kw"] > 0:
            heat_rows.append(("Measured brake power", vals["measured_bp_kw"]))
            heat_rows.append(("Remaining / unaccounted term", vals["remaining_after_brake_kw"]))
        else:
            heat_rows.append(("Remaining after the two water-side terms", vals["remaining_before_brake_kw"]))
        heat_df = pd.DataFrame(heat_rows, columns=["Term", "Value (kW)"])
        fuel_input = vals["fuel_heat_kw"]
        heat_df["Percentage of fuel input (%)"] = (
            heat_df["Value (kW)"] / fuel_input * 100.0 if fuel_input > 0 else 0.0
        )
        st.dataframe(heat_df.round(3), use_container_width=True)
        st.plotly_chart(
            px.bar(heat_df, x="Term", y="Value (kW)", title="Measured heat-balance terms"),
            use_container_width=True,
        )
        st.download_button(
            "Download heat-balance results (CSV)",
            pd.DataFrame([r]).to_csv(index=False).encode("utf-8"),
            file_name="ic_engine_heat_balance_results.csv",
            mime="text/csv",
        )
        st.warning(
            "Important: electrical input power is not automatically brake power. "
            "Calorimeter-water heat is the heat gained by the calorimeter water, not the total exhaust-gas heat. "
            "The remaining term is not a complete engine heat balance unless all required terms, including "
            "valid brake power and the lab-approved exhaust calculation, are included."
        )
        st.caption(
            "The manometer reading and gas temperatures are recorded, but exhaust-gas mass flow/heat is not "
            "calculated because the approved orifice equation and manometer-fluid details must be confirmed."
        )

# -------------------- Tab 2: performance calculator --------------------
with tab2:
    st.subheader("Engine specification summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total swept volume", f"{displacement_l:.3f} L")
    c2.metric("Rated maximum power", f"{rated_power_kw:.2f} kW")
    c3.metric("Rated maximum speed", f"{rated_speed_rpm} RPM")
    st.caption(f"Compression ratio: {compression_ratio:g}:1 · Cylinders: {cylinders}")

    st.subheader("Optional brake-power and efficiency calculation")
    st.write("Use this section if your lab has a measured brake torque and a suitable fuel-flow value.")
    with st.form("performance_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            perf_speed = st.number_input("Performance-test speed (RPM)", min_value=0.0, value=1500.0, step=50.0)
            torque_nm = st.number_input("Brake torque (N·m)", min_value=0.0, value=20.0, step=1.0)
        with c2:
            fuel_flow_kg_h = st.number_input("Fuel mass flow (kg/h)", min_value=0.0, value=1.2, step=0.1)
            cooling_flow_kg_s = st.number_input("Cooling-water flow (kg/s)", min_value=0.0, value=0.05, step=0.01, format="%.4f")
        with c3:
            cooling_in = st.number_input("Cooling-water inlet (°C)", value=26.0, step=1.0)
            cooling_out = st.number_input("Cooling-water outlet (°C)", value=62.0, step=1.0)
        indicated_power_kw = st.number_input("Indicated power (kW, optional; 0 if unknown)", min_value=0.0, value=0.0, step=0.1)
        run_performance = st.form_submit_button("Calculate performance", type="primary", use_container_width=True)

    if run_performance:
        if perf_speed <= 0 or fuel_flow_kg_h <= 0:
            st.error("Enter speed and fuel flow greater than zero.")
        elif cooling_out < cooling_in:
            st.error("Cooling-water outlet temperature is below inlet temperature. Check readings.")
        else:
            bp_kw = 2.0 * math.pi * perf_speed * torque_nm / 60000.0
            fuel_input_kw = (fuel_flow_kg_h / 3600.0) * fuel_cv
            cooling_heat_kw = cooling_flow_kg_s * water_cp * (cooling_out - cooling_in)
            bte = bp_kw / fuel_input_kw * 100.0 if fuel_input_kw > 0 else 0.0
            bsfc = fuel_flow_kg_h / bp_kw if bp_kw > 0 else None
            mech_eff = bp_kw / indicated_power_kw * 100.0 if indicated_power_kw > 0 else None
            perf_result = {
                "Brake power (kW)": bp_kw,
                "Fuel energy input (kW)": fuel_input_kw,
                "Cooling-water heat (kW)": cooling_heat_kw,
                "Brake thermal efficiency (%)": bte,
                "BSFC (kg/kWh)": bsfc,
                "Indicated power (kW)": indicated_power_kw if indicated_power_kw > 0 else None,
                "Mechanical efficiency (%)": mech_eff,
            }
            st.session_state["performance_results"] = perf_result

    if "performance_results" in st.session_state:
        p = st.session_state["performance_results"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Brake power", f"{p['Brake power (kW)']:.3f} kW")
        c2.metric("Brake thermal efficiency", f"{p['Brake thermal efficiency (%)']:.2f}%")
        c3.metric("BSFC", f"{p['BSFC (kg/kWh)']:.3f} kg/kWh" if p["BSFC (kg/kWh)"] is not None else "N/A")
        st.dataframe(pd.DataFrame([p]).T.rename(columns={0: "Value"}), use_container_width=True)
        if p["Brake thermal efficiency (%)"] > 100:
            st.warning("Brake thermal efficiency exceeds 100%. Check the readings, units, and fuel calorific value.")
        if p["Mechanical efficiency (%)"] is not None:
            if p["Mechanical efficiency (%)"] > 100:
                st.warning("Mechanical efficiency exceeds 100%. Check brake and indicated power values.")
            else:
                st.metric("Mechanical efficiency", f"{p['Mechanical efficiency (%)']:.2f}%")
        st.download_button(
            "Download performance results (CSV)",
            pd.DataFrame([p]).to_csv(index=False).encode("utf-8"),
            file_name="ic_engine_performance_results.csv",
            mime="text/csv",
        )

# -------------------- Tab 3: multi-point CSV --------------------
with tab3:
    st.subheader("Multiple test readings and graphs")
    st.write("Download the template, enter your measurements in Excel, save it as CSV, then upload it here.")
    template = pd.DataFrame({
        "Speed_rpm": [1000, 1200, 1400],
        "Torque_Nm": [10, 15, 20],
        "FuelFlow_kg_h": [0.7, 0.9, 1.2],
        "CoolingWater_kg_s": [0.05, 0.05, 0.05],
        "CoolingIn_C": [26, 26, 26],
        "CoolingOut_C": [35, 45, 55],
    })
    st.download_button(
        "Download CSV template",
        template.to_csv(index=False).encode("utf-8"),
        file_name="ic_engine_test_template.csv",
        mime="text/csv",
    )
    uploaded = st.file_uploader("Upload your experimental CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            required = [
                "Speed_rpm", "Torque_Nm", "FuelFlow_kg_h",
                "CoolingWater_kg_s", "CoolingIn_C", "CoolingOut_C",
            ]
            missing = [col for col in required if col not in df.columns]
            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                for col in required:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                if df[required].isna().any().any():
                    st.error("Some required CSV cells are blank or not numeric. Please correct the file and upload again.")
                else:
                    df["BrakePower_kW"] = 2.0 * math.pi * df["Speed_rpm"] * df["Torque_Nm"] / 60000.0
                    df["FuelFlow_kg_s"] = df["FuelFlow_kg_h"] / 3600.0
                    df["FuelInput_kW"] = df["FuelFlow_kg_s"] * fuel_cv
                    df["CoolingHeat_kW"] = (
                        df["CoolingWater_kg_s"] * water_cp * (df["CoolingOut_C"] - df["CoolingIn_C"])
                    )
                    df["BrakeThermalEfficiency_pct"] = (
                        df["BrakePower_kW"] / df["FuelInput_kW"].replace(0, float("nan")) * 100.0
                    )
                    df["BSFC_kg_kWh"] = (
                        df["FuelFlow_kg_h"] / df["BrakePower_kW"].replace(0, float("nan"))
                    )
                    df["RemainingHeat_kW_no_exhaust_term"] = (
                        df["FuelInput_kW"] - df["BrakePower_kW"] - df["CoolingHeat_kW"]
                    )
                    st.dataframe(df, use_container_width=True)
                    x_axis = st.selectbox("X-axis", ["Speed_rpm", "Torque_Nm", "BrakePower_kW", "FuelFlow_kg_h"])
                    y_axis = st.selectbox(
                        "Y-axis",
                        ["BrakePower_kW", "BrakeThermalEfficiency_pct", "BSFC_kg_kWh", "CoolingHeat_kW", "RemainingHeat_kW_no_exhaust_term"],
                    )
                    st.plotly_chart(
                        px.line(df, x=x_axis, y=y_axis, markers=True, title=f"{y_axis} vs {x_axis}"),
                        use_container_width=True,
                    )
                    st.download_button(
                        "Download calculated dataset",
                        df.to_csv(index=False).encode("utf-8"),
                        file_name="ic_engine_calculated_dataset.csv",
                        mime="text/csv",
                    )
                    if (df["CoolingOut_C"] < df["CoolingIn_C"]).any():
                        st.warning("One or more rows have cooling-water outlet temperature below inlet temperature.")
        except Exception as exc:
            st.error(f"Could not process this CSV: {exc}")

# -------------------- Tab 4: formulas --------------------
with tab4:
    st.subheader("Formula guide")
    formulas = [
        ("Swept volume", "V = π/4 × bore² × stroke × number of cylinders", "Convert dimensions to metres before calculation."),
        ("Fuel mass flow", "ṁfuel = (fuel volume × density) / time", "Convert cc to litres; density is in kg/L."),
        ("Fuel heat input", "Q̇fuel = ṁfuel × calorific value", "kg/s × kJ/kg gives kW."),
        ("Electrical input power", "P = V × I / 1000", "This is electrical input power, not automatically engine brake power."),
        ("Brake power", "BP = 2πNT / 60000", "N in RPM, T in N·m; result in kW."),
        ("Water-side heat transfer", "Q̇water = ṁwater × Cp × (Tout − Tin)", "Water flow in kg/s; Cp in kJ/(kg·K)."),
        ("Brake thermal efficiency", "ηbth = BP / fuel heat input × 100", "Requires valid brake power."),
        ("BSFC", "BSFC = fuel flow (kg/h) / BP (kW)", "Result in kg/kWh."),
        ("Mechanical efficiency", "ηm = BP / IP × 100", "Requires valid indicated power."),
    ]
    st.table(pd.DataFrame(formulas, columns=["Parameter", "Formula", "Notes"]))
    st.warning(
        "The manometer/orifice calculation is intentionally not automated until the approved equation, "
        "manometer fluid, and required constants are confirmed from your lab manual."
    )

st.divider()
st.caption("IC Engine Digital Lab · Student project prototype · Verify all calculations with your lab manual.")
