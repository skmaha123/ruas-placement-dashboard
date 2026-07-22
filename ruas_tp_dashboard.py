import git
import streamlit as st
import pandas as pd
import plotly.express as px
import time
import streamlit.components.v1 as components
from numpy import add
from websockets.version import commit

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="DIRECTORATE OF  TRAINING & PLACEMENTS, RUAS",
    page_icon="🎓",
    layout="wide"
)

# -------------------------------------------------
# RUAS THEME
# -------------------------------------------------

st.markdown("""
<style>
.main {
    background-color:#f8f9fc;
}

.metric-box{
    padding:20px;
    border-radius:15px;
    background:white;
    box-shadow:0px 2px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.markdown("""
<h1 style='text-align:center;color:#800000'>
🎓 DIRECTORATE OF  TRAINING & PLACEMENTS, RUAS
</h1>
<h4 style='text-align:center;color:#444444'>
Real-Time Placement Analytics Dashboard
</h4>
""", unsafe_allow_html=True)

st.divider()

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------

uploaded_file = st.sidebar.file_uploader(
    "Upload Placement Excel File",
    type=["xlsx"]
)

# -------------------------------------------------
# EXCEL FORMAT INFO
# -------------------------------------------------

with st.sidebar.expander("Expected Columns"):

    st.write("""
AcademicYear

Faculty

Department

Program

BatchStrength

EligibleStudents

Offers

Companies

HigherStudies

Entrepreneurship

Others

AverageSalary

MedianSalary

HighestSalary

PlacementStatus
""")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

if uploaded_file:

    df = pd.read_excel(uploaded_file)

else:

    st.warning(
        "Please upload Placement_Master.xlsx"
    )

    st.stop()

# -------------------------------------------------
# KPI CALCULATION
# -------------------------------------------------

total_batch = int(
    df["BatchStrength"].sum()
)

total_eligible = int(
    df["EligibleStudents"].sum()
)

total_offers = int(
    df["Offers"].sum()
)

total_companies = int(
    df["Companies"].sum()
)

highest_salary = float(
    df["HighestSalary"].max()
)

average_salary = round(
    df["AverageSalary"].mean(),2
)

median_salary = round(
    df["MedianSalary"].mean(),2
)

placement_percent = round(
    (total_offers / total_eligible) * 100,
    2
)

# -------------------------------------------------
# KPI CARDS
# -------------------------------------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "👨‍🎓 Eligible Students",
    f"{total_eligible:,}"
)

c2.metric(
    "📜 Total Offers",
    f"{total_offers:,}"
)

c3.metric(
    "🏢 Companies",
    f"{total_companies:,}"
)

c4.metric(
    "📈 Placement %",
    f"{placement_percent}%"
)

c5,c6,c7,c8 = st.columns(4)

c5.metric(
    "🎓 Batch Size",
    f"{total_batch:,}"
)

c6.metric(
    "💰 Avg Salary",
    f"{average_salary} LPA"
)

c7.metric(
    "⭐ Median Salary",
    f"{median_salary} LPA"
)

c8.metric(
    "🏆 Highest Salary",
    f"{highest_salary} LPA"
)

st.divider()

# -------------------------------------------------
# ACHIEVEMENT POPUP
# -------------------------------------------------

placeholder = st.empty()

if total_offers > 0:

    placeholder.success(
        f"🎉 Congratulations! RUAS has achieved {total_offers} placement offers."
    )

    time.sleep(5)

    placeholder.empty()

# -------------------------------------------------
# FILTERS
# -------------------------------------------------

st.sidebar.header("Filters")

faculty_filter = st.sidebar.multiselect(
    "Faculty",
    options=df["Faculty"].unique(),
    default=df["Faculty"].unique()
)

filtered_df = df[
    df["Faculty"].isin(faculty_filter)
]

# -------------------------------------------------
# CHARTS ROW 1
# -------------------------------------------------

col1,col2 = st.columns(2)

with col1:

    fig1 = px.bar(
        filtered_df,
        x="Program",
        y="Offers",
        color="Faculty",
        title="Offers by Program"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )

with col2:

    fig2 = px.pie(
        filtered_df,
        names="Faculty",
        values="Offers",
        hole=0.5,
        title="Faculty Contribution"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

# -------------------------------------------------
# CHARTS ROW 2
# -------------------------------------------------

col3,col4 = st.columns(2)

with col3:

    fig3 = px.bar(
        filtered_df,
        x="Program",
        y="AverageSalary",
        color="Faculty",
        title="Average Salary"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

with col4:

    fig4 = px.bar(
        filtered_df,
        x="Program",
        y="HighestSalary",
        color="Faculty",
        title="Highest Salary"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

# -------------------------------------------------
# FACULTY SUMMARY
# -------------------------------------------------

st.subheader("Faculty-Wise Placement Summary")

faculty_summary = (
    filtered_df
    .groupby("Faculty")
    .agg({
        "BatchStrength":"sum",
        "EligibleStudents":"sum",
        "Offers":"sum",
        "Companies":"sum"
    })
    .reset_index()
)

faculty_summary["PlacementPercent"] = round(
    faculty_summary["Offers"] /
    faculty_summary["EligibleStudents"] * 100,
    2
)

st.dataframe(
    faculty_summary,
    use_container_width=True
)

# -------------------------------------------------
# PROGRAM SUMMARY
# -------------------------------------------------

st.subheader("Program-Wise Statistics")

st.dataframe(
    filtered_df,
    use_container_width=True
)

# -------------------------------------------------
# LIVE ENTRY FORM
# -------------------------------------------------

st.subheader("➕ Add New Placement Data")

with st.form("new_record"):

    faculty = st.text_input("Faculty")

    department = st.text_input("Department")

    program = st.text_input("Program")

    offers = st.number_input(
        "Offers",
        min_value=0
    )

    company = st.number_input(
        "Companies",
        min_value=0
    )

    highest = st.number_input(
        "Highest Salary",
        min_value=0.0
    )

    submit = st.form_submit_button(
        "Submit"
    )

    if submit:

        st.balloons()

        st.success(
            f"""
🎉 Congratulations!

{program}

has reported

{offers} new offers

Highest Package:
₹ {highest} LPA
"""
        )

# -------------------------------------------------
# DOWNLOAD FILTERED DATA
# -------------------------------------------------

csv = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="Download Current Data",
    data=csv,
    file_name="RUAS_Placement_Report.csv",
    mime="text/csv"
)
st.markdown("<br>" * 100, unsafe_allow_html=True)
# -------------------------------------------------
# AUTO SCROLL TOP ↔ BOTTOM
# -------------------------------------------------

components.html(
    """
    <script>
    let direction = 1;

    setInterval(function () {

        const doc = window.parent.document.documentElement;

        const currentPos =
            window.parent.pageYOffset ||
            doc.scrollTop;

        const maxScroll =
            doc.scrollHeight -
            window.parent.innerHeight;

        if (currentPos >= maxScroll - 5) {
            direction = -1;   // start moving up
        }

        if (currentPos <= 5) {
            direction = 1;    // start moving down
        }

        window.parent.scrollBy(
            0,
            4 * direction
        );

    }, 30);
    </script>
    """,
    height=0
)
