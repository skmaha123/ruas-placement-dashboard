import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="MSRUAS Placement Intelligence",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.main{
    background-color:#f6f8fb;
}

.metric-container{
    background:white;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.08);
}

h1,h2,h3{
    color:#003366;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🎓 MSRUAS Placement Intelligence Dashboard")

st.markdown(
"""
AI driven analytics and forecasting platform for placement,
higher studies and progression data.
"""
)

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload Placement Workbook",
    type=["xlsx"]
)

if uploaded_file:

    df = pd.read_excel(
        uploaded_file,
        sheet_name="Master_Placement_Data"
    )

    # --------------------------------------------------
    # CLEAN DATA
    # --------------------------------------------------

    numeric_cols = [
        "Year",
        "Graduated",
        "Placed_or_Offers",
        "Higher_Studies",
        "Entrepreneurship",
        "Placement_Percentage"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df = df.dropna()

    # --------------------------------------------------
    # KPIs
    # --------------------------------------------------

    total_students = int(df["Graduated"].sum())

    total_placements = int(
        df["Placed_or_Offers"].sum()
    )

    avg_placement = round(
        df["Placement_Percentage"].mean(),
        2
    )

    total_higher = int(
        df["Higher_Studies"].sum()
    )

    c1,c2,c3,c4 = st.columns(4)

    c1.metric(
        "Graduates",
        f"{total_students:,}"
    )

    c2.metric(
        "Placements",
        f"{total_placements:,}"
    )

    c3.metric(
        "Average Placement %",
        f"{avg_placement}%"
    )

    c4.metric(
        "Higher Studies",
        f"{total_higher:,}"
    )

    st.divider()

    # --------------------------------------------------
    # FACULTY SELECTION
    # --------------------------------------------------

    faculty = st.selectbox(
        "Select Faculty",
        ["All"] + sorted(
            df["Faculty"].unique()
        )
    )

    if faculty != "All":
        filtered = df[
            df["Faculty"] == faculty
        ]
    else:
        filtered = df.copy()

    # --------------------------------------------------
    # CHART 1
    # --------------------------------------------------

    col1,col2 = st.columns(2)

    with col1:

        fig1 = px.bar(
            filtered,
            x="Faculty",
            y="Placement_Percentage",
            color="Year",
            barmode="group",
            text="Placement_Percentage",
            title="Placement % by Faculty"
        )

        fig1.update_layout(
            height=500
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    # --------------------------------------------------
    # CHART 2
    # --------------------------------------------------

    with col2:

        fig2 = px.line(
            filtered,
            x="Year",
            y="Placement_Percentage",
            color="Faculty",
            markers=True,
            line_shape="spline",
            title="Placement Trend"
        )

        fig2.update_layout(
            height=500
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    # --------------------------------------------------
    # FACULTY COMPARISON
    # --------------------------------------------------

    faculty_perf = (
        df.groupby("Faculty")
        .agg({
            "Placement_Percentage":"mean"
        })
        .reset_index()
        .sort_values(
            "Placement_Percentage",
            ascending=False
        )
    )

    fig3 = px.funnel(
        faculty_perf,
        x="Placement_Percentage",
        y="Faculty",
        title="Faculty Ranking"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.divider()

    # --------------------------------------------------
    # FORECAST MODEL
    # --------------------------------------------------

    st.header("🔮 Placement Forecast")

    encoded = df.copy()

    faculty_map = {
        v:k
        for k,v in enumerate(
            encoded["Faculty"].unique()
        )
    }

    encoded["Faculty_Code"] = (
        encoded["Faculty"]
        .map(faculty_map)
    )

    X = encoded[
        [
            "Year",
            "Graduated",
            "Higher_Studies",
            "Entrepreneurship",
            "Faculty_Code"
        ]
    ]

    y = encoded[
        "Placement_Percentage"
    ]

    model = RandomForestRegressor(
        n_estimators=500,
        random_state=42
    )

    model.fit(X,y)

    left,right = st.columns(2)

    with left:

        forecast_faculty = st.selectbox(
            "Faculty for Prediction",
            sorted(
                df["Faculty"].unique()
            )
        )

        future_year = st.slider(
            "Target Year",
            2027,
            2035,
            2027
        )

    with right:

        graduates = st.number_input(
            "Expected Graduates",
            100,
            5000,
            500
        )

        higher = st.number_input(
            "Expected Higher Studies",
            0,
            1000,
            50
        )

        entrepreneur = st.number_input(
            "Expected Entrepreneurship",
            0,
            500,
            10
        )

    if st.button("Generate Forecast"):

        pred = model.predict(
            [[
                future_year,
                graduates,
                higher,
                entrepreneur,
                faculty_map[
                    forecast_faculty
                ]
            ]]
        )[0]

        pred = max(
            0,
            min(pred,100)
        )

        predicted_placed = round(
            graduates *
            pred / 100
        )

        st.success(
            f"""
Predicted Placement Percentage:
{pred:.2f}%
"""
        )

        st.metric(
            "Predicted Students Placed",
            predicted_placed
        )

        forecast_df = pd.DataFrame({
            "Faculty":[forecast_faculty],
            "Year":[future_year],
            "Graduates":[graduates],
            "Predicted Placement %":[pred],
            "Predicted Placements":[predicted_placed]
        })

        st.dataframe(
            forecast_df,
            use_container_width=True
        )

        csv = forecast_df.to_csv(
            index=False
        )

        st.download_button(
            "Download Forecast",
            csv,
            "forecast.csv",
            "text/csv"
        )

    st.divider()

    # --------------------------------------------------
    # TABLE
    # --------------------------------------------------

    st.header("Data Explorer")

    st.dataframe(
        filtered,
        use_container_width=True
    )