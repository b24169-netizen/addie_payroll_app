import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Leave Salary Calculator")

st.write("Enter days worked in each period and salary/day")

rows = 5  # number of rows

data = []

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.write("Period 1 Days")

with col2:
    st.write("Period 2 Days")

with col3:
    st.write("Period 3 Days")

with col4:
    st.write("Salary / Day")

for i in range(rows):
    c1, c2, c3, c4 = st.columns(4)

    p1 = c1.number_input(f"Row {i+1} P1", key=f"p1{i}")
    p2 = c2.number_input(f"Row {i+1} P2", key=f"p2{i}")
    p3 = c3.number_input(f"Row {i+1} P3", key=f"p3{i}")
    salary_day = c4.number_input(f"Row {i+1} Salary/Day", key=f"s{i}")

    total_days = p1 + p2 + p3
    total_salary = total_days * salary_day

    data.append({
        "Period1": p1,
        "Period2": p2,
        "Period3": p3,
        "Total Days": total_days,
        "Salary/Day": salary_day,
        "Total Salary": total_salary
    })

df = pd.DataFrame(data)

st.subheader("Table")
st.dataframe(df)

# totals
total_days_all = df["Total Days"].sum()
total_salary_all = df["Total Salary"].sum()

st.write("Total Days:", total_days_all)
st.write("Total Salary:", total_salary_all)

# leave calculation
factor = 28 / 365
entitled_leave = total_days_all * factor
salary_per_day = total_salary_all / total_days_all if total_days_all != 0 else 0
total_payable = entitled_leave * salary_per_day

st.subheader("Leave Calculation")

st.write("Salary / Day:", salary_per_day)
st.write("Total Entitled Leave:", entitled_leave)
st.write("Total Payable:", total_payable)

# custom days payout
st.subheader("Custom Days Calculation")

input_days = st.number_input("Enter Days")

custom_payment = salary_per_day * input_days

st.write("Amount:", custom_payment)

# -------- Excel Export --------
def convert_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    processed_data = output.getvalue()
    return processed_data

excel_file = convert_to_excel(df)

st.download_button(
    label="Download Excel",
    data=excel_file,
    file_name="leave_salary_calculation.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
