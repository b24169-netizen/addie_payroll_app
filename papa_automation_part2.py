import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Payroll Leave Entitlement Calculator")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    # -----------------------------
    # Load Excel
    # -----------------------------
    df = pd.read_excel(uploaded_file, header=[2,3])

    df.columns = [' '.join(col).strip() for col in df.columns]
    df.columns = [c.replace("Unnamed:", "").strip() for c in df.columns]

    date_col = [c for c in df.columns if "Date" in c][0]

    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")

    df = df.dropna(subset=[date_col])

    # -----------------------------
    # Create Payroll Periods
    # -----------------------------
    start_date = df[date_col].min()

    df["period_num"] = ((df[date_col] - start_date).dt.days // 28)

    df["period_start"] = start_date + pd.to_timedelta(df["period_num"] * 28, unit="D")
    df["period_end"] = df["period_start"] + pd.Timedelta(days=27)

    df["Period"] = (
        df["period_start"].dt.strftime("%d/%m/%Y")
        + " - "
        + df["period_end"].dt.strftime("%d/%m/%Y")
    )

    result = df.groupby(["period_start","Period"]).agg(
        total_days=(date_col,"nunique"),
        planned_hours=("Planned Duration","sum"),
        actual_hours=("Actual Duration","sum")
    ).reset_index()

    result = result.sort_values("period_start")
    result = result.drop(columns=["period_start"])

    # -----------------------------
    # Salary Input per Period
    # -----------------------------
    result["Salary"] = 0.0

    st.subheader("Payroll Summary (Enter Salary Per Period)")

    edited_df = st.data_editor(result)

    # -----------------------------
    # Totals
    # -----------------------------
    total_days = edited_df["total_days"].sum()
    total_salary = edited_df["Salary"].sum()

    st.subheader("Totals")

    st.write(f"Total Days Worked: **{total_days}**")
    st.write(f"Total Salary: **{total_salary:.2f}**")

    if total_days > 0:

        # -----------------------------
        # Main Calculations
        # -----------------------------
        salary_per_day = total_salary / total_days
        factor = 28 / 365
        entitled_leave = total_days * factor
        total_payable = entitled_leave * salary_per_day

        st.subheader("Leave Entitlement Calculation")

        st.write(f"Salary per Day: **{salary_per_day:.2f}**")
        st.write(f"Entitled Leave Days: **{entitled_leave:.2f}**")
        st.write(f"Total Leave Payable: **{total_payable:.2f}**")

        # -----------------------------
        # Custom Days Calculation
        # -----------------------------
        st.subheader("Custom Pay Calculation")

        input_days = st.number_input(
            "Enter number of days",
            min_value=0.0,
            step=1.0
        )

        custom_pay = salary_per_day * input_days

        st.write(f"Payable Amount: **{custom_pay:.2f}**")

        # -----------------------------
        # Download Excel Option
        # -----------------------------
        st.subheader("Download Results")

        export_df = edited_df.copy()
        export_df["Salary_per_day"] = salary_per_day
        export_df["Entitled_Leave_Days"] = entitled_leave
        export_df["Total_Leave_Payable"] = total_payable

        output = BytesIO()
        export_df.to_excel(output, index=False, engine="openpyxl")
        output.seek(0)

        st.download_button(
            label="Download Excel File",
            data=output,
            file_name="leave_payroll_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
