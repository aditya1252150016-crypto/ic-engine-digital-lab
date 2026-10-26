import math
from datetime import datetime
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="IC Engine Digital Lab",
    page_icon="⚙️",
    layout="wide",
)

st.markdown("""
<style>
    .main .block-container {padding-top: 1.6rem; padding-bottom: 2.5rem;}
    div[data-testid="stMetric"] {
        background: rgba(120, 120, 120, 0.08);
        border: 1px solid rgba(120, 120, 120, 0.18);
        padding: 14px 16px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚙️ IC Engine Digital Lab")
st.caption("Web-based IC engine performance calculator • Heat balance • Data validation")
st.info(
    "Educational engineering tool. Enter measured laboratory readings and verify the "
    "calculation method against your lab manual/instructor before using results in a report."
)

with st.sidebar:
    st.header("Experiment setup")
    engine_type = st.selectbox("Engine type", ["4-stroke petrol", "4-stroke diesel", "2-stroke", "Other / unspecified"])
    test_name = st.text_input("Experiment / test name", "IC Engine Performance Test")
    operator = st.text_input("Student / team (optional)", "")
    test_date = st.date_input("Test date", value=datetime.today().date())
        st.divider()
    st.subheader("Engine Specifications")

    bore_mm = st.number_input(
        "Bore diameter (mm)",
        min_value=1.0,
        value=80.0,
        step=1.0
    )

    stroke_mm = st.number_input(
        "Stroke length (mm)",
        min_value=1.0,
        value=110.0,
        step=1.0
    )

    num_cylinders = st.number_input(
        "Number of cylinders",
        min_value=1,
        value=1,
        step=1
    )

    compression_ratio = st.number_input(
        "Compression ratio",
        min_value=1.0,
        value=16.0,
        step=0.5
    )

    max_power_kw = st.number_input(
        "Maximum engine power (kW)",
        min_value=0.1,
        value=3.68,
        step=0.1
    )

    max_speed_rpm = st.number_input(
        "Maximum engine speed (RPM)",
        min_value=1,
        value=1500,
        step=100
    )
    st.divider()
    st.subheader("Calculation assumptions")
    fuel_cv = st.number_input("Fuel calorific value (kJ/kg)", min_value=1.0, value=44000.0, step=100.0)
    fuel_density = st.number_input("Fuel density (kg/L), if volume flow is used", min_value=0.01, value=0.74, step=0.01)
    st.caption("Use the calorific value and density supplied by your laboratory or fuel specification.")

tabs = st.tabs([
    "1 · Single-point calculator",
    "2 · Heat balance",
    "3 · Test data & graphs",
    "4 · Manual comparison",
    "5 · Formula guide",
])

# ------------------ Single point ------------------
with tabs[0]:
    st.subheader("Engine readings")
    st.write("Enter readings from one steady operating point. Use the units shown.")
    c1, c2, c3 = st.columns(3)
    with c1:
        speed = st.number_input("Engine speed (rpm)", min_value=0.0, value=1500.0, step=50.0)
        torque = st.number_input("Brake torque (N·m)", min_value=0.0, value=20.0, step=1.0)
        fuel_rate_type = st.selectbox("Fuel flow input", ["Mass flow (kg/h)", "Volume flow (mL/min)"])
    with c2:
        if fuel_rate_type == "Mass flow (kg/h)":
            fuel_mass_kg_h = st.number_input("Fuel mass flow (kg/h)", min_value=0.0, value=1.2, step=0.1)
            fuel_mass_kg_s = fuel_mass_kg_h / 3600.0
        else:
            fuel_volume_ml_min = st.number_input("Fuel volume flow (mL/min)", min_value=0.0, value=25.0, step=1.0)
            fuel_mass_kg_s = (fuel_volume_ml_min / 1_000_000.0) * fuel_density * 60.0
        cooling_water_kg_s = st.number_input("Cooling-water mass flow (kg/s)", min_value=0.0, value=0.10, step=0.01, format="%.4f")
        cooling_in = st.number_input("Cooling-water inlet temperature (°C)", value=25.0, step=1.0)
    with c3:
        cooling_out = st.number_input("Cooling-water outlet temperature (°C)", value=35.0, step=1.0)
        exhaust_mass_kg_s = st.number_input("Exhaust-gas mass flow (kg/s, optional)", min_value=0.0, value=0.0, step=0.01, format="%.4f")
        exhaust_temp = st.number_input("Exhaust-gas temperature (°C)", value=250.0, step=5.0)
        ambient_temp = st.number_input("Ambient/reference temperature (°C)", value=25.0, step=1.0)

    st.markdown("**Indicated power (optional measured value)**")
    ip_col1, ip_col2 = st.columns(2)
    with ip_col1:
        ip_method = st.selectbox("Indicated power source", [
            "Not supplied",
            "Measured/calculated IP (kW)",
            "IMEP-based calculation (4-stroke)",
            "IMEP-based calculation (2-stroke)",
        ])
    with ip_col2:
        if ip_method == "Measured/calculated IP (kW)":
            indicated_power_kw = st.number_input("Indicated power (kW)", min_value=0.0, value=8.0, step=0.5)
        elif ip_method.startswith("IMEP-based"):
        imep_bar = st.number_input(
            "Indicated mean effective pressure (bar)",
            min_value=0.0,
            value=6.0,
            step=0.5
        )

        displacement_l = (
            3.141592653589793
            * (bore_mm / 1000.0) ** 2
            / 4
            * (stroke_mm / 1000.0)
            * num_cylinders
            * 1000.0
        )

        st.metric(
            "Calculated engine displacement",
            f"{displacement_l:.3f} L"
        )

        strokes = 4 if "4-stroke" in ip_method else 2

        indicated_power_kw = (
            (imep_bar * 1e5)
            * (displacement_l / 1000.0)
            * (speed / (60.0 * (strokes / 2.0)))
            / 1000.0
        )
            else:
        indicated_power_kw = None
        st.caption("IP requires an indicated-power measurement or suitable cylinder/IMEP data.")
        
    if st.button("Calculate performance", type="primary", use_container_width=True):
        errors = []
        if speed <= 0:
            errors.append("Engine speed must be greater than zero.")
        if fuel_mass_kg_s <= 0:
            errors.append("Fuel flow must be greater than zero to calculate fuel-based performance.")
        if cooling_out < cooling_in:
            errors.append("Cooling-water outlet temperature is below inlet temperature; verify the readings.")
        if fuel_cv <= 0:
            errors.append("Calorific value must be greater than zero.")
        if errors:
            for err in errors:
                st.error(err)
            st.stop()

        bp_kw = 2 * math.pi * speed * torque / 60000.0
        fuel_heat_kw = fuel_mass_kg_s * fuel_cv
        cp_water = 4.186  # kJ/(kg K)
        cooling_heat_kw = cooling_water_kg_s * cp_water * (cooling_out - cooling_in)
        exhaust_heat_kw = None
        if exhaust_mass_kg_s > 0:
            # Approximate sensible heat; use lab-specified exhaust cp where available.
            cp_exhaust = 1.05  # kJ/(kg K), approximation
            exhaust_heat_kw = exhaust_mass_kg_s * cp_exhaust * max(exhaust_temp - ambient_temp, 0.0)

        brake_thermal_eff = bp_kw / fuel_heat_kw * 100.0 if fuel_heat_kw > 0 else None
        bsfc = fuel_mass_kg_s * 3600.0 / bp_kw if bp_kw > 0 else None  # kg/kWh
        mechanical_eff = bp_kw / indicated_power_kw * 100.0 if indicated_power_kw and indicated_power_kw > 0 else None
        ip_kw = indicated_power_kw if indicated_power_kw and indicated_power_kw > 0 else None

        known_terms = bp_kw + cooling_heat_kw + (exhaust_heat_kw or 0.0)
        unaccounted_kw = fuel_heat_kw - known_terms
        unaccounted_pct = unaccounted_kw / fuel_heat_kw * 100.0 if fuel_heat_kw else None

        result = {
            "Test name": test_name,
            "Date": str(test_date),
            "Engine type": engine_type,
            "Speed (rpm)": speed,
            "Torque (N·m)": torque,
            "Brake power (kW)": bp_kw,
            "Indicated power (kW)": ip_kw,
            "Fuel flow (kg/s)": fuel_mass_kg_s,
            "Fuel energy input (kW)": fuel_heat_kw,
            "Cooling-water heat (kW)": cooling_heat_kw,
            "Exhaust heat (kW)": exhaust_heat_kw,
            "Unaccounted heat (kW)": unaccounted_kw,
            "Brake thermal efficiency (%)": brake_thermal_eff,
            "Mechanical efficiency (%)": mechanical_eff,
            "BSFC (kg/kWh)": bsfc,
            "Unaccounted heat (%)": unaccounted_pct,
        }
        st.session_state["single_result"] = result
        st.session_state["single_inputs"] = {
            "speed": speed, "torque": torque, "fuel_mass_kg_s": fuel_mass_kg_s,
            "cooling_water_kg_s": cooling_water_kg_s, "cooling_in": cooling_in,
            "cooling_out": cooling_out, "exhaust_mass_kg_s": exhaust_mass_kg_s,
            "exhaust_temp": exhaust_temp, "ambient_temp": ambient_temp,
            "fuel_cv": fuel_cv, "indicated_power_kw": ip_kw,
        }

    if "single_result" in st.session_state:
        r = st.session_state["single_result"]
        st.divider()
        st.subheader("Calculated results")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Brake power", f'{r["Brake power (kW)"]:.3f} kW')
        m2.metric("Brake thermal efficiency", f'{r["Brake thermal efficiency (%)"]:.2f}%')
        m3.metric("BSFC", f'{r["BSFC (kg/kWh)"]:.3f} kg/kWh' if r["BSFC (kg/kWh)"] is not None else "N/A")
        m4.metric("Indicated power", f'{r["Indicated power (kW)"]:.3f} kW' if r["Indicated power (kW)"] is not None else "Not supplied")
        if r["Mechanical efficiency (%)"] is not None:
            st.metric("Mechanical efficiency", f'{r["Mechanical efficiency (%)"]:.2f}%')
            if r["Mechanical efficiency (%)"] > 100:
                st.warning("Mechanical efficiency exceeds 100%. Check IP/BP values and units.")
        if r["Brake thermal efficiency (%)"] > 100:
            st.warning("Brake thermal efficiency exceeds 100%. Check fuel flow, calorific value and power units.")
        if r["Unaccounted heat (kW)"] < 0:
            st.warning("Calculated heat leaving the system exceeds fuel energy input. Check measured flows, temperatures, assumptions and units.")
        st.dataframe(pd.DataFrame([r]).T.rename(columns={0: "Value"}), use_container_width=True)
        st.download_button(
            "Download single-point results (CSV)",
            data=pd.DataFrame([r]).to_csv(index=False).encode("utf-8"),
            file_name="ic_engine_single_point_results.csv",
            mime="text/csv",
        )

# ------------------ Heat balance ------------------
with tabs[1]:
    st.subheader("Heat balance visualization")
    st.write("Uses the most recent calculation from the Single-point calculator.")
    if "single_result" not in st.session_state:
        st.warning("Calculate a single operating point in Tab 1 first.")
    else:
        r = st.session_state["single_result"]
        heat_values = [
            ("Brake power", r["Brake power (kW)"]),
            ("Cooling-water heat", r["Cooling-water heat (kW)"]),
        ]
        if r["Exhaust heat (kW)"] is not None:
            heat_values.append(("Exhaust-gas sensible heat", r["Exhaust heat (kW)"]))
        heat_values.append(("Unaccounted heat", r["Unaccounted heat (kW)"]))
        heat_df = pd.DataFrame(heat_values, columns=["Heat component", "Heat (kW)"])
        heat_df["Percentage of fuel energy (%)"] = heat_df["Heat (kW)"] / r["Fuel energy input (kW)"] * 100.0
        st.metric("Fuel energy input", f'{r["Fuel energy input (kW)"]:.3f} kW')
        fig = px.bar(heat_df, x="Heat component", y="Heat (kW)", color="Heat component",
                     title="Heat balance components", text_auto=".2f")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(heat_df.round(3), use_container_width=True)
        total_accounted = sum(v for _, v in heat_values)
        st.write(f"Heat balance total (including unaccounted term): **{total_accounted:.3f} kW**")
        st.write("The unaccounted term is computed as fuel energy input minus the included output terms. "
                 "If exhaust mass flow is not entered, exhaust heat remains included in the unaccounted term.")
        st.caption("Exhaust heat is an approximation using Cp = 1.05 kJ/(kg·K) unless your lab specifies another value. "
                   "Radiation/convection and other losses are not separately measured in this simplified balance.")

# ------------------ Dataset and graphs ------------------
with tabs[2]:
    st.subheader("Multi-point test data")
    st.write("Upload a CSV containing repeated steady-state readings, or use the sample template.")
    template = pd.DataFrame({
        "Speed_rpm": [1000, 1200, 1400],
        "Torque_Nm": [10, 15, 20],
        "FuelFlow_kg_h": [0.7, 0.9, 1.2],
        "CoolingWater_kg_s": [0.08, 0.09, 0.10],
        "CoolingIn_C": [25, 25, 25],
        "CoolingOut_C": [31, 33, 35],
        "IP_kW_optional": [None, None, None],
    })
    st.download_button("Download CSV template", template.to_csv(index=False).encode("utf-8"),
                       "ic_engine_test_template.csv", "text/csv")
    uploaded = st.file_uploader("Upload your experimental CSV", type=["csv"])
    if uploaded is not None:
        try:
            df = pd.read_csv(uploaded)
            required = ["Speed_rpm", "Torque_Nm", "FuelFlow_kg_h", "CoolingWater_kg_s", "CoolingIn_C", "CoolingOut_C"]
            missing = [col for col in required if col not in df.columns]
            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                numeric_cols = required + (["IP_kW_optional"] if "IP_kW_optional" in df.columns else [])
                for col in numeric_cols:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                df["BrakePower_kW"] = 2 * math.pi * df["Speed_rpm"] * df["Torque_Nm"] / 60000.0
                df["FuelFlow_kg_s"] = df["FuelFlow_kg_h"] / 3600.0
                df["FuelInput_kW"] = df["FuelFlow_kg_s"] * fuel_cv
                df["CoolingHeat_kW"] = df["CoolingWater_kg_s"] * 4.186 * (df["CoolingOut_C"] - df["CoolingIn_C"])
                df["BrakeThermalEfficiency_pct"] = df["BrakePower_kW"] / df["FuelInput_kW"] * 100.0
                df["BSFC_kg_kWh"] = df["FuelFlow_kg_h"] / df["BrakePower_kW"]
                if "IP_kW_optional" in df.columns:
                    df["MechanicalEfficiency_pct"] = df["BrakePower_kW"] / df["IP_kW_optional"] * 100.0
                df["UnaccountedHeat_kW_no_exhaust_measurement"] = df["FuelInput_kW"] - df["BrakePower_kW"] - df["CoolingHeat_kW"]
                st.dataframe(df, use_container_width=True)
                x_options = ["Speed_rpm", "Torque_Nm", "BrakePower_kW", "FuelFlow_kg_h"]
                x_axis = st.selectbox("X-axis", x_options, index=1)
                y_options = ["BrakePower_kW", "BrakeThermalEfficiency_pct", "BSFC_kg_kWh", "CoolingHeat_kW", "UnaccountedHeat_kW_no_exhaust_measurement"]
                y_axis = st.selectbox("Y-axis", y_options)
                fig = px.line(df, x=x_axis, y=y_axis, markers=True, title=f"{y_axis} vs {x_axis}")
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("Download calculated dataset", df.to_csv(index=False).encode("utf-8"),
                                   "ic_engine_calculated_dataset.csv", "text/csv")
                if (df["BrakeThermalEfficiency_pct"] > 100).any():
                    st.warning("One or more points have brake thermal efficiency above 100%; check units and readings.")
                if (df["CoolingOut_C"] < df["CoolingIn_C"]).any():
                    st.warning("One or more rows have cooling outlet temperature below inlet temperature.")
        except Exception as e:
            st.error(f"Could not read this CSV: {e}")

# ------------------ Manual comparison ------------------
with tabs[3]:
    st.subheader("Manual vs digital calculation comparison")
    st.write("Enter your independently calculated values. Comparison only works for values calculated from the same readings and method.")
    if "single_result" not in st.session_state:
        st.info("First calculate a single operating point in Tab 1. Then enter manual results here.")
    else:
        r = st.session_state["single_result"]
        rows = []
        fields = [
            ("Brake power (kW)", "Brake power (kW)"),
            ("Brake thermal efficiency (%)", "Brake thermal efficiency (%)"),
            ("BSFC (kg/kWh)", "BSFC (kg/kWh)"),
        ]
        if r["Indicated power (kW)"] is not None:
            fields.append(("Indicated power (kW)", "Indicated power (kW)"))
        for label, key in fields:
            digital = r[key]
            if digital is None:
                continue
            manual = st.number_input(f"Manual {label}", min_value=0.0, value=float(digital), key=f"manual_{key}")
            absolute_error = abs(manual - digital)
            percentage_error = absolute_error / abs(digital) * 100.0 if digital != 0 else (0.0 if manual == 0 else None)
            rows.append({"Parameter": label, "Manual value": manual, "Digital value": digital,
                         "Absolute error": absolute_error, "Percentage error (%)": percentage_error})
        if rows:
            comp = pd.DataFrame(rows)
            st.dataframe(comp.round(5), use_container_width=True)
            st.download_button("Download comparison (CSV)", comp.to_csv(index=False).encode("utf-8"),
                               "manual_vs_digital_comparison.csv", "text/csv")
            st.caption("A close match validates implementation against your chosen manual calculation, but does not by itself validate the experimental measurements.")

# ------------------ Formula guide ------------------
with tabs[4]:
    st.subheader("Formula guide and assumptions")
    formulas = [
        ("Brake power", "BP = 2πNT / 60,000", "N in rpm, T in N·m; result in kW."),
        ("Fuel energy input", "Q̇fuel = ṁfuel × CV", "ṁ in kg/s and CV in kJ/kg; result in kW."),
        ("Cooling-water heat", "Q̇cool = ṁwater × Cp × (Tout − Tin)", "Cp ≈ 4.186 kJ/(kg·K) for water."),
        ("Brake thermal efficiency", "ηbth = BP / Q̇fuel × 100", "Requires positive fuel energy input."),
        ("Brake-specific fuel consumption", "BSFC = fuel flow (kg/h) / BP (kW)", "Result in kg/kWh."),
        ("Mechanical efficiency", "ηm = BP / IP × 100", "Requires a valid indicated-power value."),
        ("Unaccounted heat", "Q̇unaccounted = Q̇fuel − BP − Q̇cool − Q̇exhaust", "Only as complete as the heat terms measured/included."),
        ("Indicated power from IMEP", "IP = pimep × Vd,total × power strokes per second", "4-stroke: power strokes per cylinder per second = N/120; 2-stroke = N/60. Use total swept volume across all cylinders."),
    ]
    st.table(pd.DataFrame(formulas, columns=["Parameter", "Formula", "Notes"]))
    st.warning(
        "For IMEP-based IP, use total swept volume across all cylinders and a consistent pressure unit. "
        "If your lab manual uses a different convention or measurement setup, follow the lab manual and document it."
    )
    st.markdown("**Current scope limitations**")
    st.markdown("""
    - The single-point calculator calculates brake power from measured speed and torque.
    - Indicated power is not inferred from brake power; supply measured IP or IMEP and displacement data.
    - Exhaust heat is a simplified sensible-heat estimate if exhaust mass flow is provided.
    - Volumetric efficiency, air-fuel ratio and combustion-specific metrics require additional measurements.
    - The sample CSV values are demonstration-only; replace them with actual lab readings for academic reporting.
    """)

st.divider()
st.caption("IC Engine Digital Lab • Student project prototype • Verify equations, assumptions and units with your faculty/lab manual.")
